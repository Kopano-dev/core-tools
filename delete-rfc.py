#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#

import kopano
from MAPI.Util import *
import sys
from kopano.errors import NotFoundError, MAPIErrorNotFound

def opt_args():
    parser = kopano.parser('skpc')
    parser.add_option("--user", dest="user", action="store", help="Run script for user x")
    return parser.parse_args()

def main():
    options, args = opt_args()

    if not options.user:
        print 'please user %s --user <username>' % sys.argv[0]

    user = kopano.Server().user(options.user)
    count = 0
    for folder in user.store.folders():
        print folder
        for item in folder.items():
            try:
                if item.prop(PR_EC_IMAP_EMAIL).value:
                    item.delete(item.prop(PR_EC_IMAP_EMAIL))
                    count += 1
            except (MAPIErrorNotFound, NotFoundError):
                continue

    print 'removed %s items' % count


if __name__ == "__main__":
    main()
