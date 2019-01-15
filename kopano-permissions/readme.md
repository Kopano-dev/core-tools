kopano-permissions
============

kopano-permissions is a cli to modify or change user permissions



## Features

kopano-rules supports:

* List permissions per user
* Add new permissions
* Remove user permissions
* Calculate custom permissions
* Add delegate user
* Remove delegate user


## Dependencies

kopano-rules depends on a few Python libraries:

* [python3-kopano](https://download.kopano.io/supported/core:/final/)
* [tabulate](https://pypi.org/project/tabulate/)
* [binascii](https://docs.python.org/3/library/binascii.html)


## Usage

#### list permissions

    kopano-permissions.py --user <username> --list

#### list permissions including 'hidden' folders

    kopano-permissions.py --user <username> --list-all
    
#### list permissions per folder
--folder parameter can be set multiple times 

    kopano-permissions.py --user <username> --list --folder <foldername>
    
#### Add default permission on store 
default permission are norights, readonly, secretary, owner and fullcontrol
    
    kopano-permissions.py --user <username>  --add <usernmae> --permission secretary
    
#### Add default permission on a specific folder

    kopano-permissions.py --user <username>  --add <usernmae> --permission secretary --folder Inbox
    
#### Calculate custom permission

    kopano-permissions.py --calculate
    
    Please select the permissions (1,5,7)
    [1] Create items
    [2] Read items
    [3] Create subfolders
    [4] Folder permissions
    [5] Folder visible
    [6] Edit own items
    [7] Edit all items
    [8] Delete own items
    [9] Delete all items
    1,2,3,4
    Please use the following value for changing the permissions 0x183

#### Add custom permissions

    kopano-permissions.py --user <username>  --add <usernmae> --permission 0x183 

#### Remove permissions
    kopano-permissions.py --user <username>  --remove <usernmae> 
     
#### Set delegate
available flags: 
* --private (delegate can see private items)
* --copy (delegate receives copies of meeting-related messages)
 
    
    kopano-permissions.py --user <username>  --add <usernmae>  --delegate --private --copy
    
#### Remove delegate
Adding one of the flags will only remove that specific permission 

    kopano-permissions.py --user <username>  --remove <usernmae>  --delegate 
