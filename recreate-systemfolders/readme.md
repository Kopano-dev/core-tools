# recreate-systemfolders

Script to re-create system folders. 

**Note: Inbox can't be re-created with this script**

Supported folders
- Calendar
- Contacts
- Drafts
- Journal
- Notes
- Outbox
- Sent Items
- Deleted Items
- Junk E-mail

**Usage**
```python
python3 recreate-systemfolders.py --user username --systemfolder systemfoldername**
```

If store is using a different locale than language use 
```python
python3 recreate-systemfolders.py --user username --systemfolder systemfoldername** --lang nl_NL.utf-8
```

To list all systemfolder that are broken
```python
python3 recreate-systemfolders.py --user username --list
```

To auto fix the sytemfolders that are broken, `--lang` should be added if you use a different locale for the store.
```
python3 recreate-systemfolders.py --user username --auto-fix
```

List of system folder parameter names:

- calendar
- contacts
- drafts
- journal
- notes
- outbox
- sentmail
- tasks
- wastebasket
- junk
