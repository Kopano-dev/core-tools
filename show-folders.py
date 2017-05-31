#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


try:
    import kopano
except ImportError:
    import zarafa as kopano
from MAPI.Util import *

def opt_args():
    parser = kopano.parser('skpcf')
    parser.add_option("--user", dest="user", action="store", help="Username")
    parser.add_option("--public", dest="public", action="store_true", help="Show public folders")
    parser.add_option("--delete", dest="delete", action="store", help="Delete folder based on entryid")

    return parser.parse_args()

def main():
    options, args = opt_args()

    if not  options.user and not options.public:
        print 'Please use\n' \
              '%s --user <username>  or\n' \
              '%s --public' % (sys.argv[0], sys.argv[0])
        sys.exit(1)
    if options.user:
        user = kopano.Server(options).user(options.user)
        store = user.store
        name = user.name
    if options.public:
        name = 'Public'
        store = kopano.Server(options).public_store
    if not options.delete:
        print 'Store:', name.encode('utf-8')
        print '{:50} {:50} {:50}'.format('Folder name', 'Parent folder', 'Entryid')
        for folder in store.root.folders():
            print '{:50} {:50} {:50}'.format(folder.name.encode('utf8'), folder.parent.name.encode('utf8'), folder.entryid)
    else:
        print 'Not in yet'


if __name__ == "__main__":
    main()