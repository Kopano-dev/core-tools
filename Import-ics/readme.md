import-ics
==========

The following script allow you to import ics files 

## Usage

For all users:
```python
python3 import-ics.py --all --calendar foldername --import /path/to/ics/file
```
  
For a single user:
```python
python3 import-ics.py --user username --calendar foldername --import /path/to/ics/file
```
Download ics from url 
```python
python3 import-ics.py --user username --calendar foldername --import 'https//example.com/data.ics'

```

Purge folder first 
```python
python3 import-ics.py --user username --calendar foldername --import /path/to/ics/file --purge

```
