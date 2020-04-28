kopano-cleanup
==============

The following scripts allow you to automatically delete or archive all items older than x days in a users **Junk E-mail** and **Deleted Items** folder.

Parameters
```python
  -h, --help                         show this help message and exit
  -c FILE, --config=FILE             load settings from FILE
  -s SOCKET, --server-socket=SOCKET  connect to server SOCKET
  -k FILE, --ssl-key=FILE            SSL key file
  -p PASS, --ssl-pass=PASS           SSL key password
  -U NAME, --auth-user=NAME          login as user
  -P PASS, --auth-pass=PASS          login with password
  -f NAME, --folder=NAME             Specify folder
  -m, --modify                       enable database modification
  --user=USER                        Run script for user
  --public                           Run script for Public store
  --wastebasket                      Run cleanup script for the wastebasket
                                     folder
  --archive=ARCHIVE                  instead of removing items archive them
                                     into this folder
  --junk                             Run cleanup script for the junk folder
  --force                            Force items without date to be removed
  --all                              Run over all folders
  --recursive                        Run over the subfolders (Only works if -f
                                     is being used)
  --days=DAYS                        Delete older then x days
  --verbose                          Verbose mode
  --dry-run                          Run script in dry mode
  --empty                            Empty the complete folder (only works
                                     with --wastebasket or --junk)
  --progressbar                      Show progressbar
```

## Usage
delete
```python
python cleanup.py --user username --junk --wastebasket --days days
```

archive
```python
python cleanup.py --user username --junk --wastebasket --days days  --archive foldername

```

