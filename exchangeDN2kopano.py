#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


import kopano
from kopano.errors import *
from MAPI.Util import *
import binascii

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
    parser = kopano.parser('skpcfuUP')
    parser.add_option("--all", dest="all", action="store_true", help="Run script for all users")
    return parser.parse_args()


def get_username(prop):
    mapping_dict = {
        'p.halbwachs': 'p.lehensteiner',

    }
    username = prop.split('CN=')[-1]
    if mapping_dict.get(username.lower()):
        username = mapping_dict[username]
    try:
        tmp_user = server.user(username.lower())
    except NotFoundError:
        return None

    return tmp_user


def change_recipients(item):
    ## Get recipient list
    table = item.mapiobj.OpenProperty(PR_MESSAGE_RECIPIENTS, IID_IMAPITable, MAPI_UNICODE, 0)
    table.SetColumns(RECIP_PROPS, 0)
    rows = table.QueryRows(-1, 0)

    for recp in rows:
        display_name = None
        email = None
        smtp = None
        change = None
        for prop in recp:
            if prop.ulPropTag == 0X3001001F:
                display_name = prop.Value

            if prop.ulPropTag == 0x3002001F and prop.Value == u'EX':
                prop.Value = u'SMTP'
            if prop.ulPropTag == 0x3003001F:
                if  u'EXCHANGE' in prop.Value:
                    tmp_user = get_username(prop.Value)
                    change = True
                    if tmp_user:
                        prop.Value = tmp_user.email
                        email = tmp_user.email
                    elif not tmp_user and display_name:
                        prop.Value = display_name
                        email = display_name
                else:
                    email = prop.Value

            if prop.ulPropTag == 0x300B0102 and change:
                smtp = True
                if email:
                    prop.Value = 'SMTP:{}'.format(email)
                elif display_name:
                    prop.Value = 'SMTP:{}'.format(display_name)

        if not smtp:
            if email:
                recp.append(SPropValue(0x300B0102, 'SMTP:{}'.format(email)))
            elif display_name:
                recp.append(SPropValue(0x300B0102, 'SMTP:{}'.format(display_name)))

        entryid = server.ab.CreateOneOff(display_name, u'SMTP', email, MAPI_UNICODE)
        recp.append(SPropValue(PR_ENTRYID, entryid))

    item.mapiobj.ModifyRecipients(MODRECIP_MODIFY, rows)
    return item

def change_properties(item):

    # Fix  Sender
    try:
        exchange_sender = item.prop(PR_SENDER_SEARCH_KEY).value
        sender_username = get_username(exchange_sender)
        if sender_username:
            item.create_prop(PR_SENDER_SEARCH_KEY, 'ZARAFA:{}\x00'.format(sender_username.name))
            item.create_prop(PR_SENDER_ADDRTYPE_W, u'ZARAFA')
            item.create_prop(PR_SENDER_EMAIL_ADDRESS_W, u'{}'.format(sender_username.fullname))
            item.create_prop(PR_SENDER_NAME_W, u'{}'.format(sender_username.name))
            item.create_prop(PR_SENDER_ENTRYID, binascii.unhexlify(sender_username.userid))
    except NotFoundError:
        pass

    # fix sender name
    try:
        exchange_sent = item.prop(PR_SENT_REPRESENTING_SEARCH_KEY).value
        sent_username = get_username(exchange_sent)
        if sent_username:
            item.create_prop(PR_SENT_REPRESENTING_SEARCH_KEY, 'ZARAFA:{}\x00'.format(sent_username.name))
            item.create_prop(PR_SENT_REPRESENTING_ADDRTYPE_W, u'ZARAFA')
            item.create_prop(PR_SENT_REPRESENTING_NAME_W, u'{}'.format(sent_username.fullname))
            item.create_prop(PR_SENT_REPRESENTING_EMAIL_ADDRESS_W, u'{}'.format(sent_username.name))
            item.create_prop(PR_SENT_REPRESENTING_ENTRYID, binascii.unhexlify(sent_username.userid))
    except NotFoundError:
        pass
    # Fix  Received by
    try:
        exchange_received = item.prop(PR_RECEIVED_BY_SEARCH_KEY).value
        received_username = get_username(exchange_received)
        if received_username:
            item.create_prop(PR_RECEIVED_BY_SEARCH_KEY, 'ZARAFA:{}\x00'.format(received_username.name))
            item.create_prop(PR_RECEIVED_BY_ADDRTYPE_W, u'ZARAFA')
            item.create_prop(PR_RECEIVED_BY_EMAIL_ADDRESS_W, u'{}'.format(received_username.fullname))
            item.create_prop(PR_RECEIVED_BY_NAME_W, u'{}'.format(received_username.name))
            item.create_prop(PR_RECEIVED_BY_ENTRYID, binascii.unhexlify(received_username.userid))
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

    if not options.users and not options.all:
        print('please use\n{} --user <username>\nor\n{} --all'.format(sys.argv[0], sys.argv[0]))
        sys.exit(1)

    global server
    server = kopano.Server(options)

    for user in server.users():
        for folder in user.store.folders():
            for item in folder.items():

                item = change_recipients(item)
                item = change_properties(item)



if __name__ == "__main__":
    main()
