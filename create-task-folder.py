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

    # Create tmp task folder
    # Some store can't create Task so we rename it later
    print  'Create Tmp Tasks  folder'
    taskfolder = user.store.subtree.create_folder('TMP-Tasks')
    taskfolder.container_class = 'IPF.TASK'

    try:
        taskfolder.mapiobj.SetProps([SPropValue(PR_DISPLAY_NAME, 'Tasks')])
        taskfolder.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)
    except MAPI.Struct.MAPIErrorCollision as e:
        print 'Can\'t rename folder to Tasks\n', e
        user.store.root.delete(taskfolder)
        sys.exit(1)

    #promote to task folder
    print 'Promote Tasks folder'
    user.store.root.mapiobj.SetProps([SPropValue(PR_IPM_TASK_ENTRYID, binascii.unhexlify(taskfolder.entryid))])
    user.store.root.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)

    print 'Renaming Folder to Tasks'

if __name__ == "__main__":
    main()