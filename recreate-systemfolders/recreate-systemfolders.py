import kopano
from kopano.errors import  *
import sys
import binascii
from MAPI.Util import *
import uuid

def opt_args():
    parser = kopano.parser('skpcfmUP')
    parser.add_option("--user", dest="user", action="store", help="Run script for user")
    parser.add_option("--create", dest="create", action="store", help="create folder")
    parser.add_option("--systemfolder", dest="systemfolder", action="store",
                      help="available: calendar, contacts, drafts, journal, notes, outbox, sentmail, task, wastebasket, junk")
    parser.add_option("--safe", dest="safe", action="store_true", help="won't delete the old system folder")

    return parser.parse_args()


def getprop(item, myprop):
    try:
        return item.prop(myprop).value
    except:
        return None


def main():
    options, args = opt_args()
    if not options.user:
        print('Please use:\n {} --user <username>  '.format(sys.argv[0]))
        sys.exit(1)

    user = kopano.Server(options).user(options.user)
    print(user)
    whitelist = ['calendar', 'contacts', 'drafts', 'journal', 'notes', 'outbox', 'sentmail', 'tasks',
                 'wastebasket', 'junk']
    name2ipf={
        'calendar': u'IPF.Appointment',
        'contacts': u'IPF.Contact',
        'journal': u'IPF.Journal',
        'notes': u'IPF.StickyNote',
        'tasks': u'IPF.Task',
    }
    storeid = {"sentmail": PR_IPM_SENTMAIL_ENTRYID,
               "outbox": PR_IPM_OUTBOX_ENTRYID,
               "wastebasket": PR_IPM_WASTEBASKET_ENTRYID}

    rootid = {"calendar": PR_IPM_APPOINTMENT_ENTRYID,
              "contacts": PR_IPM_CONTACT_ENTRYID,
              "drafts": PR_IPM_DRAFTS_ENTRYID,
              "journal": PR_IPM_JOURNAL_ENTRYID,
              "notes": PR_IPM_NOTE_ENTRYID,
              "tasks": PR_IPM_TASK_ENTRYID}

    if options.systemfolder in whitelist:
        if not options.create:
            oldfolder = getattr(user.store, options.systemfolder)
            oldname = oldfolder.name
            oldid = oldfolder.entryid

        # create new sent items box
        if options.create:
            name = options.create
            print('create folder "{}"'.format(name))
        else:
            name = str(uuid.uuid4())
            print('create tmp folder "{}"'.format(name))

        tmp = user.store.subtree.folder(name, create=True)

        if not options.create:
            # move all item to tmp folder
            print('copy items from old'.format(options.systemfolder))
            user.store.subtree.copy(oldfolder.items(), tmp)
            # delete old box

            if not options.safe:
                print('Delete {} folder'.format(options.systemfolder))
                getattr(user.store, options.systemfolder).delete(getattr(user.store, options.systemfolder))
            else:
                newname = uuid.uuid4()
                print('change the name of the old {} folder to {}'.format(options.systemfolder, newname.decode('utf-8')))

                getattr(user.store, options.systemfolder).mapiobj.create_prop(PR_DISPLAY_NAME, newname.decode('utf-8'))


            print('change {} to {}'.format(tmp.name, oldname))
            tmp.mapiobj.create_prop(PR_DISPLAY_NAME, oldname)
            if name2ipf.get(options.systemfolder):
                bla = tmp.create_prop(PR_CONTAINER_CLASS_W, name2ipf[options.systemfolder])
                print(tmp.container_class, options.systemfolder)

        # promote tmp file to  sytemfolders
        print('Promote new folder to be a system folder')
        if options.systemfolder in storeid:
            user.store.create_prop(storeid.get(options.systemfolder), binascii.unhexlify(tmp.entryid))

        if options.systemfolder in rootid:
            user.store.root.create_prop(rootid.get(options.systemfolder), binascii.unhexlify(tmp.entryid))

        if options.systemfolder == 'junk':
            add_ren = user.store.root.prop(PR_ADDITIONAL_REN_ENTRYIDS).value
            add_ren[4] = binascii.unhexlify(tmp.entryid)
            user.store.root.create_prop(PR_ADDITIONAL_REN_ENTRYIDS, add_ren)

        if options.safe and not options.create:
            print('\n\nEntryid of old {} folder :{}\nNew name is:{}'.format(oldname.decode('utf-8'),
                                                                            oldid, newname.decode('utf-8')))


if __name__ == "__main__":
    main()
