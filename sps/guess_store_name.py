#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


import kopano
from MAPI.Util import PR_RECEIVED_BY_EMAIL_ADDRESS_W


def opt_args():
    parser = kopano.parser('skpcfuUPvS')

    return parser.parse_args()

def get_user(folder):
    check = 0
    emails = []
    for item in folder.items():
        email = item.prop(PR_RECEIVED_BY_EMAIL_ADDRESS_W).value
        if email not in emails:
            emails.append(item.prop(PR_RECEIVED_BY_EMAIL_ADDRESS_W).value)

        check += 1 

        if check == 5:
            break
    return ', '.join(emails)
  


def main():
    options, args = opt_args()

    for store in kopano.Server(options).stores():
        user = store.user
        if not user:
            print(store.outbox.count)
            if store.inbox.count > 0:
                user =get_user(store.inbox)
            elif  store.outbox.count > 0:
                user =get_user(store.outbox)
            else: 
                user = "None"
        else: 
            user = user.name
        print("{} - {}".format(store.entryid, user))

if __name__ == "__main__":
    main()
