#!/usr/bin/env python3

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
        if not user.store:
            continue
        found_items = []
        global_break = None
        print('running for user {}'.format(user.name))
        blacklist = [user.contacts.name, user.calendar.name, user.tasks.name, user.notes.name]
        for folder in user.store.folders():
            if folder.name in blacklist:
                continue

            if global_break:
                break
            for item in folder.items():
                if options.until:
                    submit_time = item.prop(PR_LAST_MODIFICATION_TIME).value
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
                    try:
                        print('removing item {}'.format(item.subject))
                    except UnicodeEncodeError:
                        print('removing item {}'.format(item.subject.encode('utf-8')))
                    user.store.delete(item)
                else:
                    try:
                        print(
                            '{} -> {} -> {}'.format(item.folder.name, item.subject,
                                                    item.prop(PR_LAST_MODIFICATION_TIME).value))
                    except UnicodeEncodeError:
                        print('{} -> {} -> {}'.format(item.folder.name.encode('utf-8'),
                                                      item.subject.encode('utf-8'),
                                                      item.prop(PR_LAST_MODIFICATION_TIME).value))





if __name__ == "__main__":
    main()
