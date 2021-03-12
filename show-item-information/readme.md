# show-item-information.py

Print item information 

## Help

```
Usage: show-item-information.py [options]

Options:
  -h, --help                         show this help message and exit
  -c FILE, --config=FILE             load settings from FILE
  -s SOCKET, --server-socket=SOCKET  connect to server SOCKET
  -k FILE, --ssl-key=FILE            SSL key file
  -p PASS, --ssl-pass=PASS           SSL key password
  -U NAME, --auth-user=NAME          login as user
  -P PASS, --auth-pass=PASS          login with password
  -u NAME, --user=NAME               Specify user
  -f NAME, --folder=NAME             Specify folder
  -m, --modify                       enable database modification
  -v, --verbose                      enable verbose output
  --search=SEARCH                    string to search for
  --public                           search in public store
```
## Dependencies

kopano-rules depends on a few Python libraries:

* [python3-kopano](https://download.kopano.io/supported/core:/final/)
* [tabulate](https://pypi.org/project/tabulate/)

## Usage:

Search for an item on the global store of a user 
> python3 show-item-information.py -u username  --search "subject to search for" 

Search for an item on the global store of the public store
> python3 show-item-information.py --public  --search "subject to search for" 

Search for an item on a specific folder of the public store
> python3 show-item-information.py --public  -f full/path/of/the/folder  --search "subject to search for" 

Search for an item on a specific folder for multiple users 
> python3 show-item-information.py -u username -u username2  -f full/path/of/the/folder   --search "subject to search for" 


Search for an item in multiple folder for a user  
> python3 show-item-information.py -u username  -f full/path/of/the/folder -f foldername2 --search "subject to search for" 

## Example output
```
python3 show-item-information.py --public  --search "meeting user  
Running script for public store
+--------------------+-----------------+-------------------------------------------+--------------------+---------------------+-----------------+----------------------+
| Subject            | Folder          | Time/Date                                 | Owner              | Created             | Last modified   | Last modified user   |
+====================+=================+===========================================+====================+=====================+=================+======================+
| Test meeting user  | Public Calendar | 2021-03-09 13:00:00 - 2021-03-09 13:30:00 | user               | 2021-03-12 09:50:41 | user2           | 2021-03-12 09:50:41  |
+--------------------+-----------------+-------------------------------------------+--------------------+---------------------+-----------------+----------------------+
```