#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


import kopano
from MAPI.Util import *


def opt_args():
    parser = kopano.parser('skpcfuUPv')
    parser.add_option("--all", dest="all", action="store_true", help="Run script for all users")
    parser.add_option("--clear-calendar", dest="cal", action="store_true", help="Clear the default calendar folder")
    parser.add_option("--clear-tasks", dest="task", action="store_true", help="Clear the default tasks folder")
    parser.add_option("--clear-notes", dest="notes", action="store_true", help="Clear the default notes folder")

    return parser.parse_args()


def main():
    options, args = opt_args()
    if not options.users and not options.all:
        print('please use\n{} --user <username>\nor\n{} --all'.format(sys.argv[0], sys.argv[0]))
        sys.exit(1)

    for user in kopano.Server(options).users():
        print(user.name)
        if options.cal:
            print('clearing Calendar')
            user.store.calendar.empty()
        if options.task:
            print('clearing Tasks')
            user.store.tasks.empty()
        if options.notes:
            print('clearing notes')
            user.store.notes.empty()

if __name__ == "__main__":
    main()
