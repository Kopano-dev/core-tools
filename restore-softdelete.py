#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#

import kopano
from MAPI.Util import *
from datetime import  datetime
import sys
from kopano import Property
import time

def opt_args():
    parser = kopano.parser('skpcfUP')
    parser.add_option("--user", dest="user", action="store", help="run for user x")
    parser.add_option("--daysbefore", dest="daysbefore", action="store", help="Delete older then x days (DD-MM-YYYY)")
    parser.add_option("--daysafter", dest="daysafter", action="store", help="Delete older then x days (DD-MM-YYYY)")
    parser.add_option("--newfolder", dest="newfolder", action="store", help="save restored items in new folder")
    parser.add_option("--public", dest="public", action="store_true", help="Restore soft-delete items in public folder")
    parser.add_option("--archive", dest="archive", action="store_true", help="Restore soft-delete items in archive folder")
    parser.add_option("--verbose", dest="verbose", action="store_true", help="verbose mode")

    return parser.parse_args()

def main():
    options, args = opt_args()

    if not options.user and not options.public:
        print('Please use {} --user <username> '.format(sys.argv[0]))
        sys.exit(1)
    if not options.daysbefore and not options.daysafter:
        print('Restoring all messages')

    if options.public:
        user = kopano.Server(options).public_store
    else:
        user = kopano.Server(options).user(options.user)

    if options.archive:
        store = user.archive_store
    elif options.public:
        store = user
    else:
        store = user.store

    if options.verbose:
        print('\nRunning script for {}'.format(user.name))
    itemcount = 0

    for folder in store.folders(parse=True):

        if options.newfolder:
            newfolder = user.store.folder(options.newfolder)
        else:
            newfolder = folder

        deleted_folder = folder.deleted
        for item in deleted_folder:
            restore = False
            if options.daysafter and options.daysbefore:
                daysafter = MAPI.Time.unixtime(
                    time.mktime(datetime.strptime(options.daysafter, '%d-%m-%Y').timetuple()))
                daysbefore = MAPI.Time.unixtime(
                    time.mktime(datetime.strptime(options.daysbefore, '%d-%m-%Y').timetuple()))
                if item.last_modified <= daysbefore and item.last_modified >= daysafter:
                    restore = True
            else:
                restore = True

            if restore:
                deleted_folder.move(item, newfolder)
                if options.verbose:
                    try:
                        print("item '{}' is restored in folder '{}'".format(item.subject, newfolder))
                    except MAPIErrorNotFound:
                        pass 
                    itemcount += 1

    if options.verbose:
        print('{} items where restored'.format(itemcount))


if __name__ == '__main__':
    main()