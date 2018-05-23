#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from __future__ import print_function
from __future__ import unicode_literals
import kopano

NOSTORE = 'No Store Attached'


def main():
    kopano.parser('skpcu').parse_args()
    print ('{:50} {:50} {:50}'.format(
        'Username', 'Store GUID', 'Archive GUID'))
    for user in kopano.Server().users(parse=True):

        if getattr(user.store, 'guid', False):
            store_id = user.store.guid.upper()
        else:
            store_id = NOSTORE
        if user.archive_store:
            archive_id = user.archive_store.guid.upper()
        else:
            archive_id = NOSTORE
        print ('{:50} {:50} {:50}'.format(user.name, store_id, archive_id))


if __name__ == "__main__":
    main()
