### Backup-mapi

Does a backup on MAPI level

### contacts2suggested

Convert contacts to suggested contacts, also possible to convert the sent mail to user to the suggested contacts

### create-ldap-contacts

Create random contacts in the ldap (central lxd ldap can't be used)

### fix-entryid

Fix entryid on mails if the store is hooked on an other usr, or if the users uuid is changed in the ldap

### get_info

Retrieve PR_DISPLAY_TO names. 

### kopano-permissions

New untested kopano permissions script

### NK2-to-suggested-contacts

## Usage

Restore NK2 file

        python NK2-to-suggested-contacts.py --user <username> --file </path/to/NK2/file>


Restore CSV file

        python NK2-to-suggested-contacts.py --user <username> --file </path/to/NK2/file> --csv

## options
* --user

    username on which the restore action takes place
* --file

    NK2 or CSV file that need to be restored
* --csv

    Use a CSV file instead (need to have the headers  (address_type, display_name, email_address))
* --delimiter

    Overwrite the default delimiter ,

### fix-folder-class

Fixes the folder that are missing the container_class property

options
* --list

    list all the folders that are missing the container_class property. A json file is saved so the user can manually fix these fodlers
* --restore

    uses the json file that is created with the --list options to manually fix the folder
    the following folder type's can be used:
    
    * Note  (Mail folder)
    * Appointment (Calendar folder)
    * Stickynote (Notes folder)
    * Contact  (contacts folder)
    * Tasks    (task folder)
* --auto

    Tries to guess the folder type's and if possible fix the folder. 
    It will create a json file if folders can't be fix, the --restore option can be used then 
* --mail 

    Will fix all the broken folder to mail folders