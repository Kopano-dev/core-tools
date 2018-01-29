fix-received-date
=================

Fix the received date. 

## Usage:
```python
python fix-received-date.py -u <username> 
```
Test run
```python
python fix-received-date.py -u <username>  --dry-run
```

delete-items
============

Delete items  between  given dates.

## Usage:

```python
 python delete-items.py -u <username> --from <YYYY-MM-DD> --until <YYYY-MM-DD>
```


localize-folders
================


The following script allow you to rename the systemfolders to an other language. 



## Usage

For all users:
```python
python localize-folders.py --lang <e.g. nl_NL.UTF-8>
```
  
For a single user:
```python
python localize-folders.py --user <username> --lang <e.g. nl_NL.UTF-8>
```
Switch back to english:
```python
python localize-folders.py --reset
```
kopano-cleanup
==============


The following scripts allow you to automatically delete all items older than x days in a users **Junk E-mail** and **Deleted Items** folder.



## Usage

```python
python cleanup.py --user \<user\> --junk --wastebasket --days \<days\>
```

recreate-systemfolders
======================

Script that can recreate system folder*

## Usage
```python
python recreate-systemfolders --user \<user\> --create <foldername> --systemfolder <systemfoldername**>
```

\* Inbox folder  can't be recreated. 
\*\* Following systemfolders are available  calendar, contacts, drafts, journal, notes, outbox, sentmail, task, wastebasket


show-guid
================


The following script prints the primairy and archive store GUID if exist.  

fix-delegates.py
================

Will recreate the ids for the delegates  in the root store

    python fix-delegates.py --user <username> --modify      - will recreate the ids and create a restore file
    python fix-delegates.py --user <username> --restore     - will restore the file what was create with the modify option

kopano-rules
============

kopano-rules is a cli to modify or change a server side rule


## Features


kopano-rules supports:

* List all rules per user
* Enable/disable rules
* Delete rules
* Create Rules



## Dependencies


kopano-rules depends on a few Python libraries:


* [terminaltables](https://pypi.python.org/pypi/terminaltables)


## Usage


#### list rules

    python kopano-rules --user <username> --list

#### enable, disable or delete rule

    python kopano-rules.py --user <username> --rule <number> --state enable
    python kopano-rules.py --user <username> --rule <number> --state disable
    python kopano-rules.py --user <username> --rule <number> --state delete

#### create rule

    python kopano-rules.py --user <username> --create <rulename> --conditions* "<conditions>" --actions "<actions>" --exceptions "<exceptions>"*


\* conditions or exceptions is required or both

Conditions, actions and exceptions layout is > message:variables

Multiple conditions,  actions  and exceptions must we seperated with ;

##### available options

###### Conditions / exceptions:

* received-from *
* name-in-cc
* name-in-to
* name-in-to-cc
* sent-to *
* importance (Low, Normal or High)
* sensitivity (normal, personal, private or confidential)
* sent-only-to-me
* contain-word-in-body **
* contain-word-in-header **
* contain-word-in-subject **
* contain-word-sender-address  **
* message-size (size in kb)
* meeting-request 
* received-date (dd-mm-yyyy)
* has-attachment

###### Actions:

* forward-to *
* redirect-to *
* forward-as-attachment *
* move-to  ***
* copy-to  ***
* delete


\* for more addresses use , (user@kopano.com,user2@kopano.com)

\*\* when using multiple words use , to seperate them (hello,world,how are you)

\*\*\* foldername,username. When using a subfolder(mainfolder/subfolder), username is only nessecary when you want to copy/move the message to an other user.



### Example's

##### create rule with one condition
     python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com" --actions "forward-to:user2@kopano.com"


##### create rule with multiple conditions
     python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com;importance:low" --actions "forward-to:user2@kopano.com"


#### create rule with multiple actions

    python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com" --actions "forward-to:user2@kopano.com;copy-to:Inbox/kopano,user2"

#### create rule with multiple actions conditions and  exceptions

    python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com;has-attachment" --exceptions "received-date:01-01-2015,01-01-2017;sensitivity:personal" --actions "forward-to:user2@kopano.com;copy-to:Inbox/kopano,user2"



### Known issue's

* message-size and name-in-to  are not working at the moment
* list issues with name-in-cc and  name-in-to
* sensitivity  'normal' is not selectable in webapp

# resolve-entryid.py

Tries to resolve which item a given entryid is, optionally dumping to an eml as a file, or deleting the item.

##
```
Usage: resolve-entryid.py [options]

Options:
  -h, --help                         show this help message and exit
  -s SOCKET, --server-socket=SOCKET  connect to server SOCKET
  -k FILE, --ssl-key=FILE            SSL key file
  -p PASS, --ssl-pass=PASS           SSL key password
  -f NAME, --folder=NAME             Specify folder
  --entryid=ENTRYID                  Entryid to resolve
  --eml                              Write as eml to file
  --delete                           Delete the item from the store
```

## Usage:
    python resolve-entryid.py --entryid 0000000036B232938E34485AB84A848127AB7B1A01000000050000001393248EF62F490A8FF798A73B427BA500000000

## Example output for a calendar item
```
Entryid : 0000000036B232938E34485AB84A848127AB7B1A01000000050000001393248EF62F490A8FF798A73B427BA500000000
Guessed storeid : 36B232938E34485AB84A848127AB7B1A
Store : kopano
User : kopano (Kopano Kokuntu)
Server : Server(default:)
Message_class : IPM.Appointment
Folder : Folder(Calendar)
Subject : Test
Received : None
Stubbed : False
```