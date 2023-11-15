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
    parser = kopano.parser('skpcu')
    parser.add_option("-f","--folder", dest="folder", action="store", help="junkfolder")

    return parser.parse_args()


def main():
    options, args = opt_args()

    if not options.users or not options.folder:
        print 'Please use %s -u <username> -f <foldername>' % sys.argv[0]
        sys.exit(1)
    server = kopano.Server(options)
    for user in server.users(parse=True):
        for folder in user.folders():

            if options.folder == folder.name:
                print 'Set %s to system Junk folder' % folder.name
                junkentry = folder.entryid
                junk_prop = user.store.root.prop(PR_ADDITIONAL_REN_ENTRYIDS).value
                junk_prop[4] = binascii.unhexlify(junkentry)
                user.store.root.mapiobj.SetProps([SPropValue(PR_ADDITIONAL_REN_ENTRYIDS, junk_prop)])
                user.store.root.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)


if __name__ == "__main__":
    main()