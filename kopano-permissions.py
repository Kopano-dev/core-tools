#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#

import kopano
from MAPI.Util import *
import sys
import binascii
from terminaltables import AsciiTable

ecRightsNone = 0x00000000
ecRightsReadAny = 0x00000001
ecRightsCreate = 0x00000002
ecRightsEditOwned = 0x00000008
ecRightsDeleteOwned = 0x00000010
ecRightsEditAny = 0x00000020
ecRightsDeleteAny = 0x00000040
ecRightsCreateSubfolder = 0x00000080
ecRightsFolderAccess = 0x00000100
ecRightsFolderVisible = 0x00000400

ecRightsFullControl = 0x000004FBL

ecRightsTemplateNoRights = ecRightsFolderVisible
ecRightsTemplateReadOnly = ecRightsTemplateNoRights | ecRightsReadAny
ecRightsTemplateSecretary = ecRightsTemplateReadOnly | ecRightsCreate | ecRightsEditOwned | ecRightsDeleteOwned | ecRightsEditAny | ecRightsDeleteAny
ecRightsTemplateOwner = ecRightsTemplateSecretary | ecRightsCreateSubfolder | ecRightsFolderAccess
EMS_AB_ADDRESS_LOOKUP = 0x1


def opt_args():
    parser = kopano.parser('skpcf')
    parser.add_option("--user", dest="user", action="store", help="Run script for user ")
    parser.add_option("--list", dest="printrules", action="store_true", help="Print rules")
    parser.add_option("--details", dest="printdetails", action="store_true", help="Print more details")
    parser.add_option("--calculate", dest="calc", action="store_true", help="Calculate persmissions")
    parser.add_option("--remove", dest="remove", action="store", help="Remove permissions for this user")
    parser.add_option("--add", dest="add", action="store", help="Add permissions for this user")
    parser.add_option("--permission", dest="permission", action="store",
                      help="Set permissions [norights|readonly|secretary|owner|fullcontrol] or use the calculate "
                           "options to give a custom permission set")

    return parser.parse_args()


def getpermissions(folder, customname=None):
    definepermissions = {ecRightsTemplateNoRights: 'No rights',
                         ecRightsTemplateReadOnly: 'Readonly',
                         ecRightsTemplateSecretary: 'Secretary',
                         ecRightsTemplateOwner: 'Owner',
                         ecRightsFullControl: 'Full control'
                         }
    perfolder = {'No rights': [],
                 'Readonly': [],
                 'Secretary': [],
                 'Owner': [],
                 'Full control': [],
                 'Other': []
                 }

    acl_table = folder.mapiobj.OpenProperty(PR_ACL_TABLE, IID_IExchangeModifyTable, 0, 0)
    table = acl_table.GetTable(0)
    cols = table.QueryColumns(TBL_ALL_COLUMNS)
    table.SetColumns(cols, 0)
    acltable = table.QueryRows(-1, 0)
    for acl in acltable:
        for prop in acl:
            if prop.ulPropTag == 0x6672001E:
                name = prop.Value
            if prop.ulPropTag == 0x66730003:
                try:
                    permission = definepermissions[prop.Value]
                except KeyError:
                    permission = 'Other'
                perfolder[permission].append(name)

    return perfolder


def listpermissions(user, options):
    table_data = [["Folder", "Fullcontroll", "Owner", "Secretary", "Readonly", "No rights", "Other"]]
    store = user.store
    if not options.folders:
        perfolder = getpermissions(store)
        table_data.append(['Store', '\n'.join(perfolder['Full control']), '\n'.join(perfolder['Owner']),
                           '\n'.join(perfolder['Secretary']),
                           '\n'.join(perfolder['Readonly']), '\n'.join(perfolder['No rights']),
                           '\n'.join(perfolder['Other'])])

    for folder in store.folders():
        perfolder = getpermissions(folder)
        folderindent = ''
        for i in xrange(0, len(folder.path.split('/')) - 1):
            folderindent += '-'
        foldername = '%s %s ' % (folderindent, folder.name)
        table_data.append([foldername, '\n'.join(perfolder['Full control']), '\n'.join(perfolder['Owner']),
                           '\n'.join(perfolder['Secretary']),
                           '\n'.join(perfolder['Readonly']), '\n'.join(perfolder['No rights']),
                           '\n'.join(perfolder['Other'])])

    table = AsciiTable(table_data)

    print 'Store information %s ' % user.name
    print 'Folder permissions:'
    print table.table


def calculatepermissions():
    convertlist = {1: 0x00000002,
                   2: 0x00000001,
                   3: 0x00000080,
                   4: 0x00000100,
                   5: 0x00000400,
                   6: 0x00000008,
                   7: 0x00000020,
                   8: 0x00000010,
                   9: 0x00000040
                   }

    perm = raw_input("Please select the permissions (1,5,7)\n"
                     "[1] Create items\n"
                     "[2] Read items\n"
                     "[3] Create subfolders\n"
                     "[4] Folder permissions\n"
                     "[5] Folder visible\n"
                     "[6] Edit own items\n"
                     "[7] Edit all items\n"
                     "[8] Delete own items\n"
                     "[9] Delete all items\n")
    calculate = 0x00000000
    for number in perm.split(','):
        try:
            calculate = calculate | convertlist[int(number)]
        except ValueError:
            continue

    print 'Please use the following value for changing the permissions %s ' % hex(calculate)


def removepermissions(user, options, folder, customname=None):

    removeuser = kopano.Server(options).user(options.remove).fullname

    acl_table = folder.mapiobj.OpenProperty(PR_ACL_TABLE, IID_IExchangeModifyTable, 0, 0)
    table = acl_table.GetTable(0)
    cols = table.QueryColumns(TBL_ALL_COLUMNS)
    table.SetColumns(cols, 0)
    acltable = table.QueryRows(-1, 0)
    remove = False
    for acl in acltable:
        for prop in acl:
            if prop.ulPropTag == 0x6672001E:
                if removeuser == prop.Value:
                    rowlist = [ROWENTRY(
                        ROW_REMOVE,
                        acl
                    )]
                    remove = True
                    break
    if remove:
        acl_table.ModifyTable(0, rowlist)
        if customname:
            foldername = customname
        else:
            foldername = folder.name
        print 'removing %s from the permission table for folder %s ' % (removeuser, foldername)


def addpermissions(user, options, foldername):
    if not options.permission:
        print 'please use %s --user <username> --add  <username> --permission <permission>' % sys.argv[0]
        sys.exit(1)
    convertrules = {"norights": ecRightsTemplateNoRights,
                    "readonly": ecRightsTemplateReadOnly,
                    "secretary": ecRightsTemplateSecretary,
                    "owner": ecRightsTemplateOwner,
                    "fullcontrol": ecRightsFullControl
                    }
    try:
        permission = convertrules[options.permission]
    except KeyError:
        permission = int(options.permission, 0)


    acl_table = foldername.mapiobj.OpenProperty(PR_ACL_TABLE, IID_IExchangeModifyTable, 0, 0)
    table = acl_table.GetTable(0)
    cols = table.QueryColumns(TBL_ALL_COLUMNS)
    table.SetColumns(cols, 0)
    acltable = table.QueryRows(-1, 0)

    newvalue = len(acltable) + 1
    adduser = kopano.Server(options).user(options.add)
    rowlist = [ROWENTRY(
        ROW_ADD,
        [SPropValue(0x0FFF0102, binascii.unhexlify(adduser.userid)),
         SPropValue(0x66710014, newvalue),
         SPropValue(0x6672001E, adduser.fullname),
         SPropValue(0x66730003, permission)])]

    acl_table.ModifyTable(0, rowlist)


def main():
    options, args = opt_args()

    if options.calc:
        calculatepermissions()
        sys.exit(0)

    if not options.user:
        print 'please user %s --user <username>' % sys.argv[0]
        sys.exit(1)

    server = kopano.Server(options)
    user = server.user(options.user)

    if options.printrules:
        listpermissions(user, options)
        sys.exit(0)



    if options.remove:
        if not options.folders:
            removepermissions(user, options, user.store, 'Store')
        for folder in user.store.folders(parse=True):
            removepermissions(user, options, folder)

    if options.add:
        if options.folders:
            for folder in user.store.folders(parse=True):
                addpermissions(user, options, folder)
        else:
            addpermissions(user, options, user.store)


if __name__ == "__main__":
    main()
