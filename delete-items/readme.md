delete-items
============

Delete items

## Usage:

Delete all items between a time spane
```python
 python delete-items.py -u <username> --from <YYYY-MM-DD> --until <YYYY-MM-DD>
```

Delete all items with subject
```python
 python delete-items.py -u <username> --subject "subject of the item" 
```

Delete with entryid
```python
 python delete-items.py -u <username> --entryid 000000004A85E36673C749BD83E84022C88DC30901000000050000003874F6C41EDE475B957908F7FFCD907E00000000 
```

Run script without removing anything 
```python
 python delete-items.py -u <username> --subject "subject of the item" --dry-run
```
