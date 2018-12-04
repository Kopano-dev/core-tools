#!/usr/bin/env python

import kopano
import sys
import binascii
from MAPI.Tags import *
from datetime import datetime
from kopano.errors import *


def opt_args():
    parser = kopano.parser('skpcmUPuf')
    parser.add_option("--storeid", dest="storeid", action="store", help="Store ID")
    parser.add_option("--subject", dest="subject", action="store", help="subject")
    parser.add_option("--from", dest="fromaddress", action="store", help="from address")
    parser.add_option("--until", dest="until", action="store", help="Only search for mails younger then yyyy-mm-dd")
    parser.add_option("--delete", dest="delete", action="store_true", help="Delete item")
    parser.add_option("--stop-after-first-hit", dest="stop", action="store_true", help="Stop search after first hit")
    return parser.parse_args()


def main():
    options, args = opt_args()
    server = kopano.Server(options)
    for user in server.users():
        found_items = []
        global_break = None
        print('running for user {}'.format(user.name))
        for folder in user.folders():
            if global_break:
                break
            for item in folder.items():
                if options.until:
                    submit_time = item.prop(PR_CREATION_TIME).value
                    check = datetime.strptime('{} 00:00:00'.format(options.until), '%Y-%m-%d 00:00:00')
                    if submit_time < check:
                        break

                if (options.subject or options.subject == '') and options.subject.lower() == item.subject.lower():
                    if options.fromaddress:
                        if options.fromaddress == item.sender.email:
                            found_items.append(item)
                            if options.stop:
                                global_break = True
                                break
                    else:
                        found_items.append(item)
                        if options.stop:
                            global_break = True
                            break

                elif (options.fromaddress and (not options.subject and options.subject != '' )) and options.fromaddress == item.sender.email:
                    found_items.append(item)
                    if options.stop:
                        global_break = True
                        break


        if len(found_items) > 0:
            for item in found_items:
                if options.delete:
                    print('removing item {}'.format(item.subject))
                    user.store.delete(item)
                else:
                    print('{} -> {}'.format(item.folder.name, item.subject))





if __name__ == "__main__":
    main()
