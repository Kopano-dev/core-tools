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

* [python3-kopano](https://download.kopano.io/supported/core:/final/)
* [tabulate](https://pypi.org/project/tabulate/)
* [binascii](https://docs.python.org/3/library/binascii.html)


## Usage

#### list rules

    python kopano-rules --user <username> --list

#### enable, disable or delete rule
    python kopano-rules.py --user <username> --rule <number> --state enable
    python kopano-rules.py --user <username> --rule <number> --state disable
    python kopano-rules.py --user <username> --rule <number> --state delete

#### create rule
    python kopano-rules.py --user <username> --create <rulename> --conditions* "<conditions>" --actions "<actions>" --exceptions "<exceptions>"*
\* conditions or exceptions is required or both:w


Conditions, actions and exceptions layout is > message:variables

#### Import rule from exchange
This is tested with the following exchange command
    
    Get-Mailbox; $mbox | Foreach { Get-InboxRule -Mailbox $_.DistinguishedName } | ConvertTo-Json
To import

    python kopano-rules.py --import /path/to/json-file

To enable ldap searches for converting the legacyExchangeDN use the config option
    
    python kopano-rules.py --import /path/to/json-file --ldap-config config.py

example ldap config file 
    
    URL = 'ldap://x.x.x.x:389'
    BINDDN = "example\Administrator"
    PASSWORD = "Password"
    BASEDN = "DC=example,DC=lan"   

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
* mark-as-read  (not supported by core yet)
* mark-as-junk
* mark-as-importance (Low, Normal or High)

\* for more addresses use , (user@kopano.com,user2@kopano.com)

\*\* when using multiple words use , to seperate them (hello,world,how are you)

\*\*\* foldername,username. When using a subfolder(mainfolder/subfolder), username is only nessecary when you want to copy/move the message to an other user.


### Example's

##### Create rule with one condition
     python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com" --actions "forward-to:user2@kopano.com"


##### Create rule with multiple conditions
     python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com" --conditions "importance:low" --actions "forward-to:user2@kopano.com"

#### Create rule with multiple actions
    python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com" --actions "forward-to:user2@kopano.com" --actions "copy-to:Inbox/kopano,user2"

#### Create rule with multiple actions conditions and  exceptions
    python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com" --conditions "has-attachment" --exceptions "received-date:01-01-2015,01-01-2017" --exceptions" sensitivity:personal" --actions "forward-to:user2@kopano.com" --actions "copy-to:Inbox/kopano,user2"

#### Create rule and stop processing further rules on the message 
    python kopano-rules.py --user user1 --create firstrule --conditions "received-from:user3@kopano.com" --actions "forward-to:user2@kopano.com" --stop-processing


### Known issue's
* message-size and name-in-to are not working at the moment
* list issues with name-in-cc and  name-in-to
* sensitivity  'normal' is not selectable in webapp
* mark-as-read is not supported yet (should be in KC 8.7)