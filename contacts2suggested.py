#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


try:
    import kopano
except ImportError:
    import zarafa as kopano
from MAPI.Util import *
import json
import datetime


def opt_args():
    parser = kopano.parser('skpcf')
    parser.add_option("--user", dest="user", action="store", help="Run script for user ")
    parser.add_option("--sent", dest="sent", action="store_true", help="import user from sent items")
    parser.add_option("--total", dest="total", action="store", help="amount of contacts")
    parser.add_option("--days", dest="days", action="store", help="import user from sent items")

    return parser.parse_args()

def searchemail(displayname):
    for word in displayname.split():
        if '@' in word:
            return word

    return False


def main():
    options, args = opt_args()

    user = kopano.Server(options).user(options.user)
    history = user.store.prop(0X6773001F).value
    history = json.loads(history)
    if options.sent:
        num = 0
        today = datetime.datetime.now()
        for item in user.store.sentmail:
            emails = item.prop(PR_DISPLAY_TO_W).value.split(';')
            names = item.prop(PR_DISPLAY_TO_W).value.split(';')
            add =0
            for address in emails:

                email = searchemail(address)
                if email:
                    email = email.replace('<', '').replace('>', '').replace('(', '').replace(')', '').replace("'", '').replace('"', '')
                    if email not in str(history['recipients']):
                        if options.days:
                            until = today + datetime.timedelta(days=int(options.days))
                            messagedate = item.prop(PR_MESSAGE_DELIVERY_TIME).value
                            if messagedate > until:
                                continue

                        if len(item.prop(PR_DISPLAY_TO_W).value) > 0:
                            addresstype = 'ZARAFA'
                        else:
                            addresstype= 'SMTP'

                        history['recipients'].append({"display_name": names[add].lstrip().replace("'", ''),
                                                      "smtp_address": email.lstrip(),
                                                      "email_address": email.lstrip(), "address_type": addresstype, "count": 1,
                                                      "object_type": 6})

                num += 1
                add += 1
                if options.total and num == int(options.total):
                    break
    else:
        for contact in user.store.contacts:
            try:
                email = contact.prop(0X8133001F).value
                if str(email) not in str(history['recipients']):
                    history['recipients'].append({"display_name": contact.prop(0X8130001F).value,
                                                  "smtp_address": "",
                                                  "email_address": email, "address_type": "ZARAFA", "count": 1,
                                                  "object_type": 6})
            except MAPIErrorNotFound:
                continue


    user.store.mapiobj.SetProps([SPropValue(0X6773001F, u'%s' % json.dumps(history))])
    user.store.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)

if __name__ == "__main__":
    main()
