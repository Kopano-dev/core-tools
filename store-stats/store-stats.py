#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


import kopano
from tabulate import tabulate
import locale
locale.setlocale(locale.LC_ALL, '')


def opt_args():
    parser = kopano.parser('skpcmuUP')
    parser.add_option("--hidden", dest="hidden", action="store_true", help="Show hidden folders")
    return parser.parse_args()

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def main():
    options, args = opt_args()
    table_header = ["Folder path", "Items in folder",  "Folder size"]
    for user in kopano.Server(options).users():
        table_data = []
        folders = user.store.root.folders()
        items= 0
        total_folders = 0
        for folder in folders:

            size = locale.format('%d', folder.size, 1)
            if folder.path:
                name = folder.path
            else:
                if not options.hidden:
                    continue
                name = ".{}".format(folder.name)
            items += folder.count
            total_folders += 1
            table_data.append([name, folder.count, '{} ({} bytes)'.format(sizeof_fmt(folder.size), size)])
        print('{} folders and {} items in store of {}'.format(total_folders, items, user.name))
        print(tabulate(table_data, headers=table_header,tablefmt="grid"))
if __name__ == "__main__":
    main()

