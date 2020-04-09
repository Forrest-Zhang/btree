# btree-pure-python
B-Tree implementation with pure Python by Forrest Zhang (Forrest@263.net)

## Features
* Pure Python
* No additional module requires
* Allow more items with same key (FIFO)
    * new item with same key will be placed at right side
    * early inserted item will be deleted firstly
* Inherited class btree_debug provides rich debug informations:
    * Dump the full tree in text
    * Check node item/children numbers and key orders in tree

## API
* class btree_item:
    * def __init__(self, key, value):

* class btree:
    * def __init__(self, min_degree: int):
    * def traverse(self, callback=None, cb_data=None):
    * def search(self, key) -> [btree_item]:
    * def insert_item(self, item:btree_item):
    * def insert(self, key, value) -> btree_item:
    * def delete(self, key, item:btree_item=None) -> None or btree_item:
    * def delete_all(self, key) -> [btree_item]:


# Test
It has been tested with Python 3.8.2/Windows 64bit.

See the bottom of btree.py for the test cases, and test log in btree.log
