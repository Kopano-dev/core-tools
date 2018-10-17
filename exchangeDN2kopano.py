#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


# UNTESTED!!!!!!

import kopano
from kopano.errors import *
from MAPI.Util import *


def opt_args():
    parser = kopano.parser('skpcuUP')
    parser.add_option("--all", dest="all", action="store_true", help="Run script for all users")
    return parser.parse_args()

def main():
    options, args = opt_args()

    if not options.users and not options.all:
        print('please use\n{} --user <username>\nor\n{} --all'.format(sys.argv[0], sys.argv[0]))
        sys.exit(1)

    global server
    server = kopano.Server(options)
    property_list=[PR_SENT_REPRESENTING_SEARCH_KEY, PR_RECEIVED_BY_ENTRYID, PR_SENT_REPRESENTING_ENTRYID,
                   PR_RCVD_REPRESENTING_ENTRYID, PR_RECEIVED_BY_SEARCH_KEY, PR_RCVD_REPRESENTING_SEARCH_KEY,
                   PR_SENT_REPRESENTING_EMAIL_ADDRESS_W, PR_RECEIVED_BY_EMAIL_ADDRESS_W,
                   PR_RCVD_REPRESENTING_EMAIL_ADDRESS_W, PR_SENDER_ENTRYID, PR_SENDER_SEARCH_KEY,
                   PR_SENDER_EMAIL_ADDRESS_W]

    mapping_dict = {
        'p.halbwachs': 'p.lehensteiner'
    }

    for user in server.users():
        for folder in user.store.folders():
            for item in folder.items():
                for p in property_list:
                    try:
                        prop = item.prop(p)
                    except NotFoundError:
                        continue

                    if 'EXCHANGE' in p.value:
                        username = prop.value.split('CN=')[-1]
                        if mapping_dict.get(username.lower()):
                            username = mapping_dict[username]
                        try:
                            tmp_user = server.user(username.lower())
                        except NotFoundError:
                            print('User "{}" not found in Kopano server skipping property'.format(username))
                            continue

                        if '_ENTRYID' in prop.idname:
                            value = tmp_user.userid
                        elif "_KEY" in prop.idname:
                            value = u'ZARAFA:{}'.format(tmp_user.username)
                        else:
                            value = tmp_user.username

                        item.create_prop(prop.proptag, value)


if __name__ == "__main__":
    main()
