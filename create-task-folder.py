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
    parser.add_option("--user", dest="user", action="store", help="Username")


    return parser.parse_args()

def main():
    options, args = opt_args()

    if not options.user:
        print 'Please use: %s --user <username>' % sys.argv[0]
        sys.exit(1)
    user = kopano.Server().user(options.user)

    #create task folder
    print 'Create Tasks folder'
    taskfolder = user.store.subtree.create_folder('Tasks')

    #promote to task folder
    print 'Promote Tasks folder to systemfolder'
    user.store.root.mapiobj.SetProps([SPropValue(PR_IPM_TASK_ENTRYID, binascii.unhexlify(taskfolder.entryid))])
    user.store.root.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)

    print 'Done?'
if __name__ == "__main__":
    main()