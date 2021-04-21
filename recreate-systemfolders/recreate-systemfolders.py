import kopano
import sys
import binascii
from MAPI.Tags import (
    PR_IPM_SENTMAIL_ENTRYID, PR_IPM_OUTBOX_ENTRYID,
    PR_IPM_WASTEBASKET_ENTRYID, PR_IPM_APPOINTMENT_ENTRYID,
    PR_IPM_CONTACT_ENTRYID, PR_IPM_DRAFTS_ENTRYID, PR_IPM_JOURNAL_ENTRYID,
    PR_IPM_NOTE_ENTRYID, PR_IPM_TASK_ENTRYID, PR_ADDITIONAL_REN_ENTRYIDS
    )
import locale
import gettext

def opt_args():
    parser = kopano.parser('skpcfmUP')
    parser.add_option("--user", dest="user", action="store", help="Run script for user")
    parser.add_option("--lang", dest="lang", action="store", default="en_GB", help="use locale (e.g. nl_NL.UTF-8) automatically rename the folder")
    parser.add_option("--list", dest="list", action="store_true", help="List broken folders")
    parser.add_option("--auto-fix", dest="auto_fix", action="store_true", help="automatically check for broken systemfolder and  fix them")

    parser.add_option("--systemfolder", dest="systemfolder", action="store",
                      help="available: calendar, contacts, drafts, journal, notes, outbox, sentmail, task, wastebasket, junk")    
                      
    return parser.parse_args()

def translate(lang):
    if 'en_gb' in lang.lower():
        trans = {"sentmail": "Sent Items",
                 "outbox": "Outbox",
                 "wastebasket": "Deleted Items",
                 "inbox": "Inbox",
                 "calendar": "Calendar",
                 "contacts": "Contacts",
                 "suggested_contacts": "Suggested Contacts",
                 "drafts": "Drafts",
                 "journal": "Journal",
                 "notes": "Notes",
                 "tasks": "Tasks",
                 "rss": "RSS Feeds",
                 "junk": "Junk E-mail"}
    else:
        try:
            locale.setlocale(locale.LC_ALL, lang)
        except locale.Error:
            print('Error: {} Is not a language pack or is not installed'.format(lang))
            sys.exit(1)

        encoding = locale.getlocale()[1]

        if "UTF-8" not in encoding and "UTF8" not in encoding:
            print('Error: Locale "{}" is in "{}" not in UTF-8,'
                  'please select an appropriate UTF-8 locale.'.format(lang, encoding))
            sys.exit(1)
        try:
            t = gettext.translation('kopano', "/usr/share/locale", languages=[locale.getlocale()[0]])
            _ = t.gettext
        except (ValueError, IOError):
            print('Error: kopano is not translated in {}'.format(lang))
            sys.exit(1)

        trans = {"sentmail": _("Sent Items"),
                 "outbox": _("Outbox"),
                 "wastebasket": _("Deleted Items"),
                 "inbox": _("Inbox"),
                 "calendar": _("Calendar"),
                 "contacts": _("Contacts"),
                 "suggested_contacts": _("Suggested Contacts"),
                 "drafts": _("Drafts"),
                 "journal": _("Journal"),
                 "notes": _("Notes"),
                 "tasks": _("Tasks"),
                 "rss": _("RSS Feeds"),
                 "junk": _("Junk E-mail")}
    return trans

def fix_system_folder(trans, user, foldername):
    storeid = {"sentmail": PR_IPM_SENTMAIL_ENTRYID,
                "outbox": PR_IPM_OUTBOX_ENTRYID,
                "wastebasket": PR_IPM_WASTEBASKET_ENTRYID}

    rootid = {"calendar": PR_IPM_APPOINTMENT_ENTRYID,
            "contacts": PR_IPM_CONTACT_ENTRYID,
            "drafts": PR_IPM_DRAFTS_ENTRYID,
            "journal": PR_IPM_JOURNAL_ENTRYID,
            "notes": PR_IPM_NOTE_ENTRYID,
            "tasks": PR_IPM_TASK_ENTRYID}

    folder = user.store.create_folder(trans.get(foldername.lower()))

    if storeid.get(foldername):
        print("Changing folder '{}' to systemfolder for '{}'".format(folder.name, foldername))
        user.store.create_prop(storeid.get(foldername), binascii.unhexlify(folder.entryid))
    elif rootid.get(foldername):
        print("Changing folder {} to systemfolder for {}".format(folder.name, foldername))
        user.store.root.create_prop(rootid.get(foldername), binascii.unhexlify(folder.entryid))
    elif foldername.lower() == 'junk':
        print("Changing folder {} to systemfolder for {}".format(folder.name, foldername))
        add_ren = user.store.root.prop(PR_ADDITIONAL_REN_ENTRYIDS).value
        add_ren[4] = binascii.unhexlify(folder.entryid)
        user.store.root.create_prop(PR_ADDITIONAL_REN_ENTRYIDS, add_ren)
    else:
        print("system folder not known")

def check_for_broken_folders(trans, user, autofix=False):
    if not user.calendar.name:
        print("Broken calendar folder")
        if autofix:
            fix_system_folder(trans, user, "calendar")
    if not user.contacts.name:
        print("Broken contacts folder")
        if autofix:
            fix_system_folder(trans, user, "contacts")
    if not user.drafts.name:
        print("Broken drafts folder")
        if autofix:
            fix_system_folder(trans, user, "drafts")
    if not user.journal.name:
        print("Broken journal folder")
        if autofix:
            fix_system_folder(trans, user, "journal")
    if not user.junk.name:
        print("Broken junk folder")
        if autofix:
            fix_system_folder(trans, user, "junk")
    if not user.notes.name:
        print("Broken notes folder")
        if autofix:
            fix_system_folder(trans, user, "notes")
    if not user.outbox.name:
        print("Broken outbox folder")
        if autofix:
            fix_system_folder(trans, user, "outbox")
    if not user.sentmail.name:
        print("Broken sentmail folder")
        if autofix:
            fix_system_folder(trans, user, "sentmail")
    if not user.tasks.name:
        print("Broken tasks folder")
        if autofix:
            fix_system_folder(trans, user, "tasks")
    if not user.wastebasket.name:
        print("Broken wastebasket folder")
        if autofix:
            fix_system_folder(trans, user, "wastebasket")

def main():
    options, args  = opt_args()
    trans = translate(options.lang)
    if not options.user or (not options.systemfolder and not options.list and not options.auto_fix):
        print('Please use:\n {} --user=username  --systemfolder=foldername (e.g. calendar, contacts, drafts, journal, notes, outbox, sentmail, task, wastebasket, junk)'.format(sys.argv[0]))
        sys.exit(1)
    user = kopano.Server(options).user(options.user)
    if options.list or options.auto_fix:
        check_for_broken_folders(trans, user, options.auto_fix)
    else:
       fix_system_folder(trans, user, options.systemfolder)    

if __name__ == "__main__":
    main()
