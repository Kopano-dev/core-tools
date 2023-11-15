#!/usr/bin/env python3

# Do not use this in a production enviroment. It's dirty 
# Script is used for the demo enviroment on demo.kopano.com

import kopano
import pickle
import os
from MAPI.Tags import *
from datetime import datetime, timedelta
from calendar import monthrange

def opt_args():
    parser = kopano.parser('skpcuUPm')
    parser.add_option('--backup', dest='backup', action='store_true', help='backup')
    parser.add_option('--restore', dest='restore', action='store_true', help='restore')
    parser.add_option('--location', dest='location', action='store',  help='location')
    parser.add_option('--restore-from', dest='restore_from', action='store',  help='restore from user')
    return parser.parse_args()

def backup(server, options):
    location = './'
    if options.location:
        location = options.location
    if not os.path.exists(location):
        os.mkdir(location)
        
    for user in server.users():
        if not user.store:
            continue
        user_path = '{}/{}'.format(location, user.name)
        if not os.path.exists(user_path):
            os.mkdir(user_path)
        for folder in user.store.folders():
            if folder.count == 0:
                continue
            folder_path = '{}/{}'.format(user_path, folder.path)
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)
            for item in folder.items():
                item_path = '{}/{}'.format(folder_path, item.entryid)
                item.dump(open(item_path, 'wb'))

def restore(server, options):
    location = './'
    if options.location:
        location = options.location
    if not location.endswith('/'):
        location +='/'
    if options.restore_from:
        old = location
        location +='{}/'.format(options.restore_from)

    items = []
    for subdir, dirs, files in os.walk(location):
        for file in files:
            items.append(os.path.join(subdir, file))

    if options.restore_from:
        for user in server.users(parse=False):
            restore_items(items, server, options, old, user)
    else:
        restore_items(items, server, options, location)


def restore_items(items, server, options, location, override_user=None):
    
    user = None
    folder = None
    if override_user:
        user = override_user

    for item in items:
        tmp = item.replace(location,'').split('/')
        if not override_user:
            if not user or tmp[0] != user.name:
                print('change user ', tmp[0])
                user = server.user(tmp[0])
        item_folder = '/'.join(tmp[1:-1])
        if not folder or folder !=  folder.path:
            folder = user.store.folder(item_folder, create=True)
        new_item = folder.create_item(load=open(item, 'rb'))
        
        # change date to this year and month and try to put it on the same day as orginal planned
        if new_item.message_class == 'IPM.Appointment':
            new_item.start = convert_month(new_item.start)
            new_item.end =  convert_month(new_item.end)
            if new_item.get_prop("appointment:33293"):
                new_item.create_prop(new_item.prop("appointment:33293").proptag, convert_month(new_item.prop("appointment:33293").value))
            if new_item.get_prop("appointment:33294"):
                new_item.create_prop(new_item.prop("appointment:33294").proptag, convert_month(new_item.prop("appointment:33294").value))

            if new_item.get_prop("common:34070"):
                new_item.create_prop(new_item.prop("common:34070").proptag, convert_month(new_item.prop("common:34070").value))
            if new_item.get_prop("common:34071"):
                new_item.prop(new_item.prop("common:34071").proptag, convert_month(new_item.prop("common:34071").value))

            if new_item.get_prop("appointment:33333"):
                new_item.prop(new_item.prop("appointment:33333").proptag, convert_month(new_item.prop("appointment:33333").value))
            if new_item.get_prop("appointment:33334"):
                new_item.create_prop(new_item.prop("appointment:33334").proptag, convert_month(new_item.prop("appointment:33334").value))        

        if new_item.message_class == 'IPM.Note':
            new_date = convert_month(new_item.received, True)
            new_item.received = new_date
            new_item.create_prop(PR_CREATION_TIME, new_date)
            new_item.create_prop(PR_MESSAGE_DELIVERY_TIME, new_date)
            new_item.create_prop(PR_CLIENT_SUBMIT_TIME, new_date)


def convert_month(date, mail=None):
    today = datetime.now()
    this_month = today.month
    this_year = today.year
    # It can happen that we try to change to a date that doesn't exist.
    # Check the the day against the total days in this month and change it if needed
    days = monthrange(this_year, this_month)[1]
    day = int(date.strftime("%d"))
    if day > days:
        day =  day - (day - days)
    new_date = date.strftime('{}-{}-{:02d} %H:%M:%S'.format(this_year, this_month, day))
    new_date = datetime.strptime(new_date, "%Y-%m-%d %H:%M:%S")

    # Changing only the month and year for mails is strange as we then probably reveive mails in the future.
    if mail:
        if new_date > today:
            new_date =  new_date - timedelta(days=31)
    else:
        # Try to put the appoinment on the same weekday as original planned
        adjust = (int(date.strftime('%w')) - int(new_date.strftime('%w')))
        new_date = new_date + timedelta(days=adjust)
     
    return new_date

if __name__ == '__main__':
    options, args = opt_args()
    server =  kopano.Server(options)
    if options.backup:
        backup(server, options)
    if options.restore:
        restore(server, options)
