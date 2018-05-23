try:
    import kopano
except ImportError:
    import zarafa as kopano
import sys
import binascii
from MAPI.Util import *
import uuid

def opt_args():
    parser = kopano.parser('skpcfm')
    parser.add_option("--user", dest="user", action="store", help="Run script for user")
    parser.add_option("--create", dest="create", action="store", help="create folder")
    parser.add_option("--systemfolder", dest="systemfolder", action="store",
                      help="available: calendar, contacts, drafts, journal, notes, outbox, sentmail, task, wastebasket")
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
        print 'Please use:\n %s --user <username>  ' % (sys.argv[0])
        sys.exit(1)

    user = kopano.Server(options).user(options.user)
    print user
    whitelist = ['calendar', 'contacts', 'drafts', 'journal', 'notes', 'outbox', 'sentmail', 'task',
                 'wastebasket']
    if options.systemfolder in whitelist:

        if not options.create:
            oldfolder = getattr(user.store, options.systemfolder)
            oldname = oldfolder.name
            oldid = oldfolder.entryid

        # create new sent items box
        if options.create:
            name = options.create
        else:
            name = uuid.uuid4()
        try:
            print 'create tmp folder', name.decode('utf-8')
            tmp = user.store.subtree.create_folder(name.decode('utf-8'))
        except MAPIErrorCollision:
            print '%s already exist' % name.decode('utf-8')
            sys.exit(1)

        if not options.create:
            # move all item to tmp folder
            print 'copy items from old', options.systemfolder
            user.store.subtree.copy(oldfolder.items(), tmp)
            # delete old box

            if not options.safe:
                print 'Delete %s folder' % options.systemfolder
                getattr(user.store, options.systemfolder).delete(getattr(user.store, options.systemfolder))
            else:
                newname = uuid.uuid4()
                print 'change the name of the old %s folder to %s' % (options.systemfolder, newname.decode('utf-8'))
                getattr(user.store, options.systemfolder).mapiobj.SetProps([SPropValue(PR_DISPLAY_NAME, newname.decode('utf-8'))])
                getattr(user.store, options.systemfolder).mapiobj.SaveChanges(KEEP_OPEN_READWRITE)


            print 'change %s to %s' % (tmp.name, oldname)
            tmp.mapiobj.SetProps([SPropValue(PR_DISPLAY_NAME, oldname)])
            tmp.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)
        # promote tmp file to  sytemfolders
        storeid = {"sentmail": PR_IPM_SENTMAIL_ENTRYID,
                   "outbox": PR_IPM_OUTBOX_ENTRYID,
                   "wastebasket": PR_IPM_WASTEBASKET_ENTRYID}

        rootid = {"calendar": PR_IPM_APPOINTMENT_ENTRYID,
                  "contacts": PR_IPM_CONTACT_ENTRYID,
                  "drafts": PR_IPM_DRAFTS_ENTRYID,
                  "journal": PR_IPM_JOURNAL_ENTRYID,
                  "notes": PR_IPM_NOTE_ENTRYID,
                  "tasks": PR_IPM_TASK_ENTRYID}

        print 'Promote new folder to be a system folder'
        if options.systemfolder in storeid:
            user.store.mapiobj.SetProps(
                [SPropValue(storeid.get(options.systemfolder), binascii.unhexlify(tmp.entryid))])
            user.store.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)
        if options.systemfolder in rootid:
            user.store.root.mapiobj.SetProps(
                [SPropValue(rootid.get(options.systemfolder), binascii.unhexlify(tmp.entryid))])
            user.store.root.mapiobj.SaveChanges(KEEP_OPEN_READWRITE)

        if options.safe and not options.create:
            print '\n\nEntryid of old %s folder :%s\nNew name is:%s' % (oldname.decode('utf-8'), oldid, newname.decode('utf-8'))


if __name__ == "__main__":
    main()