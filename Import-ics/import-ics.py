#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import kopano
from MAPI.Util import *
import requests
import sys
import re
import requests

def opt_args():
    parser = kopano.parser('skpucmUP')
    parser.add_option("--all", dest="all", action="store_true", help="Run for all users ")
    parser.add_option("--import", dest="import_ics", action="store", help="Path/url to ics file")
    parser.add_option("--calendar", dest="calendar", action="store", help="Calendar folder where to import the ics file")
    parser.add_option("--purge", dest="purge", action="store_true", help="purge folder on import")

    return parser.parse_args()

def url(str):
   ur = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str)
   if len(ur) > 0:
       return True

   return False


def main():
    options, args = opt_args()
    if not options.users and not options.all:
        print('please run:\n'
              'python3 {} -u username --import /path/to/ics/file --calendar foldername'
              '\nor\n'
              'python3 {} --all  --import /path/to/ics/file --calendar foldername '.format(sys.argv[0], sys.argv[0]))
        sys.exit(1)
    for user in kopano.Server(options).users():
        # Open folder of create if not exist
        folder = user.store.folder(options.calendar, create=True)
        # Check if container_class is IPF.Calendar
        if not folder.container_class == 'IPF.Appointment':
            folder.container_class = 'IPF.Appointment'

        # check if we need to download the ics file or open it from the filesystem
        if url(options.import_ics):
            r = requests.get(options.import_ics)
            if r.content:
                ics_file = r.content
            else:
                print('can\'t read ics file')
                print(r.raw)
        else:
            with open(options.import_ics,'rb') as f:
                ics_file = f.read()
        # Purge folder if parameter ---purge is given
        if options.purge:
            folder.empty()

        # Import the ics file
        folder.read_ics(ics_file)
        print('addde ics data')

if __name__ == "__main__":
    main()
