#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#

import kopano
from MAPI.Util import *
import sys
import binascii
from tabulate import tabulate
if sys.version_info <= (3, 0):
    print('Script is only working with python 3 ')
    sys.exit(1)

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

ecRightsFullControl = 0x000004FB

ecRightsTemplateNoRights = ecRightsFolderVisible
ecRightsTemplateReadOnly = ecRightsTemplateNoRights | ecRightsReadAny
ecRightsTemplateSecretary = ecRightsTemplateReadOnly | ecRightsCreate | ecRightsEditOwned | ecRightsDeleteOwned | ecRightsEditAny | ecRightsDeleteAny
ecRightsTemplateOwner = ecRightsTemplateSecretary | ecRightsCreateSubfolder | ecRightsFolderAccess
EMS_AB_ADDRESS_LOOKUP = 0x1


def opt_args():
    parser = kopano.parser('skpcfUP')
    parser.add_option("--user", dest="user", action="store", help="Run script for user ")
    parser.add_option("--list", dest="printrules", action="store_true", help="Print rules")
    parser.add_option("--list-all", dest="printrulesall", action="store_true", help="Print rules including the 'hidden' folders")
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
    table.SetColumns([PR_ENTRYID, PR_MEMBER_ID, CHANGE_PROP_TYPE(PR_MEMBER_NAME, PT_UNICODE), PR_MEMBER_RIGHTS], TBL_BATCH)
    acltable = table.QueryRows(-1, 0)

    for acl in acltable:
        for prop in acl:
            if prop.ulPropTag == 0x6672001F:
                name = prop.Value
            if prop.ulPropTag == 0x66730003:
                permission = 'Other'
                if definepermissions.get(prop.Value):
                    permission = definepermissions[prop.Value]

                perfolder[permission].append(name)

    return perfolder


def getdelegateuser(user):
    inbox = user.store.inbox

    names = {}
    names['users'] = {}

    freebusyprops = inbox.mapiobj.GetProps([PR_FREEBUSY_ENTRYIDS], 0)
    fbmsg = user.store.mapiobj.OpenEntry(freebusyprops[0].Value[1], None, MAPI_MODIFY)
    fbProps = fbmsg.GetProps(
        [PR_SCHDINFO_DELEGATE_ENTRYIDS, CHANGE_PROP_TYPE(PR_SCHDINFO_DELEGATE_NAMES, PT_MV_UNICODE), PR_DELEGATE_FLAGS],
        0)

    if fbProps[0].ulPropTag == PR_SCHDINFO_DELEGATE_ENTRYIDS:
        for i in range(0, len(fbProps[0].Value)):
            if not names['users'].get(fbProps[1].Value[i]):
                names['users'][fbProps[1].Value[i]] = {}
                names['users'][fbProps[1].Value[i]]['private'] = bool(fbProps[2].Value[i])

    for rule in inbox.rules():
        if rule.name == 'Delegate Meetingrequest service':
            for dellist in rule.mapirow[1719664894].lpAction[0].actobj.lpadrlist:
                for prop in dellist:
                    if prop.ulPropTag == 268370178:
                        entryid = prop.ulPropTag
                    if prop.ulPropTag == 805371935:
                        if not names['users'].get(prop.Value):
                            names['users'][prop.Value] = {}

                        names['users'][prop.Value]['delegate'] = True

    return names


def listpermissions(user, options):
    tabledelagate_header = ["User","See private items", "Send copy"]
    tabledelagate_data = []
    #delegate info
    delnames = getdelegateuser(user)

    for deluser in delnames['users']:

        try:
            if delnames['users'][deluser]['delegate']:
                delegate = u"\u2713"
        except:
            delegate = 'x'

        if delnames['users'][deluser]['private']:
            private = u"\u2713"
        else:
            private = 'x'

        if delegate or private:
            tabledelagate_data.append([deluser, private, delegate])

    #acl rules
    table_header = ["Folder", "Fullcontroll", "Owner", "Secretary", "Readonly", "No rights", "Other"]
    tableacl_data =[]

    store = user.store
    if not options.folders:
        perfolder = getpermissions(store)
        tableacl_data.append(['Store', '\n'.join(perfolder['Full control']), '\n'.join(perfolder['Owner']),
                           '\n'.join(perfolder['Secretary']),
                           '\n'.join(perfolder['Readonly']), '\n'.join(perfolder['No rights']),
                           '\n'.join(perfolder['Other'])])
    if options.printrulesall:
        folders = store.root.folders()
    else:
        folders = store.folders()
    for folder in folders:
        perfolder = getpermissions(folder)
        folderindent = ''
        if folder.path:
            for i in range(0, len(folder.path.split('/')) - 1):
                folderindent += '-'

        foldername = '%s %s ' % (folderindent, folder.name)
        tableacl_data.append([foldername, '\n'.join(perfolder['Full control']), '\n'.join(perfolder['Owner']),
                           '\n'.join(perfolder['Secretary']),
                           '\n'.join(perfolder['Readonly']), '\n'.join(perfolder['No rights']),
                           '\n'.join(perfolder['Other'])])


    print('Store information {}'.format(user.name))
    if len(tabledelagate_data) > 0:
        print('Delegate information:')
        print(tabulate(tabledelagate_data, headers=tabledelagate_header, tablefmt="grid", stralign="center"))

    print('Folder permissions:')
    print(tabulate(tableacl_data, headers=table_header, tablefmt="grid"))


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

    perm = input("Please select the permissions (1,5,7)\n"
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

    print('Please use the following value for changing the permissions {}'.format(hex(calculate)))


def removepermissions(user, options, folder, customname=None):

    removeuser = kopano.Server(options).user(options.remove).fullname

    acl_table = folder.mapiobj.OpenProperty(PR_ACL_TABLE, IID_IExchangeModifyTable, 0, 0)
    table = acl_table.GetTable(0)
    cols = table.QueryColumns(TBL_ALL_COLUMNS)
    table.SetColumns([PR_ENTRYID, PR_MEMBER_ID, CHANGE_PROP_TYPE(PR_MEMBER_NAME, PT_UNICODE), PR_MEMBER_RIGHTS], TBL_BATCH)
    acltable = table.QueryRows(-1, 0)
    remove = False
    for acl in acltable:
        for prop in acl:
            if prop.ulPropTag == 0x6672001F:
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
        print('removing {} from the permission table for folder {}'.format(removeuser, foldername))


def create_table_row(foldername, options, permission):
    acl_table = foldername.mapiobj.OpenProperty(PR_ACL_TABLE, IID_IExchangeModifyTable, 0, 0)
    table = acl_table.GetTable(0)
    # cols = table.QueryColumns(TBL_ALL_COLUMNS)
    table.SetColumns([PR_ENTRYID, PR_MEMBER_ID, CHANGE_PROP_TYPE(PR_MEMBER_NAME, PT_UNICODE), PR_MEMBER_RIGHTS], TBL_BATCH)
    acltable = table.QueryRows(-1, 0)

    newvalue = len(acltable) + 1
    adduser = kopano.Server(options).user(options.add)
    rowlist = [ROWENTRY(
        ROW_ADD,
        [SPropValue(0x0FFF0102, binascii.unhexlify(adduser.userid)),
         SPropValue(0x66710014, newvalue),
         SPropValue(0x6672001F, adduser.fullname),
         SPropValue(0x66730003, permission)])]

    acl_table.ModifyTable(0, rowlist)

def addpermissions(user, options, foldername):
    if not options.permission:
        print('please use: {} --user <username> --add  <username> --permission <permission>'.format(sys.argv[0]))
        sys.exit(1)

    convertrules = {"norights": ecRightsTemplateNoRights,
                    "readonly": ecRightsTemplateReadOnly,
                    "secretary": ecRightsTemplateSecretary,
                    "owner": ecRightsTemplateOwner,
                    "fullcontrol": ecRightsFullControl
                    }

    if convertrules.get(options.permission.lower()):
        permission = convertrules[options.permission.lower()]
    else:
        permission = int(options.permission, 0)

    # if container class is IPF.Appointment  add permission to the Freebusy Data folder as wel
    if foldername.container_class == 'IPF.Appointment':
        freebusy = user.store.root.folder('Freebusy Data')
        create_table_row(freebusy, options, permission)

    create_table_row(foldername, options, permission)

    if foldername.name == user.name:
        foldername = 'Main store'
    else:
        foldername = foldername.name
    print('Added user {} with rights {} on folder {}'.format(options.add, options.permission, foldername))


def main():
    options, args = opt_args()

    if options.calc:
        calculatepermissions()
        sys.exit(0)

    if not options.user:
        print('please use:  %s --user <username>'.format(sys.argv[0]))
        sys.exit(1)

    server = kopano.Server(options)
    user = server.user(options.user)

    if options.printrules or options.printrulesall:
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
