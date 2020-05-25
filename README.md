# btree
B-Tree implementation with pure Python by Forrest Zhang (Forrest@263.net)

## Features
* Pure Python
* No additional module requires
* Allow more items with same key (FIFO)
    * new item with same key will be placed at right side
    * early inserted item will be deleted firstly
* Binary range search for the items with same key
* list-like items management (Get item(s) by subscription __[]__):
    * btree[3]: get the 4th item
    * btree[20:10:-1]: get slice of items and in reversed order
    * del btree[3]: delete the 4th item
* Traverse the btree by using __in__ keyword, e.g. "for item in btree"
* Inherited class btree_debug provides rich debug informations:
    * Dump the full tree in text
    * Check node item/children numbers and key orders in tree

## API
* constants:
    * BTREE_MIN_DEGREE_MIN = 2
    * BTREE_MIN_DEGREE_DEFAULT = 1023

* class btree_item:
    * member: bt_key
    * def \_\_init\_\_(self, bt_key):

* class btree_kv(btree_item):
    * member: value
    * def \_\_init\_\_(self, key, value):

* class btree_items(list):  # internal use
    * def key_range_start(self, key, right:int=None) -> int:
    * def key_range_end(self, key) -> int:
    * def key_range(self, key) -> int, int:

* class btree:
    * operator: in
    * operator: []
    * operator: += []
    * def \_\_init\_\_(self, min_degree: int=BTREE_MIN_DEGREE_DEFAULT):
    * def traverse(self, callback=None, cb_data=None):
    * def search(self, key) -> [btree_item]:
    * def insert(self, item:btree_item):
    * def insert_kv(self, key, value) -> btree_kv:
    * def delete(self, key, item:btree_item=None) -> None or btree_item:
    * def delete_all(self, key) -> [btree_item]:


# Test
It has been tested with Python 3.8.2/Windows 64bit.

See the bottom of btree.py for the test cases, and test log in btree.log
