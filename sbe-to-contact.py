#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from __future__ import print_function
from __future__ import unicode_literals
import kopano
import sys


def opt_args():
    parser = kopano.parser('sSkpcufmUPv')
    options, args = parser.parse_args()
    if not options.users:
        parser.print_help()
        exit()
    else:
        return options

def main():
    options = opt_args()
    print("Running in read only mode use -m to modify the database")
    for user in kopano.Server(options).users():
        changed_items= 0 
        for f in user.folders(recurse=True):
            if f.container_class == 'IPF.Contact':
                for item in f.items():
                    if item.message_class == 'IPM.Contact:SBE':
                        changed_items += 1
                        if options.verbose:
                            print('Fixing contact {}'.format(item.name))
                        if options.modify:
                            item.message_class = 'IPM.Contact'
            
        print('Fixed {} contacts for user {}'.format(changed_items, user.name))
              


if __name__ == "__main__":
    main()
