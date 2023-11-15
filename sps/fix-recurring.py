#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


import kopano
from MAPI.Util import *


def opt_args():
    parser = kopano.parser('skpcfuUPv')
    parser.add_option("--all", dest="all", action="store_true", help="Run script for all users")
    parser.add_option("--dry-run", dest="dryrun", action="store_true", help="Dry-run")

    return parser.parse_args()


def main():
    options, args = opt_args()
    if not options.users and not options.all:
        print('please use\n{} --user <username>\nor\n{} --all'.format(sys.argv[0], sys.argv[0]))
        sys.exit(1)

    for user in kopano.Server(options).users():
        for folder in user.store.folders():
            if folder.container_class == 'IPF.Appointment':
                for item in folder.items():
                    if item.get_prop('appointment:33302'):
                        if not item.recurring:
                            print('Fixing {}'.format(item.subject))
                            if not options.dryrun:
                                item[kopano.pidlid.PidLidRecurring] = True


if __name__ == "__main__":
    main()
