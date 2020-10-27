#!/usr/bin/env python

from MAPI import *
from MAPI.Util import *
import kopano


def opt_args():
    parser = kopano.parser("SskpcufUP")
    parser.add_option("--move", dest="move", action="store_true", help="attempt to move broken ipm_subtree in 'Kopano Restored Folders'")
    parser.add_option("--archive", dest="archive", action="store_true", help="Run script for archive stores")
    parser.add_option("--dry-run", dest="dryrun", action="store_true", help="run the script without executing any actions")
    return parser.parse_args()

def main():
    options, args = opt_args()

    restorefoldername = "Kopano Restored Folders"

    ipmsubtree = {}  # Always correct values, as we look for the IPM_SUBTREE.
    entryidstore = {}  # IPM_SUBTREE_ENTRYID values on user.store, could be incorrect.

    for user in kopano.Server(options).users(parse=True):
        restoredfolders = False
        if options.archive:
            store = user.archive_store
        else:
            store = user.store

        if not store:
            print('User %s has no store' % user.name)
            continue
        print("Processing user: %s" % user.name)
        try:
            entryidstore[user.name] = store.mapiobj.GetProps([PR_IPM_SUBTREE_ENTRYID], 0)[0].Value.encode("hex").upper()
        except:
            continue

        for folder in store.root.folders():
            if folder.name == "IPM_SUBTREE":
                if user.name not in ipmsubtree.keys():
                    ipmsubtree[user.name] = folder.entryid

        if entryidstore[user.name] != ipmsubtree[user.name]:
            if options.dryrun:
                print("!! Script running in dry-run mode, nothing will be modified.")
            print("- Incorrect IPM_SUBTREE is set: '%s'" % entryidstore[user.name])
            print("* Updating IPM_SUBTREE_ENTRYID to: '%s'" % ipmsubtree[user.name])
            if ipmsubtree[user.name]:
                if not options.dryrun:
                    store.mapiobj.SetProps([SPropValue(PR_IPM_SUBTREE_ENTRYID, ipmsubtree[user.name].decode("hex"))])
            if ipmsubtree[user.name] and entryidstore[user.name] and options.move:
                srcfld = store.folder(entryidstore[user.name])
                dstfld = store.folder(ipmsubtree[user.name])
                print("* Copying source folder '%s' to '%s'" % (srcfld.name, dstfld.name))
                if not options.dryrun:
                    try:
                        if store.folder(restorefoldername):
                            resfolder = store.folder(restorefoldername)
                            restoredfolders = True
                    except kopano.NotFoundException:
                            restorefolder = dstfld.create_folder(restorefoldername)
                            resfolder = store.folder(restorefolder.entryid)
                            restoredfolders = True

                    if restoredfolders:
                        if resfolder:
                            srcfld.move(srcfld, resfolder)
                        else:
                            print("- Unable to move '%s' into '%s'" % (srcfld.name, dstfld.name))

            elif not ipmsubtree[user.name]:
                print("- No IPM_SUBTREE present, does the user have a store?")

if __name__ == "__main__":
    main()
