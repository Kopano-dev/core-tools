ipf-imap-to-note.py
=================
Rewrite the folder container_class from 'IPF.Imap' to 'IPF.Note'.

This makes folders imported through PST (Where Outlook was used as an Imap client) visible again.
 

## Usage:
To rewrite all folders with the container_class 'IPF.Imap'
```python
python ipf-imap-to-note.py -u <username> 
```
Test do a test run
```python
python ipf-imap-to-note.py -u <username>  --dry-run
```