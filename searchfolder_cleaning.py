#!/usr/bin/env python

import datetime

import kopano
from MAPI.Util import  *



for u in kopano.users():
    print('User: %s' % u.name)
    findroot = u.findroot
    if not findroot:
        print('No findroot for user "%s"' % u.name)
        continue

        # Saved searchfolder list
    try:
        saved_sf = list(u.store.searches())
    except MAPIErrorNotFound:
        saved_sf = []

    # If the search folder is a permanent search folder, we keep it.
    # If it's a normal search folder that's older than 7 days, remove it for performance improvement.
    for sf in findroot.folders():
        if sf not in saved_sf:
            if sf.created < datetime.datetime.now() - datetime.timedelta(days=7):
                print('Removing searchfolder "%s"' % sf.name)
                findroot.delete(sf)

