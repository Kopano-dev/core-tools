delete-search-folders.py
========================

## Usage

#### Remove all search folder for all users
```python
python3 delete-search-folders.py --days 0
```

#### Keep saved search folder
```python
python3 delete-search-folders.py --days 0 --keep-saved
```

#### Delete search folder per user
```python
python3 delete-search-folders.py -u username --days 0
```