#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#

import kopano
from kopano.defs import RIGHT_NAME, EID_EVERYONE
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
    parser.add_option("--root-only", dest="only_store", action="store_true", help="Remove permissions of only the ROOT/Store folder")
    parser.add_option("--add", dest="add", action="store", help="Add permissions for this user")
    parser.add_option("--permission", dest="permission", action="store",
                      help="Set permissions [norights|readonly|secretary|owner|fullcontrol] or use the calculate "
                           "options to give a custom permission set")
    parser.add_option("--delegate", dest="delegate", action="store_true", help="Add user as delegate")
    parser.add_option("--private", dest="private", action="store_true", help="Allow delegate to see private items")
    parser.add_option("--copy", dest="copy", action="store_true", help="Send copy of meeting request to delegate")



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
    table.SetColumns([PR_ENTRYID, PR_MEMBER_ID, CHANGE_PROP_TYPE(PR_MEMBER_NAME, PT_UNICODE), PR_MEMBER_RIGHTS], TBL_BATCH)
    acltable = table.QueryRows(-1, 0)

    for acl in acltable:
        name = None
        for prop in acl:
            if prop.ulPropTag == 0x6672001F:
                name = prop.Value
            if prop.ulPropTag == 0x66730003:

                if definepermissions.get(prop.Value):
                    permission = definepermissions[prop.Value]
                else:
                    permission = 'Other'
                    r = []
                    for right, right_name in RIGHT_NAME.items():
                        if prop.Value & right:
                            r.append(right_name)
                    if len(r) > 0:
                        name = '{}: {}'.format(name, ', '.join(r).replace('_',' '))

                perfolder[permission].append(name)

    return perfolder


def getdelegateuser(user):
    '''
    Delegates are stored in 2 places
    the first one is for the delegate info and if the delegate can see private items.
    The second one is a rule to check if the meeting request need to be forwarded to the delegate
    :param user:
    :return: dict
    '''
    inbox = user.store.inbox

    names = {}
    names['users'] = {}

    freebusyprops = inbox.mapiobj.GetProps([PR_FREEBUSY_ENTRYIDS], 0)
    fbmsg = user.store.mapiobj.OpenEntry(freebusyprops[0].Value[1], None, MAPI_MODIFY)
    fbProps = fbmsg.GetProps(
        [PR_SCHDINFO_DELEGATE_ENTRYIDS, CHANGE_PROP_TYPE(PR_SCHDINFO_DELEGATE_NAMES, PT_MV_UNICODE), PR_DELEGATE_FLAGS],
        0)

    # Check if user is allowed to see private items
    if fbProps[0].ulPropTag == PR_SCHDINFO_DELEGATE_ENTRYIDS:
        for i in range(0, len(fbProps[0].Value)):
            entryid = binascii.hexlify(fbProps[0].Value[i])
            # if not names['users'].get(fbProps[1].Value[i]):
            if not names['users'].get(entryid):
                names['users'][entryid] = {}
                names['users'][entryid]['name'] = fbProps[1].Value[i]
                names['users'][entryid]['private'] = bool(fbProps[2].Value[i])

    # check if a meeting request need to be sent to the delegate
    for rule in inbox.rules():
        if rule.name == 'Delegate Meetingrequest service':
            for dellist in rule.mapirow[1719664894].lpAction[0].actobj.lpadrlist:
                for prop in dellist:
                    if prop.ulPropTag == 268370178:
                        entryid = binascii.hexlify(prop.Value)
                        if not names['users'].get(entryid):
                            names['users'][entryid] = {}
                    if prop.ulPropTag == 805371935:
                        names['users'][entryid]['name'] = prop.Value ## XXX add names here as well as pyko adds the username for private items
                        names['users'][entryid]['delegate'] = True

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
            delegate = u"\u2717"

        if delnames['users'][deluser].get('private'):
            private = u"\u2713"
        else:
            private =u"\u2717"

        if delegate or private:
            tabledelagate_data.append([delnames['users'][deluser]['name'], private, delegate])

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
    if options.remove.lower() == 'everyone':
        removeuser = 'Everyone'
        remuser = None
    else:
        remuser = kopano.Server(options).user(options.remove)
        removeuser = remuser.fullname

    # so not remove folder if delegate is passed and no folder
    if options.delegate:
        if not remuser:
            print('everyone can not be removed at the moment with the script')
        else:
            flags = []
            if options.private:
                flags.append('see_private')
            if options.copy:
                flags.append('send_copy')
            try:
                dlg = user.delegation(remuser)
                if len(flags) == 0:
                    user.delete(dlg)
                    print('removing delegate permission for user {}'.format(remuser.name))
                else:
                    dlg.flags = [f for f in dlg.flags if f not in flags]
                    print('removing {} for delegate user {}'.format(' '.join(flags), remuser.name))
            except kopano.errors.NotFoundError:
                print('user {} is not a delegate'.format(remuser.name))

    if not options.folders and options.delegate:
        sys.exit(0)

    acl_table = folder.mapiobj.OpenProperty(PR_ACL_TABLE, IID_IExchangeModifyTable, 0, 0)
    table = acl_table.GetTable(0)
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


def create_table_row_permission(foldername, options, permission):
    acl_table = foldername.mapiobj.OpenProperty(PR_ACL_TABLE, IID_IExchangeModifyTable, 0, 0)
    table = acl_table.GetTable(0)
    table.SetColumns([PR_ENTRYID, PR_MEMBER_ID, CHANGE_PROP_TYPE(PR_MEMBER_NAME, PT_UNICODE), PR_MEMBER_RIGHTS], TBL_BATCH)
    acltable = table.QueryRows(-1, 0)

    newvalue = len(acltable) + 1
    if options.add.lower() == 'everyone':
        adduser = binascii.hexlify(EID_EVERYONE)
        fullname = 'Everyone'
    else:
        newuser = kopano.Server(options).user(options.add)
        adduser = newuser.userid
        fullname = newuser.fullname

    rowlist = [ROWENTRY(
        ROW_ADD,
        [SPropValue(0x0FFF0102, binascii.unhexlify(adduser)),
         SPropValue(0x66710014, newvalue),
         SPropValue(0x6672001F, fullname),
         SPropValue(0x66730003, permission)])]

    acl_table.ModifyTable(0, rowlist)

def addpermissions(user, options, foldername):
    if not options.permission and not options.delegate:
        print('please use: {} --user <username> --add  <username> --permission <permission>'.format(sys.argv[0]))
        sys.exit(1)

    if options.delegate:
        flags = []
        delegateuser = kopano.Server(options).user(options.add)
        dlg = user.delegation(delegateuser, create=True)
        if options.private:
            flags.append('see_private')
        if options.copy:
            flags.append('send_copy')
        if len(flags) > 0:
            dlg.flags += flags
            print('Add {} as delegate with {}'.format(delegateuser.name, ' '.join(flags)))
        else:
            print('Add {} as delegate'.format(delegateuser.name))

    if not options.permission and options.delegate:
        sys.exit(0)

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

    # if container class is IPF.Appointment add permission to the Freebusy Data folder as wel
    try:
        if foldername.container_class == 'IPF.Appointment':
            freebusy = user.store.root.folder('Freebusy Data')
            create_table_row_permission(freebusy, options, permission)
    except AttributeError:
        pass



    create_table_row_permission(foldername, options, permission)


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
            if options.only_store:
                sys.exit(0)
        for folder in userstore.folders(parse=True):
           removepermissions(user, options, folder)

    if options.add:
        if options.folders:
            for folder in user.store.folders(parse=True):
                addpermissions(user, options, folder)
        else:
            addpermissions(user, options, user.store)

if __name__ == "__main__":
    main()
