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
* contain-word-sender-address  **
* contain-word-in-subject **
* contain-word-in-body **
* message-size  (size in kb)
* received-date  (dd-mm-yyyy)
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

     python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com;importance:low" --actions "forward-to:user2@kopano.com"

##### create rule with multiple conditions

     python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com" --actions "forward-to:user2@kopano.com"

#### create rule with multiple actions

    python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com" --actions "forward-to:user2@kopano.com;copy-to:Inbox/kopano,user2"

#### create rule with multiple actions conditions and  exceptions

    python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com;has-attachment" --exceptions "received-date:01-01-2015,01-01-2017;sensitivity:personal" --actions "forward-to:user2@kopano.com;copy-to:Inbox/kopano,user2"



### Known issue's

* message-size and name-in-to  are not working at the moment
* list issues with name-in-cc and  name-in-to
* sensitivity  'normal' is not selectable in webapp


