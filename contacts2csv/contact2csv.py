#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import kopano
import sys
import csv
from MAPI.Util import *
import MAPI.Util
import MAPI.Time
import time
import pickle
from datetime import datetime
import os

scriptdir = os.path.dirname(os.path.realpath(__file__))


extra = {"PR_DISPLAY_NAME_FULL": 0x8130001f,
         "PR_EMAIL": 0x8133001f,
         "PR_FILE_AS": 0x80b5001f,
         "PR_WEBSITE": 0x80db001f,
         "PR_MAIL": 0x8134001f,
         "PR_ADDRESS": 0x80f5001f,
         "PR_CITY": 0x80f6001f,
         "PR_STATE": 0x80f7001f,
         "PR_ZIP": 0x80f8001f,
         "PR_COUNTRY": 0x80f9001f,
         "PR_IM": 0x8112001f,
         "PR_EMAIL2": 0X8144001F,
         "PR_MAIL2": 0X8143001F,
         "PR_DISPLAY_NAME_FULL2": 0X8140001F,
         "PR_EMAIL3": 0X8154001F,
         "PR_MAIL3": 0X8153001F,
         "PR_DISPLAY_NAME_FULL3": 0X8150001F
}


def opt_args():
    parser = kopano.parser('skpcm')
    parser.add_option("--user", dest="user", action="store", help="Run script for user")
    parser.add_option("--folder", dest="folder", action="store", help="Select an other contacts folder then the default one")
    parser.add_option("--export", dest="export", action="store_true", help="export contacts")
    parser.add_option("--import", dest="restore", action="store", help="import contacts")
    parser.add_option("--delimiter", dest="delimiter", action="store", help="Change delimiter (default is ,)")
    parser.add_option("--purge", dest="purge", action="store_true", help="Purge contacts before the import")
    parser.add_option("--progressbar", dest="progressbar", action="store_true", help="Show progressbar ")

    return parser.parse_args()


def progressbar(count):
    try:
        from progressbar import Bar, AdaptiveETA, Percentage, ProgressBar
    except ImportError:
        print '''Please download the progressbar library from https://github.com/niltonvolpato/python-progressbar or
        run without the --progressbar parameter'''
        sys.exit(1)
    widgets = [Percentage(),
               ' ', Bar(),
               ' ', AdaptiveETA()]
    progressmax = count
    pbar = ProgressBar(widgets=widgets, maxval=progressmax)
    pbar.start()

    return pbar


def getprop(item, myprop):

    try:
        if item.prop(myprop).typename == 'PT_UNICODE':
            return item.prop(myprop).value.encode('utf-8')
        if item.prop(myprop).typename == 'PT_SYSTIME':
            epoch = datetime.utcfromtimestamp(0)
            return (item.prop(myprop).value - epoch).total_seconds()
    except MAPIErrorNotFound:
        return None


def main():
    options, args = opt_args()
    if not options.user:
        sys.exit('Please use:\n %s --user <username>  ' % (sys.argv[0]))
    contactsarray = []
    user = kopano.Server(options).user(options.user)
    print 'running script for \'%s\'' % user.name
    if options.delimiter:
        delimiter = options.delimiter
    else:
        delimiter = ','
    if options.export:
        if options.folder:
            contacts = user.store.folder(options.folder)
        else:
            contacts = user.store.contacts
        if options.progressbar:
            pbar = progressbar(contacts.count * 2)
        print 'export contacts'
        itemcount = 0
        for contact in contacts.items():
            if options.progressbar:
                pbar.update(itemcount + 1)
            contactsarray.append(
                [getprop(contact, PR_SUBJECT_W), getprop(contact, PR_DISPLAY_NAME_W), getprop(contact, PR_GENERATION_W),
                 getprop(contact, PR_GIVEN_NAME_W), getprop(contact, PR_BUSINESS_TELEPHONE_NUMBER_W),
                 getprop(contact, PR_HOME_TELEPHONE_NUMBER_W), getprop(contact, PR_SURNAME_W),
                 getprop(contact, PR_COMPANY_NAME_W), getprop(contact, PR_TITLE_W),
                 getprop(contact, PR_DEPARTMENT_NAME_W), getprop(contact, PR_OFFICE_LOCATION_W),
                 getprop(contact, PR_PRIMARY_TELEPHONE_NUMBER_W), getprop(contact, PR_BUSINESS2_TELEPHONE_NUMBER_W),
                 getprop(contact, PR_MOBILE_TELEPHONE_NUMBER_W), getprop(contact, PR_RADIO_TELEPHONE_NUMBER_W),
                 getprop(contact, PR_CAR_TELEPHONE_NUMBER_W), getprop(contact, PR_OTHER_TELEPHONE_NUMBER_W),
                 getprop(contact, PR_PAGER_TELEPHONE_NUMBER_W), getprop(contact, PR_PRIMARY_FAX_NUMBER_W),
                 getprop(contact, PR_BUSINESS_FAX_NUMBER_W), getprop(contact, PR_HOME_FAX_NUMBER_W),
                 getprop(contact, PR_TELEX_NUMBER_W), getprop(contact, PR_ISDN_NUMBER_W),
                 getprop(contact, PR_ASSISTANT_TELEPHONE_NUMBER_W), getprop(contact, PR_HOME2_TELEPHONE_NUMBER_W),
                 getprop(contact, PR_ASSISTANT_W), getprop(contact, PR_MIDDLE_NAME_W),
                 getprop(contact, PR_DISPLAY_NAME_PREFIX_W), getprop(contact, PR_PROFESSION_W),
                 getprop(contact, PR_SPOUSE_NAME_W), getprop(contact, PR_TTYTDD_PHONE_NUMBER_W),
                 getprop(contact, PR_MANAGER_NAME_W), getprop(contact, PR_NICKNAME_W),
                 getprop(contact, PR_BUSINESS_HOME_PAGE_W), getprop(contact, PR_COMPANY_MAIN_PHONE_NUMBER_W),
                 getprop(contact, PR_HOME_ADDRESS_CITY_W), getprop(contact, PR_HOME_ADDRESS_COUNTRY_W),
                 getprop(contact, PR_HOME_ADDRESS_POSTAL_CODE_W), getprop(contact, PR_HOME_ADDRESS_STATE_OR_PROVINCE_W),
                 getprop(contact, PR_HOME_ADDRESS_STREET_W), getprop(contact, PR_OTHER_ADDRESS_CITY_W),
                 getprop(contact, PR_OTHER_ADDRESS_COUNTRY_W), getprop(contact, PR_OTHER_ADDRESS_POSTAL_CODE_W),
                 getprop(contact, PR_OTHER_ADDRESS_STATE_OR_PROVINCE_W), getprop(contact, PR_OTHER_ADDRESS_STREET_W),
                 getprop(contact, PR_WEDDING_ANNIVERSARY), getprop(contact, PR_BIRTHDAY),
                 getprop(contact, extra['PR_DISPLAY_NAME_FULL']), getprop(contact, extra['PR_EMAIL']),
                 getprop(contact, extra['PR_FILE_AS']),
                 getprop(contact, extra['PR_WEBSITE']), getprop(contact, extra['PR_MAIL']),
                 getprop(contact, extra['PR_MAIL2']), getprop(contact, extra['PR_DISPLAY_NAME_FULL2']),
                 getprop(contact, extra['PR_EMAIL2']),getprop(contact, extra['PR_MAIL3']),
                 getprop(contact, extra['PR_DISPLAY_NAME_FULL3']),getprop(contact, extra['PR_EMAIL3']),
                 getprop(contact, extra['PR_ADDRESS']),
                 getprop(contact, extra['PR_CITY']), getprop(contact, extra['PR_STATE']),
                 getprop(contact, extra['PR_ZIP']),
                 getprop(contact, extra['PR_COUNTRY']), getprop(contact, extra['PR_IM']), getprop(contact, PR_BODY_W)])
            itemcount += 1
        resultFile = open("%s_contacts.csv" % user.name, 'w')
        wr = csv.writer(resultFile, delimiter=delimiter)

        wr.writerow(['PR_SUBJECT', 'PR_DISPLAY_NAME', 'PR_GENERATION', 'PR_GIVEN_NAME', 'PR_BUSINESS_TELEPHONE_NUMBER',
                     'PR_HOME_TELEPHONE_NUMBER',
                     'PR_SURNAME', 'PR_COMPANY_NAME', 'PR_TITLE', 'PR_DEPARTMENT_NAME', 'PR_OFFICE_LOCATION',
                     'PR_PRIMARY_TELEPHONE_NUMBER',
                     'PR_BUSINESS2_TELEPHONE_NUMBER', 'PR_MOBILE_TELEPHONE_NUMBER', 'PR_RADIO_TELEPHONE_NUMBER',
                     'PR_CAR_TELEPHONE_NUMBER',
                     'PR_OTHER_TELEPHONE_NUMBER', 'PR_PAGER_TELEPHONE_NUMBER', 'PR_PRIMARY_FAX_NUMBER',
                     'PR_BUSINESS_FAX_NUMBER', 'PR_HOME_FAX_NUMBER',
                     'PR_TELEX_NUMBER', 'PR_ISDN_NUMBER', 'PR_ASSISTANT_TELEPHONE_NUMBER', 'PR_HOME2_TELEPHONE_NUMBER',
                     'PR_ASSISTANT', 'PR_MIDDLE_NAME',
                     'PR_DISPLAY_NAME_PREFIX', 'PR_PROFESSION', 'PR_SPOUSE_NAME', 'PR_TTYTDD_PHONE_NUMBER',
                     'PR_MANAGER_NAME', 'PR_NICKNAME',
                     'PR_BUSINESS_HOME_PAGE', 'PR_COMPANY_MAIN_PHONE_NUMBER', 'PR_HOME_ADDRESS_CITY',
                     'PR_HOME_ADDRESS_COUNTRY', 'PR_HOME_ADDRESS_POSTAL_CODE',
                     'PR_HOME_ADDRESS_STATE_OR_PROVINCE', 'PR_HOME_ADDRESS_STREET', 'PR_OTHER_ADDRESS_CITY',
                     'PR_OTHER_ADDRESS_COUNTRY',
                     'PR_OTHER_ADDRESS_POSTAL_CODE', 'PR_OTHER_ADDRESS_STATE_OR_PROVINCE', 'PR_OTHER_ADDRESS_STREET',
                     'PR_WEDDING_ANNIVERSARY', 'PR_BIRTHDAY',
                     'PR_DISPLAY_NAME_FULL', 'PR_EMAIL', 'PR_FILE_AS', 'PR_WEBSITE', 'PR_MAIL',
                     'PR_DISPLAY_NAME_FULL2', 'PR_EMAIL2','PR_MAIL2','PR_DISPLAY_NAME_FULL3', 'PR_EMAIL3','PR_MAIL3',
                     'PR_ADDRESS', 'PR_CITY', 'PR_STATE', 'PR_ZIP', 'PR_COUNTRY', 'PR_IM', 'PR_BODY'])
        print contactsarray
        for contact in contactsarray:
            if options.progressbar:
                pbar.update(itemcount + 1)
            wr.writerows([contact])
            itemcount += 1
        if options.progressbar:
            pbar.finish()

    if options.restore:
        if options.folder:
            contacts = user.store.folder(options.folder)
        else:
            contacts = user.store.contacts
        if options.purge:
            contacts.empty()
        if options.progressbar:
            cr = csv.reader(open(options.restore, "rb"), delimiter=delimiter)
            pbar = progressbar(sum(1 for row in cr))
        cr = csv.reader(open(options.restore, "rb"), delimiter=delimiter)
        headers = next(cr)
        total = len(headers)
        itemcount = 0
        for contact in cr:
            if contact[0]:
                if options.progressbar:
                    pbar.update(itemcount + 1)
                new_item = contacts.create_item()
                for num in range(0, total, 1):
                    if contact[num]:
                        if headers[num] == 'PR_WEDDING_ANNIVERSARY' or headers[num] == 'PR_BIRTHDAY':
                            datetime_date = datetime.fromtimestamp(int(contact[num][:-2]))
                            value = MAPI.Time.unixtime(time.mktime(datetime_date.timetuple()))
                        else:
                            value = contact[num].decode('utf-8').replace(u'\xa0', u' ')

                        if str(headers[num]) in extra:
                            new_item.mapiobj.SetProps([SPropValue(extra[headers[num]], value)])
                        else:
                            new_item.mapiobj.SetProps([SPropValue(getattr(MAPI.Util,headers[num]), value)])
                        new_item.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)
                try:
                    address = '%s\n%s\n%s\n%s\n' % (
                        new_item.prop(extra['PR_ADDRESS']).value, new_item.prop(extra['PR_CITY']).value,
                        new_item.prop(extra['PR_STATE']).value, new_item.prop(extra['PR_COUNTRY']).value)
                    new_item.mapiobj.SetProps([SPropValue(2160787487, u'%s' % address)])
                    new_item.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)
                except:
                    continue
                itemcount += 1
        if options.progressbar:
            pbar.finish()


if __name__ == "__main__":
    main()
