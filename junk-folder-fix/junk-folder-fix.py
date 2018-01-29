#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


import kopano
from MAPI.Util import *


def opt_args():
    parser = kopano.parser('skpfucm')
    return parser.parse_args()


def main():
    options, args = opt_args()
    for user in kopano.Server(options).users():
        if user.store:
            if user.junk.name == 'Ongewenste E-mail':
                print('Renaming junk folder for user {}'.format(user.name))
                user.junk.mapiobj.SetProps([SPropValue(PR_DISPLAY_NAME, 'Ongewenste e-mail')])
                user.junk.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)


if __name__ == "__main__":
    main()
