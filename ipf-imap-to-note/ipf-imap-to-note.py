#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import kopano
import sys


def opt_args():
    parser = kopano.parser('skpcufm')
    parser.add_option(
        "--dry-run",
        dest="dryrun",
        action="store_true",
        help="run the script without executing any actions")
    return parser.parse_args()


def main():
    options, args = opt_args()
    if not options.users:
        print('Usage: %s -u <username> ' % sys.argv[0])
        sys.exit(1)
    else:
        for user in kopano.Server(options).users():
            print 'Checking user store: %s' % user.name
            for f in user.folders(recurse=True):
                if f.container_class == 'IPF.Imap':
                    print '%s: IPF.Imap folder detected' % f.name
                    if not options.dryrun:
                        print '%s: Changing container_class to IPF.Note' % f.name
                        f.container_class = 'IPF.Note'


if __name__ == "__main__":
    main()
