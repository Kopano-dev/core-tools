#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from __future__ import print_function
from __future__ import unicode_literals
import kopano


def opt_args():
    parser = kopano.parser('uskPpf')
    parser.add_option('--entryid', dest='entryid', help='Entryid to resolve')
    parser.add_option('--eml', dest='eml', action='store_true', help='Write as eml to file')
    parser.add_option('--delete', dest='delete', action='store_true', help='Delete the item from the store')
    options, args = parser.parse_args()
    if not options.entryid:
        parser.print_help()
        exit()
    else:
        return options


def main():
    options = opt_args()
    if options.entryid and len(options.entryid) == 96:
        print('Entryid : {}'.format(options.entryid))
        storeid = options.entryid[8:40]
        print('Guessed storeid : {}'.format(storeid))
        try:
            store = kopano.Server(options).store(storeid)
        except Exception as e:
            print('Could not open store : {} Error: {}'.format(storeid, e))
        else:
            print('Store : {}\nUser : {} ({})'.format(store.name, store.user.name, store.user.fullname))
            try:
                item = store.item(options.entryid)
            except Exception as e:
                print('Error {}'.format(e))
            else:
                for show in ['server', 'message_class', 'folder', 'subject', 'received', 'stubbed']:
                    try:
                        print('{} : {}'.format(show.capitalize(), getattr(item, show, 'Not available')))
                    except:
                        pass
                if item.attachments():
                    for attachment in item.attachments():
                        try:
                            data = attachment.data
                        except Exception as e:
                            print('Attachment could not be read {} error {}'.format(attachment.filename, e))
                        else:
                            print('Attachment could be read : {}'.format(attachment.name))

                if options.eml:
                    try:
                        eml = item.eml()
                    except Exception as e:
                        print('Eml dump failed : error : {}'.format(e))
                    else:
                        filename = '.'.join((options.entryid, 'eml'))
                        write = open(filename, 'w')
                        write.write(eml)
                        write.close()
                        print('Eml dump: written to {}'.format(filename))

                if options.delete:
                    try:
                        store.inbox.delete(item)
                    except Exception as e:
                        print('{}'.format(e))
                    else:
                        print('{} was deleted'.format({options.entryid}))


if __name__ == '__main__':
    main()
