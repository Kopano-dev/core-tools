#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


try:
    import kopano
except ImportError:
    import zarafa as kopano
from MAPI.Util import *
import re

def opt_args():
    parser = kopano.parser('skpcf')
    parser.add_option("--user", dest="user", action="store", help="Run script for user ")
    parser.add_option("--private", dest="private", action="store_true", help="")


    return parser.parse_args()

def searchemail(displayname):
    for word in displayname.split():
        if '@' in word:
            return word

    return False


def main():
    options, args = opt_args()

    user = kopano.Server(options).user(options.user)
    for item in user.store.sentmail:
        if options.private:
            print re.sub('q|w|e|r|t|y|u|i|o|p|a|s|d|f|g|h|j|k|l|z|x|c|v|b|n|m', 'x', item.prop(PR_DISPLAY_TO_W).value.lower())
        else:
            print item.prop(PR_DISPLAY_TO_W).value


if __name__ == "__main__":
    main()