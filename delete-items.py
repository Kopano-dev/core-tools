#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#
import kopano
import sys
from MAPI.Util import *
from datetime import datetime

def opt_args():
    parser = kopano.parser('skpfucm')

    parser.add_option("--from", dest="from_date", action="store", help="Remove items older than x (YYYY-MM-DD)")
    parser.add_option("--until", dest="until_date", action="store", help="Remove item till this date (YYYY-MM-DD)")
    parser.add_option("--all", dest="all", action="store_true", help="Remove all items")
    parser.add_option("--dry-run", dest="dry_run", action="store_true", help="Dry run")
    return parser.parse_args()

def main():
    options, args = opt_args()

    if not options.users :
        print 'Usage:\n%s -u <username> ' % sys.argv[0]
        sys.exit(1)

    if not options.from_date and not options.until_date:
        print 'usage:\n%s -u <username> --from* YYYY-MM-D --until* YYYY-MM-DD \n' \
              '* only one parameter is required ' % (sys.argv[0])
        sys.exit(1)

    current_date = datetime.now()
    if options.from_date:
        from_date = datetime.strptime(options.from_date, '%Y-%m-%d')
    else:
        from_date = datetime.strptime('1970-01-01', '%Y-%m-%d')
    if options.until_date:
        until_date = datetime.strptime(options.until_date, '%Y-%m-%d')
    else:
        until_date = datetime.strptime('2038-01-19', '%Y-%m-%d')

    for user in kopano.Server(options).users():
        item_delete = 0
        print 'Runnig for user %s' % user.name
        for folder in user.store.folders():
            print 'Search items in %s' % folder.name
            for item in folder.items():
                if item.received == None:
                    received_date = item.created
                else:
                    received_date = item.received
                print item
                if received_date >= from_date and received_date <= until_date:
                    item_delete += 1
                    if options.dry_run:
                        print '{:150} {}'.format(item.subject, item.received)
                    else:
                        folder.delete(item)

        print '\nDeleted items : %s' % item_delete
if __name__ == "__main__":
    main()
