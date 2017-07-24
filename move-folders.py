#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


try:
    import kopano
except ImportError:
    import zarafa as kopano
from MAPI.Util import *
import binascii

def opt_args():
    parser = kopano.parser('skpcf')
    parser.add_option("--from_user", dest="from_user", action="store", help="Copy folders over from this user (user everyone for public store)")
    parser.add_option("--to_user", dest="to_user", action="store", help="move folders over to this user (user everyone for public store")
    parser.add_option("--remove", dest="remove", action="store_true", help="Remove folder if it already exist in the other store")
    return parser.parse_args()


def main():
    options, args = opt_args()

    if not options.from_user or not options.to_user:
        print 'Please use %s --from_user <username>  --to_user <username> --folder  <foldername>' % sys.argv[0]
        sys.exit(1)
    server = kopano.Server(options)
    if options.from_user.lower() ==  'everyone':
        from_store = server.public_store
        from_name = 'Public store'
    else:
        from_store = server.user(options.from_user).store
        from_name = from_store.user.name.encode('utf-8')
    if options.to_user.lower() == 'everyone':
        to_store = server.public_store
        to_name = 'Public store'
    else:
        to_store = server.user(options.to_user).store
        to_name = to_store.user.name.encode('utf-8')

    for folder in from_store.folders(options.folders):
        try:
            to_folder = to_store.subtree.create_folder(folder.path)
            print 'Copying folder %s from user  %s to user %s' % (folder.name.encode('utf-8'), from_name, to_name)
            from_store.subtree.copy(folder, to_folder)
        except MAPI.Struct.MAPIErrorCollision:
            if options.remove:
                #create ignore list, so system folders can't be deleted
                ignore = [to_store.inbox.entryid, to_store.calendar.entryid, to_store.contacts.entryid,
                          to_store.drafts.entryid, to_store.junk.entryid, to_store.notes.entryid,
                          to_store.outbox.entryid, to_store.sentmail.entryid, to_store.tasks.entryid,
                          to_store.subtree.entryid, to_store.wastebasket.entryid]
                if to_folder.entryid in ignore:
                    print 'Can not delete system folder'
                    sys.exit(10)
                print 'remove folder tree for', folder.path
                to_store.subtree.delete(to_folder)
                to_folder = to_store.subtree.create_folder(folder.path)
                from_store.subtree.copy(folder, to_folder)
            else:
                print 'Folder name already exist. please remove or use the parameter --remove'

if __name__ == "__main__":
    main()