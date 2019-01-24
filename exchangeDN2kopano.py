#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


import kopano
from kopano.errors import *
from MAPI.Util import *
import binascii
import json
from email import message_from_string
import re



RECIP_PROPS = [
    PR_ENTRYID,
    PR_DISPLAY_NAME_W,
    PR_EMAIL_ADDRESS_W,
    PR_RECIPIENT_ENTRYID,
    PR_RECIPIENT_TYPE,
    PR_SEND_INTERNET_ENCODING,
    PR_SEND_RICH_INFO,
    PR_RECIPIENT_DISPLAY_NAME, # XXX _W?
    PR_ADDRTYPE_W,
    PR_DISPLAY_TYPE,
    PR_RECIPIENT_TRACKSTATUS,
    PR_RECIPIENT_TRACKSTATUS_TIME,
    PR_RECIPIENT_FLAGS,
    PR_ROWID,
    PR_OBJECT_TYPE,
    PR_SEARCH_KEY,
]

def opt_args():
    parser = kopano.parser('skpcfuUPv')
    parser.add_option("--all", dest="all", action="store_true", help="Run script for all users")
    parser.add_option("--mapping-file", dest="mapping_file", action="store", help="Mapping file for legacyExchangeDN\n "
                                                                                  "(Get-ADUser -SearchBase “DC=DOMAIM,DC=COM” -Filter * -Properties SamAccountName,legacyExchangeDN,mail | Select-Object SamAccountName,legacyExchangeDN,mail| ConvertTo-Json")

    return parser.parse_args()


def get_username(prop):
    email = None
    username =  None
    if isinstance(prop, bytes):
        prop = prop.decode('utf-8')
    prop = prop.lower().replace('ex:','').replace("\x00",'')
    #legacyExchangeDN is known in the mapping file
    if mapping_dict.get(prop):
        if mapping_dict[prop].get('accountname'):
            username = mapping_dict[prop]['accountname']
        if mapping_dict[prop].get('mail'):
            email = mapping_dict[prop]['mail']

    # Do a guess for the username based on the last value in the legacyExchangeDN name.
    else:
        if isinstance(prop, bytes):
            split_this = b'CN='
        else:
            split_this = 'CN='
        username = prop.split(split_this)[-1].lower()

    ## check if user exist in Kopano
    try:
        tmp_user = server.user(username)
        print('found user {}'.format(tmp_user))
        return tmp_user
    except NotFoundError:
        # if user not found but there was an email address in the mapping file just use that then.
        if email:
            print('found email {}'.format(email))
            return email
        return None


def change_recipients(item):
    # Get transport headers in case we can't solve the user  on the server
    addresses = []
    try:
        transport_headers = message_from_string(item.prop(PR_TRANSPORT_MESSAGE_HEADERS_W).value)
        if transport_headers['From']:
            addresses.append(transport_headers['From'])
        if transport_headers['CC']:
            addresses.append(transport_headers['CC'])
        if transport_headers['To']:
            addresses.append(transport_headers['To'])
        if transport_headers['BCC']:
            addresses.append(transport_headers['BCC'])
    except NotFoundError:
        pass

    ## Get recipient list
    table = item.mapiobj.OpenProperty(PR_MESSAGE_RECIPIENTS, IID_IMAPITable, MAPI_UNICODE, 0)
    table.SetColumns(RECIP_PROPS, 0)
    rows = table.QueryRows(-1, 0)
    num = 0
    for recp in rows:

        display_name = None
        email = None
        smtp = None
        change = None
        for prop in recp:
            if prop.ulPropTag == PR_DISPLAY_NAME_W:
                display_name = prop.Value

            if prop.ulPropTag == PR_ADDRTYPE_W and prop.Value == u'EX':
                prop.Value = 'SMTP'
            if prop.ulPropTag == PR_EMAIL_ADDRESS_W:

                if u'EXCHANGE' in prop.Value:
                    tmp_user = get_username(prop.Value)
                    change = True
                    # We found a kopano user
                    if tmp_user and not isinstance(tmp_user, str):
                        prop.Value = tmp_user.email
                        email = tmp_user.email

                    # There is no kopano user but in the mapping file we did have a email address.
                    elif tmp_user and isinstance(tmp_user, str):
                        prop.Value = tmp_user
                        email = tmp_user

                    # No kopano user found checking if display name is a email address
                    elif not tmp_user and display_name:
                        if '@' in display_name:
                            prop.Value = display_name
                            email = display_name
                        else:
                            matching = [s for s in addresses if display_name in s]
                            try:
                                email = (re.findall(r'[\w\.-]+@[\w\.-]+', matching[0].split(display_name, 1)[-1])[-1])
                            except IndexError:
                                email = None
                            if not email:
                                if caching.get(display_name):
                                    email = caching[display_name]
                            if email:
                                caching.update({display_name: email})
                                prop.Value = email

                            else:
                                prop.Value = 'invalid@invalid'
                                email = 'invalid@invalid'
                                print('No email address found for {}'.format(display_name))


                else:
                    email = prop.Value

            if prop.ulPropTag == PR_SEARCH_KEY and change:
                smtp = True
                if email:
                    prop.Value = str.encode('SMTP:{}'.format(email))
                elif display_name:
                    prop.Value = str.encode('SMTP:{}'.format(display_name))

        if not smtp:
            if email:
                recp.append(SPropValue(PR_SEARCH_KEY, str.encode('SMTP:{}'.format(email))))
            elif display_name:
                recp.append(SPropValue(PR_SEARCH_KEY, str.encode('SMTP:{}'.format(display_name))))
        num +=1
        # Creating entryid as that is missing and is causing the display issue's
        try:
            entryid = server.ab.CreateOneOff(display_name, 'SMTP', email, MAPI_UNICODE)
            recp.append(SPropValue(PR_ENTRYID, entryid))
        except MAPIErrorInvalidParameter:
            print('Error while creating entryid: {}, {}'.format(display_name, email))

            continue

    item.mapiobj.ModifyRecipients(MODRECIP_MODIFY, rows)
    item.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)
    return item

def change_properties(item):
    # Get transport headers in case we can't solve the user  on the server
    try:
        transport_headers = message_from_string(item.prop(PR_TRANSPORT_MESSAGE_HEADERS_W).value)
    except NotFoundError:
        transport_headers = None
        pass

    # Fix Sender
    try:
        if item.prop(PR_SENDER_ADDRTYPE_W).value == 'EX':
            exchange_sender = item.prop(PR_SENDER_SEARCH_KEY).value
            sender_username = get_username(exchange_sender)
            if sender_username:
                if not isinstance(sender_username, str):
                    sender_search_key = str.encode('ZARAFA:{}'.format(sender_username.name))
                    sender_adresstype= u'ZARAFA'
                    sender_email = u'{}'.format(sender_username.fullname)
                    sender_name = u'{}'.format(sender_username.name)
                    sender_entryid = binascii.unhexlify(sender_username.userid)
                else:
                    sender_search_key = str.encode('SMTP:{}'.format(sender_username))
                    sender_adresstype = u'SMTP'
                    sender_email = u'{}'.format(sender_username)
                    sender_name = u'{}'.format(sender_username)
                    sender_entryid = None
            elif transport_headers:
                email =re.findall(r'[\w\.-]+@[\w\.-]+',transport_headers['From'])[-1]
                sender_search_key = str.encode('SMTP:{}'.format(email))
                sender_adresstype = u'SMTP'
                sender_email = u'{}'.format(email)
                sender_name = u'{}'.format(email)
                sender_entryid = None

            if transport_headers or sender_username:
                item.create_prop(PR_SENDER_SEARCH_KEY, sender_search_key)
                item.create_prop(PR_SENDER_ADDRTYPE_W, sender_adresstype)
                item.create_prop(PR_SENDER_EMAIL_ADDRESS_W,sender_email)
                item.create_prop(PR_SENDER_NAME_W, sender_name)
                if sender_entryid:
                    item.create_prop(PR_SENDER_ENTRYID, sender_entryid)
                else:
                    item.delete(item.prop(PR_SENDER_ENTRYID))

    except NotFoundError:
        pass

    # fix sender name
    try:
        if item.prop(PR_SENT_REPRESENTING_ADDRTYPE_W).value == 'EX':
            exchange_sent = item.prop(PR_SENT_REPRESENTING_SEARCH_KEY).value
            sent_username = get_username(exchange_sent)
            if sent_username:
                if not isinstance(sent_username, str):
                    sent_search_key = str.encode('ZARAFA:{}'.format(sent_username.name))
                    sent_adresstype = u'ZARAFA'
                    sent_email = u'{}'.format(sent_username.fullname)
                    sent_name = u'{}'.format(sent_username.name)
                    sent_entryid = binascii.unhexlify(sent_username.userid)
                else:
                    sent_search_key = str.encode('SMTP:{}'.format(sent_username))
                    sent_adresstype = u'SMTP'
                    sent_email = u'{}'.format(sent_username)
                    sent_name = u'{}'.format(sent_username)
                    sent_entryid = None
            elif transport_headers:
                email = re.findall(r'[\w\.-]+@[\w\.-]+', transport_headers['From'])[-1]
                sent_search_key = str.encode('SMTP:{}'.format(email))
                sent_adresstype = u'SMTP'
                sent_email = u'{}'.format(email)
                sent_name = u'{}'.format(email)
                sent_entryid = None
            if transport_headers or sent_username:
                item.create_prop(PR_SENT_REPRESENTING_SEARCH_KEY, sent_search_key)
                item.create_prop(PR_SENT_REPRESENTING_ADDRTYPE_W, sent_adresstype)
                item.create_prop(PR_SENT_REPRESENTING_NAME_W, sent_email)
                item.create_prop(PR_SENT_REPRESENTING_EMAIL_ADDRESS_W, sent_name)
                if sent_entryid:
                    item.create_prop(PR_SENT_REPRESENTING_ENTRYID,sent_entryid)
                else:
                    item.delete(item.prop(PR_SENT_REPRESENTING_ENTRYID))
    except NotFoundError:
        pass

    # Fix Received by
    try:
        if item.prop(PR_RECEIVED_BY_ADDRTYPE_W).value == 'EX':
            exchange_received = item.prop(PR_RECEIVED_BY_SEARCH_KEY).value
            received_username = get_username(exchange_received)
            if received_username:
                if not isinstance(received_username, str):
                    received_search_key =  str.encode('ZARAFA:{}'.format(received_username.name))
                    received_adresstype = u'ZARAFA'
                    received_email = u'{}'.format(received_username.fullname)
                    received_name = u'{}'.format(received_username.name)
                    received_entryid = binascii.unhexlify(received_username.userid)
                else:
                    received_search_key =  str.encode('SMTP:{}'.format(received_username))
                    received_adresstype = u'SMTP'
                    received_email = u'{}'.format(received_username)
                    received_name = u'{}'.format(received_username)
                    received_entryid = None
            elif transport_headers:
                email = re.findall(r'[\w\.-]+@[\w\.-]+', transport_headers['To'])[-1]
                received_search_key = str.encode('SMTP:{}'.format(email))
                received_adresstype = u'SMTP'
                received_email = u'{}'.format(email)
                received_name = u'{}'.format(email)
                received_entryid = None
            if transport_headers or received_username:
                item.create_prop(PR_RECEIVED_BY_SEARCH_KEY, received_search_key)
                item.create_prop(PR_RECEIVED_BY_ADDRTYPE_W, received_adresstype)
                item.create_prop(PR_RECEIVED_BY_EMAIL_ADDRESS_W, received_email)
                item.create_prop(PR_RECEIVED_BY_NAME_W, received_name)
                if received_entryid:
                    item.create_prop(PR_RECEIVED_BY_ENTRYID, received_entryid)
                else:
                    item.delete(item.prop(PR_RECEIVED_BY_ENTRYID))

    except NotFoundError:
        pass

    # Remove representing received address as we do not know if this is needed anymore for this item
    try:
        exchange_rep = item.prop(PR_RCVD_REPRESENTING_SEARCH_KEY).value
        rep_username = get_username(exchange_rep)
        if rep_username:
            item.delete(item.prop(PR_RCVD_REPRESENTING_SEARCH_KEY))
            item.delete(item.prop(PR_RCVD_REPRESENTING_ADDRTYPE_W))
            item.delete(item.prop(PR_RCVD_REPRESENTING_EMAIL_ADDRESS_W))
            item.delete(item.prop(PR_RCVD_REPRESENTING_ENTRYID))
            item.delete(item.prop(PR_RCVD_REPRESENTING_NAME_W))

    except NotFoundError:
        pass

    return item


def main():
    options, args = opt_args()
    global server, mapping_dict, caching
    mapping_dict = {}
    caching = {}
    if not options.users and not options.all:
        print('please use\n{} --user <username>\nor\n{} --all'.format(sys.argv[0], sys.argv[0]))
        sys.exit(1)

    if options.mapping_file:
        with open(options.mapping_file) as f:
            mapping_file = json.load(f)
        for entry in mapping_file:
            if entry['legacyExchangeDN']:
                mapping_dict.update({
                    entry['legacyExchangeDN'].lower(): {
                        "accountname":  entry['SamAccountName'],
                        "mail": entry['mail']
                }})
        if options.verbose:
            print(json.dumps(mapping_dict, indent=4))
    else:
        print('No mapping file.\n'
              'We can\'t guarantee that every account can\'t be converted')

    server = kopano.Server(options)

    for user in server.users():
        for folder in user.store.folders():
            for item in folder.items():
                item = change_recipients(item)
                item = change_properties(item)

if __name__ == "__main__":
    main()
