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

def create_recipient(name, email, addrtype, last_used=datetime.datetime.now()):
    return {
        "display_name": name,
        "smtp_address": email,
        "email_address": email,
        "address_type": addrtype,
        "object_type": 6,
        "last_used": last_used.strftime('%s'),
        "count": 1
    }

def main():
    options, _ = opt_args()

    user = kopano.Server(options).user(options.user)
    history = user.store.prop(PR_EC_RECIPIENT_HISTORY_JSON)
    history_json = json.loads(history.value)
    if options.sent:
        num = 0
        today = datetime.datetime.now()
        for item in user.store.sentmail:
            for recipient in item.to:
                email = recipient.email
                name = recipient.name
                addresstype = recipient.addrtype
                if email not in str(history_json['recipients']):
                    if options.days:
                        until = today + datetime.timedelta(days=int(options.days))
                        messagedate = item.prop(PR_MESSAGE_DELIVERY_TIME).value
                        if messagedate > until:
                            continue

                    recip = create_recipient(name, email, addresstype, item.received)
                    history_json['recipients'].append(recip)
                num += 1
                if options.total and num == int(options.total):
                    break
    else:
        for contact in user.store.contacts:
            try:
                email = contact.prop('address:32896').value
                if str(email) not in str(history_json['recipients']):
                    name = contact.prop('address:32773').value,
                    recip = create_recipient(name, email, "SMTP")
                    history_json['recipients'].append(recip)
            except kopano.NotFoundError:
                continue


    history.value = json.dumps(history_json).encode('utf-8')

if __name__ == "__main__":
    main()
