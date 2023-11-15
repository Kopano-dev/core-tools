#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.6.2'

import kopano
from MAPI.Util import *
from datetime import timedelta, datetime
import sys
import binascii


def opt_args():
    parser = kopano.parser('skpcuf')
    parser.add_option("-d", "--days", dest="days", action="store", help="Delete older then x days")
    parser.add_option("--delete-without-date", dest="dwd", action="store_true", help="Remove only the items that haven't got a date")
    parser.add_option("-F", "--force", dest="force", action="store_true",
                      help="Force deletion if delivery date is not known ")
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="verbose mode")
    parser.add_option("-P", "--progressbar", dest="progressbar", action="store_true", help="Show progressbar")
    parser.add_option("-V", "--version", dest="version", action="store_true", help="Show version number")

    return parser.parse_args()


def progressbar(folders, daysbeforedeleted):
    try:
        from progressbar import Bar, AdaptiveETA, Percentage, ProgressBar
    except ImportError:
        print '''Please download the progressbar library from https://github.com/niltonvolpato/python-progressbar or
        run without the --progressbar parameter'''
        sys.exit(1)
    widgets = [Percentage(),
               ' ', Bar(),
               ' ', AdaptiveETA()]
    progressmax = 0
    for folder in folders:
        table = folder.mapiobj.GetContentsTable(SHOW_SOFT_DELETES)
        table.SetColumns([PR_LAST_MODIFICATION_TIME], 0)
        rows = table.QueryRows(-1, 0)
        if len(rows) > 0:
            for row in rows:
                date = datetime.fromtimestamp(row[0].Value.unixtime)
                if date <= daysbeforedeleted:
                    progressmax += 1
    pbar = ProgressBar(widgets=widgets, maxval=progressmax)
    pbar.start()
    return pbar


def main():
    options, args = opt_args()
    if options.version:
        print 'Version', __version__
    if not options.days:
        print 'Please use %s --days <days>' % sys.argv[0]
        sys.exit(1)

    pbar = None
    daysbeforedeleted = datetime.now() - timedelta(days=int(options.days))

    for user in kopano.Server(options).users(remote=True):
        if options.progressbar:
            pbar = progressbar(user.store.folders(parse=True), daysbeforedeleted)
        if options.verbose:
            print '\nRunning script for', user.name
        itemcount = 0
        for folder in user.store.folders(parse=True):
            retry = []
            table = folder.mapiobj.GetContentsTable(SHOW_SOFT_DELETES)
            table.SetColumns([PR_ENTRYID, PR_SUBJECT, PR_LAST_MODIFICATION_TIME,PR_MESSAGE_DELIVERY_TIME], 0)
            rows = table.QueryRows(-1, 0)
            if len(rows) > 0:
                for row in rows:
                    entryid = row[0].Value
                    try:
                        date = datetime.fromtimestamp(row[2].Value.unixtime)
                    except AttributeError as e:
                        if options.force:
                            date = daysbeforedeleted
                        else:
                            print 'date \'%s\' error: %s' % (row[2].Value, e)
                            continue
                    try:
                        subject = row[1].Value
                    except AttributeError:
                        subject = 'No subject'
                    if date <= daysbeforedeleted:
                        if options.verbose and not options.progressbar:
                            print 'Delete item \'%s\' \'%s\'' % (subject, binascii.hexlify(entryid))
                        if options.dwd:
                            try:
                                if row[3].Value == 2147746063:
                                   folder.mapiobj.DeleteMessages([entryid], 0, None, DELETE_HARD_DELETE)
                            except MAPIErrorDiskError:
                                continue
                            except AttributeError:
                                continue
                        else:
                            try:
                                folder.mapiobj.DeleteMessages([entryid], 0, None, DELETE_HARD_DELETE)
                            except MAPIErrorDiskError as e:
                                print 'Error detected %s' % e
                                retry.append(row)

                        if options.progressbar:
                            pbar.update(itemcount + 1)
                        itemcount += 1

                if retry:
                    for row in retry:
                        try:
                            print row[0]
                            folder.mapiobj.DeleteMessages([row[0].Value], 0, None, DELETE_HARD_DELETE)
                        except MAPIErrorDiskError as e:
                            print 'Giving up for %s %s' % (row, e)
                            continue

        if options.progressbar:
            pbar.finish()
        if options.verbose:
            print '%s items where purged' % itemcount

    print 'Softdelete purge done.'


if __name__ == '__main__':
    main()