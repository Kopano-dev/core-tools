#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


import kopano
from tabulate import tabulate
from datetime import datetime

import locale
import sys
locale.setlocale(locale.LC_ALL, '')


def opt_args():
    parser = kopano.parser('skfpcmuUP')
    parser.add_option("--hidden", dest="hidden", action="store_true", help="Show hidden folders")
    parser.add_option("--public", dest="public", action="store_true", help="Run for public store")
    parser.add_option("--summary", dest="summary", action="store_true", help="Show total store size")
    parser.add_option("--older-then", dest="timestamp", action="store", help="Hide items that are younger then (dd-mm-yyyy 00:00)")
    return parser.parse_args()

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def get_stats(options, folders, storename):
    table_header = ["Folder path", "Items in folder",  "Folder size"]
    table_data = []
    items = 0
    store_size = 0
    total_folders = 0
    for folder in folders:
        if folder.path:
            name = folder.path
        else:
            if not options.hidden:
                continue
            name = ".{}".format(folder.name)

        if options.timestamp:
            count = 0
            older_then = datetime.strptime(options.timestamp, '%d-%m-%Y %H:%M')
            for item in folder.items():
                if item.received <= older_then:
                    break
                count += 1
            count = folder.count - count

        else:
            count = folder.count
        size = locale.format('%d', folder.size, 1)

        items += count
        total_folders += 1
        store_size += folder.size

        table_data.append([name, count, '{} ({} bytes)'.format(sizeof_fmt(folder.size), size)])

    if options.summary:
        print('{}: {} ({} bytes)' .format(storename, sizeof_fmt(store_size), store_size))
    else:
        print('{} folders and {} items in store of {}'.format(total_folders, items, storename))
        print(tabulate(table_data, headers=table_header, tablefmt="grid"))

def main():
    options, args = opt_args()
    server = kopano.Server(options)
    if options.public:
        public_store = server.public_store
        if not public_store:
            print('Public store not found')
            sys.exit(1)
        folders = public_store.root.folders()
        get_stats(options, folders, 'public store')
    else:
        for user in server.users():
            folders = user.store.root.folders()
            get_stats(options, folders, user.name)

if __name__ == "__main__":
    main()

