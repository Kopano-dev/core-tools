#!/usr/bin/env python3

# SPDX-License-Identifier: AGPL-3.0-or-later
import datetime
import kopano

def opt_args():
    parser = kopano.parser('skpcuUP')
    parser.add_option("--days", dest="days", default=30, type=int, action="store", help="Days to remove")
    parser.add_option("--keep-saved", dest="keep", action="store_true", help="Keep saved search folders")
    return parser.parse_args()


def main():
    options, args = opt_args()
    for u in kopano.Server(options).users():
        print('user', u.name)
        try:
            findroot = u.root.folder('FINDER_ROOT')
        except:
            print('ERROR getting findroot, skipping user')
            continue
        saved_sf = []
        if options.keep:
            saved_sf = list(u.store.searches())
        for sf in findroot.folders():
            if sf not in saved_sf:
                if sf.created < datetime.datetime.now()-datetime.timedelta(days=options.days):
                    print('deleting {} {} {} (created at {})'.format(sf.name, sf.entryid, sf.hierarchyid, sf.created))
                    findroot.delete(sf)


if __name__ == '__main__':
    main()
