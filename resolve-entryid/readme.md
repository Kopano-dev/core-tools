# resolve-entryid.py
Tries to resolve which item a given entryid is, optionally dumping to an eml as a file, or deleting the item.
This is not multi server aware.

## Help
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