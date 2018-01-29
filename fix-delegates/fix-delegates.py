#!/usr/bin/env python

import kopano
import sys
import binascii


def opt_args():
    parser = kopano.parser('skpcf')
    parser.add_option("--user", dest="user", action="store", help="username")
    parser.add_option("--modify", dest="modify", action="store_true", help="Run script and save the changes ")
    parser.add_option("--restore", dest="restore", action="store_true", help="Restore changes this script made ")
    parser.add_option("--verbose", dest="verbose", action="store_true", help="verbose mode ")
    return parser.parse_args()


def getprop(item, myprop):
    try:
        return item.prop(myprop).value
    except:
        return None


def main():
    options, args = opt_args()
    if not options.user:
        sys.exit('Please use:\n %s -u <username>' % (sys.argv[0]))

    user = kopano.Server(options).user(options.user)


# restore
    if options.restore:
        restoreids = []
        with open('%s-backup.delagates' % user.name) as lines:
            restore = lines.readlines()
            for line in restore:
                line = line.strip()
                restoreids.extend([binascii.unhexlify(line)])
        user.store.root.prop(0x36E41102).set_value(restoreids)
        if options.verbose:
            sys.exit('Restore done\n %s' % restoreids)
        else:
            sys.exit('Restore done\n')


# modify
    freebusy_folder = user.store.root.folder('Freebusy Data')
    freebusy_folder_recordkey = getprop(freebusy_folder, 0x0FF90102)
    for item in freebusy_folder.items():
        if item.subject == 'LocalFreebusy':
            freebusy_item_recordkey = getprop(item, 0x0FF90102)
    freebusy_entryids = user.store.root.prop(0x36E41102).value
    if options.modify:
        f = open('%s-backup.delagates' % user.name, 'w')
        for ids in freebusy_entryids:
            ids = binascii.hexlify(ids)
            f.write("%s\n" % ids)
        f.close()
    newid = []
    freebusy_start = freebusy_entryids[0]
    newid.extend([freebusy_start, freebusy_item_recordkey, '', freebusy_folder_recordkey])
    if options.verbose:
        print 'Old ids are \n %s \n' % freebusy_entryids
        print 'New ids are: \n %s' % newid
    if options.modify:
        print 'The new ids are saved for user %s' % user.name
        user.store.root.prop(0x36E41102).set_value(newid)

if __name__ == "__main__":
    main()