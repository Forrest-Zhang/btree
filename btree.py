#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '1.0.0'

__all__ = [
    'btree_item',
    'btree_node',
    'btree',
]

__author__ = 'Forrest Zhang <forrest@263.net>'

'''
Reference:
    * http://staff.ustc.edu.cn/~csli/graduate/algorithms/book6/chap19.htm
    * http://www.cs.utexas.edu/users/djimenez/utsa/cs3343/lecture16.html
    * http://www.cs.utexas.edu/users/djimenez/utsa/cs3343/lecture17.html
    * https://www.geeksforgeeks.org/delete-operation-in-b-tree

In 1972, B-Tree was developed by Bayer and McCreight with the name:
    Height Balanced m-way Search Tree.

Later it was named as B-Tree.

B-Tree is a self-balanced search tree in which every node contains multiple
keys and has more than two children.

The number of keys in a node and number of children for a node depends
on the minimum degree t (t>=2) of B-Tree. The Order of the B-Tree is m=2*t

B-Tree of Order m has the following properties:
    #1 - All leaf nodes must be at same level.
    #2 - All nodes except root must have at least t-1 keys
         and maximum of 2*t-1 keys.
    #3 - All non leaf nodes except root (i.e. all internal nodes)
         must have at least t children.
    #4 - If the root node is a non leaf node,
         then it must have at least 2 children.
    #5 - A non leaf node with n-1 keys must have n number of children.
    #6 - All the key values in a node must be in Ascending Order.

For example, B-Tree of Order 4 contains a maximum of 3 key values in a node
and maximum of 4 children for a node.

root:          [                  30,                             70,                  ]
internal:  [ 8,         25, ]              [ 40,       50, ]                [ 76,       88, ]
leaf: [1,3,7] [15,21,23] [26,28, ]  [35,38, ] [42,49, ] [56, 67, ]  [71,73,75] [77,85, ] [89,97, ]

=== Search ===
Starts from the root node, and make an n-way decision every time.
Where 'n' is the total number of children the node has.

In a B-Tree, the search operation is performed with O(log n) time complexity.

=== Insert ===
In a B-Tree, a new element must be added only at the leaf node. That means,
the new keyValue is always attached to the leaf node only.

=== Delete ===
Deletion from a B-tree is analogous to insertion but a little more complicated.

'''


class btree_item:

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return f'{self.key}: "{self.value}"'


class btree_node:

    def __init__(self,
                 min_degree: int,
                 items: [btree_item]=None,
                 children: ['btree_node']=None):
        self.min_degree = min_degree
        self.max_degree = 2 * min_degree - 1
        self.items = items or []  # as keys
        self.children: [btree_node] = children or []

        # number of items in the subtree
        n_item = len(self.items)
        for child in self.children:
            n_item += child.n_item
        self.n_item = n_item

    def get_n_item(self):
        n_item = len(self.items)
        for child in self.children:
            n_item += child.get_n_item()
        return n_item

    def get_n_node(self):
        n_node = len(self.children)
        for child in self.children:
            n_node += child.get_n_node()
        return n_node

    def __len__(self):
        return self.n_item

    def getitem(self, pos):
        for i, child in enumerate(self.children):
            if pos < child.n_item:
                return child.getitem(pos)
            pos -= child.n_item + 1
            if pos < 0:
                return self.items[i]

        # must be a leaf node if got here
        return self.items[pos]

    def __getitem__(self, index) -> btree_item or [btree_item]:
        top = self.n_item

        if isinstance(index, int):
            if index >= 0 and index < self.n_item:
                return self.getitem(index)
        elif isinstance(index, slice):
            start, stop, step = index.start, index.stop, index.step

            # set default for start, stop and step
            if stop is None:
                start, stop, step = 0, top, 1
            elif start is None:
                start = 0
            elif step is None:
                step = 1

            if start > 0 and start < top and (
                (step > 0 and stop > start and stop <= top)
                or (step < 0 and stop < start and stop > -2)):
                items = []
                for index in range(start, stop, step):
                    items.append(self.getitem(index))
                return items

        raise IndexError(f'{index} out of range [0, {top})')

    def __iter__(self):
        if self.children:
            yield from self.children[0].__iter__()
        for i, item in enumerate(self.items, 1):
            yield item
            if self.children:
                yield from self.children[i].__iter__()

    def is_full(self):
        return len(self.items) > self.max_degree

    def is_enough(self):
        return len(self.items) >= self.min_degree

    def is_poor(self):
        return len(self.items) < self.min_degree - 1

    def __repr__(self):
        r = f'btree_node[{len(self.items)}]: {[d.key for d in self.items]}'
        if self.children:
            r += f' children# {[len(child.items) for child in self.children]}'
        return r

    def check(self, stats, path: [int]) -> int:  # return height to leaf node
        if self.is_full():
            stats.error(f'node is full {self} @ {path}')
        elif self.is_poor() and path:
            stats.error(f'node is poor {self} @ {path}')
        if self.n_item != self.get_n_item():
            stats.error(f'node numbers incorrect #item: {self.n_item}'
                        f' vs. {self.get_n_item()} @ {path}')

        if self.children:
            if len(self.children) < 2:
                stats.error(f'less than 2 children {self} @ {path}')
            if len(self.items) + 1 != len(self.children):
                stats.error(f'items and child count error {self} @ {path}')

            height = self.children[0].check(stats, path + [0])
            for i, item in enumerate(self.items, 1):
                stats.check_order(item.key)

                _h = self.children[i].check(stats, path + [i])
                if _h != height:
                    stats.error(f'height different at {i}: {_h} vs. {height}')
            return height + 1
        else:
            for item in self.items:
                stats.check_order(item.key)
            return 0

    def traverse(self, path: [int], callback, cb_data=None):
        if self.children:
            for i, child in enumerate(self.children):
                ret = child.traverse(path + [i], callback, cb_data)
                if ret:
                    return ret

                if i < len(self.items):
                    # stop traverse() if callback return something
                    ret = callback(path + [i], self.items[i], cb_data)
                    if ret:
                        return ret
        else:
            for i, item in enumerate(self.items):
                ret = callback(path + [i], item, cb_data)
                if ret:
                    return ret

    def search(self, matches:[btree_item], key):
        for i, item in enumerate(self.items):
            # current key is too small, skip recursive
            if item.key < key:
                continue

            # try the child even if current key is bigger
            if self.children:
                self.children[i].search(matches, key)

            # current key is bigger, no more
            if  item.key > key:
                return  # don't search rest

            # pretty match
            matches += [item]

        # search in last child
        if self.children:
            self.children[-1].search(matches, key)

    def split(self) -> (btree_item, 'btree_node'):
        # right node takes right half of items and children
        n = self.min_degree

        # it's OK to "slice" or "del" on empty list
        right = btree_node(n, self.items[n:], self.children[n:])
        del self.items[n:]  # remove right part items
        del self.children[n:]  # remove right part of children

        self.n_item -= right.n_item + 1
        return self.items.pop(n - 1), right

    def insert(self, key, item: btree_item) -> bool:
        i = 0
        for it in self.items:
            # pass over the item which key is same
            # if key is same, new one is on the right (FIFO)
            if it.key > key:
                break
            i += 1

        self.n_item += 1  # each node on the path increased 1 item
        if self.children:
            if self.children[i].insert(key, item):
                # child is full, split it
                midlle, right = self.children[i].split()
                self.items.insert(i, midlle)
                self.children.insert(i + 1, right)
                return self.is_full()
        else:
            # always insert new item into a leaf node
            self.items.insert(i, item)
            return self.is_full()

    def _merge(self, index:int):
        # append items[index] and right child's items/children to left child
        left, right = self.children[index], self.children[index + 1]

        left.items.append(self.items.pop(index))  # move items[index] to left
        left.items += right.items  # and all items of right
        left.children += right.children  # and its children
        del self.children[index + 1]  # remove right child from self

        left.n_item += right.n_item + 1  # + right's items and 1 item of self

    def _get_child(self, index:int) -> 'btree_node':
        '''
        if child has not enough items (< minimum degree),
        and delete() remove one more item from it,
        then its items will be less than minimum degree.
        therefore, borrow an item and child from left/right sibling,
        or merge it with left/right sibling, make sure the items are enough.
        '''
        child = self.children[index]
        if child.is_enough():
            return child

        left_index = index - 1  # first child has no left sibling
        if index > 0 and self.children[left_index].is_enough():
            # borrow from left sibling
            left = self.children[left_index]
            child.items.insert(0, self.items[left_index])
            self.items[left_index] = left.items.pop(-1)
            if left.children:
                subtree = left.children.pop(-1)
                child.children.insert(0, subtree)
                left.n_item -= subtree.n_item
                child.n_item += subtree.n_item
            left.n_item -= 1
            child.n_item += 1
        elif index < len(self.items):  # last child has no right sibling
            right = self.children[index + 1]
            if right.is_enough():
                # borrow from the right sibling
                child.items.append(self.items[index])
                self.items[index] = right.items.pop(0)
                if right.children:
                    subtree = right.children.pop(0)
                    child.children.append(subtree)
                    right.n_item -= subtree.n_item
                    child.n_item += subtree.n_item
                right.n_item -= 1
                child.n_item += 1
            else:
                # merge the right sibling into current child
                self._merge(index)
        else:
            # if no right sibling, it must have a left sibling
            # because minimum degree >= 2.
            # merge current child into left sibling
            self._merge(left_index)
            return self.children[left_index]
        return child

    def delete(self, key, item:btree_item=None) -> None or btree_item:
        # leaf node
        if not self.children:
            for index, it in enumerate(self.items):
                if it == item or not item and it.key == key:
                    self.n_item -= 1
                    return self.items.pop(index)
            return

        # internal node
        for index, it in enumerate(self.items):
            if it.key < key:
                continue

            # found it in left child?
            found = self._get_child(index).delete(key, item)
            if found:
                self.n_item -= 1  # every node lost 1 item on the path
                return found

            # found it in items?
            if it == item or not item and it.key == key:

                def move_out_item(subtree, which):
                    '''
                    which = -1, ask for the predecessor item
                    which = 0, ask for the successor item
                    '''
                    node = subtree
                    while node.children:
                        node = node.children[which]
                    neigh = node.items[which]
                    return subtree.delete(neigh.key, neigh)

                left = self.children[index]
                if left.is_enough():
                    # replace it with predecessor item
                    self.items[index] = move_out_item(left, -1)
                else:
                    right = self.children[index + 1]
                    if right.is_enough():
                        # replace it with successor item
                        self.items[index] = move_out_item(right, 0)
                    else:
                        # merge it, then delete it
                        self._merge(index)
                        left.delete(key, it)
                self.n_item -= 1
                return it

            if it.key > key:
                return  # don't need to try the rest items and children

        # try last child
        index = len(self.items)
        found = self._get_child(index).delete(key, item)
        if found:
            self.n_item -= 1  # every node lost 1 item on the path
            return found


class btree:
    DUMP_INDENT = '    '

    def __init__(self, min_degree: int):
        if min_degree < 2:
            min_degree = 2
        self.height = 0
        self.root = btree_node(min_degree)

    # support sequence operation: btree[index]
    def __len__(self):
        return self.root.__len__()

    def __getitem__(self, index):
        return self.root.__getitem__(index)

    def __delitem__(self, index) -> btree_item:
        self.delete(None, self[index])

    def __iter__(self):
        return self.root.__iter__()

    def n_node(self):
        return self.root.get_n_node()

    def dump(self):
        pass

    def traverse(self, callback=None, cb_data=None):
        '''
        callback should take three arguments:
            def traverse_callback(path, item: btree_item, cb_data)
        if something returned by traverse_callback, tests to be True,
        then traverse will be terminated, and return with it.

        if callback is None, dump the whole b-tree.
        '''
        if not callable(callback):

            def callback(path: [int], item: btree_item, _cb_data):
                # lead item marks with "*"
                depth, lead = len(path) - 1, ' ' if path[-1] else '*'
                print(self.DUMP_INDENT * depth + f'{lead}{item}')

        return self.root.traverse([], callback, cb_data)

    def search(self, key) -> [btree_item]:
        items = []
        self.root.search(items, key)
        return items

    def insert_item(self, item:btree_item):
        if self.root.insert(item.key, item):
            middle, right = self.root.split()
            self.root = btree_node(right.min_degree,
                                   [middle], [self.root, right])
            self.height += 1

    def insert(self, key, value) -> btree_item:
        item = btree_item(key, value)
        self.insert_item(item)
        return item

    def delete(self, key, item:btree_item=None) -> None or btree_item:
        if isinstance(item, btree_item):
            key = item.key  # avoid consistent issue

        removed = self.root.delete(key, item)

        # tree may be changed even nothing's removed
        if not self.root.items and self.root.children:
            self.height -= 1
            self.root = self.root.children[0]

        return removed

    def delete_all(self, key) -> [btree_item]:
        items = []
        while True:
            # item = None, remove the first item with key
            removed = self.delete(key)
            if removed is None:
                break  # no more item with key

            items.append(removed)
        return items


if "__main__" == __name__:

    import logging

    try:
        from cam_dict.log import logger_conf, logger_setlevel
        logger = logger_conf('btree', rotating_files=1)
        logger_setlevel(logger, logging.INFO)
    except:
        logger = logging
        logging.basicConfig(level=logging.INFO)

    class btree_debug(btree):

        DEBUG_NONE = 0
        DEBUG_DUMP = 1
        DEBUG_SEARCH = 2
        DEBUG_INSERT = 4
        DEBUG_DELETE = 8
        DEBUG_ALL = 15

        def __init__(self, min_degree: int, dbg_flags=DEBUG_ALL):
            super().__init__(min_degree)
            self.dbg_flags = dbg_flags
            self.dump()

        def check(self):

            class btree_stats:

                def __init__(self):
                    self.size = 0
                    self.errors = 0
                    self.min = None
                    self.max = None

                def __repr__(self):
                    return (f'size: {self.size}, '
                            f'error: {self.errors}, '
                            f'key: {self.min} - {self.max}')

                def error(self, msg):
                    self.errors += 1
                    logger.error(msg)

                def check_order(self, key):
                    if key is None:
                        self.error(f'invalid key {key}')
                        return
                    self.size += 1
                    if self.min is None:
                        self.min = key
                        self.max = key
                    elif key < self.min:
                        self.error(f'min key error: {key} < {self.min}')
                    elif key < self.max:
                        self.error(f'max key error: {key} < {self.max}')
                    elif key > self.max:
                        self.max = key

            stats = btree_stats()
            height = self.root.check(stats, [])
            if stats.errors \
                or height != self.height or stats.size != len(self):
                logger.error(f'height: {height}/{self.height} '
                             f'size: {stats.size}/{len(self)} '
                             f'errors: {stats.errors} '
                             f'key range: {stats.min} - {stats.max}')
                self.dump()

        def dump(self):
            if self.dbg_flags & self.DEBUG_DUMP:
                t = self.root.min_degree
                logger.info(f'B-Tree Order: {2 * t}, '
                            f'minimum degree: {t}, '
                            f'#items/node: {t-1} - {2 * t - 1}, '
                            # f'#children/node: {t} - {2 * t}, '
                            f'height: {self.height}, '
                            f'items: {len(self)}'
                            )

                def dump_item(path: [int], item: btree_item, _cb_data):
                    # lead item marks with "*"
                    depth, lead = len(path) - 1, ' ' if path[-1] else '*'
                    logger.info(self.DUMP_INDENT * depth + f'{lead}{item}')

                self.traverse(dump_item)
                logger.info('---------------')

        def search(self, key) -> [btree_item]:
            items = super().search(key)
            if (self.dbg_flags & self.DEBUG_SEARCH):
                logger.info(f'... search(key: {key}) = #{len(items)}: {items}')
            return items

        def insert_item(self, item:btree_item):
            if (self.dbg_flags & self.DEBUG_INSERT):
                logger.info(f'+++ insert(item: {item})')
            super().insert_item(item)
            self.check()

        def insert(self, key, value) -> btree_item:
            if (self.dbg_flags & self.DEBUG_INSERT):
                logger.info(f'+++ insert(key: {key}, value: {value})')
            item = super().insert(key, value)
            self.check()
            return item

        def delete(self, key, item:btree_item=None) -> None or btree_item:
            removed = super().delete(key, item)
            if (self.dbg_flags & self.DEBUG_DELETE):
                logger.info(
                    f'--- delete(key: {key}, item: {item}) = {removed}')
            self.check()
            return removed

        def delete_all(self, key) -> [btree_item]:
            if (self.dbg_flags & self.DEBUG_DELETE):
                logger.info(f'--- delete_all(key: {key})')
            items = super().delete_all(key)
            if (self.dbg_flags & self.DEBUG_DELETE):
                logger.info(f'    delete_all removed #{len(items)}: {items}')
            self.check()
            return items

    def new_btree(min_degree, _dbg_flags=btree_debug.DEBUG_ALL):
        # return btree(min_degree)  # it's pretty fast without debug message,
        return btree_debug(min_degree, _dbg_flags)

    #
    # test case for traverse() and key order
    #
    logger.info('=== insert, traverse and key order test ===')
    btr = new_btree(2)

    import string
    from random import random

    # build a string that contains ASCII letters and digits
    original = string.digits + string.ascii_letters
    original = list(original)
    original.sort()
    original = ''.join(original)

    logger.info(f'randomly insert each letter of "{original}" into a btree')
    seq, lst = 0, list(original)
    while lst:
        letter = lst.pop(int(random() * len(lst)))
        btr.insert(letter, seq)
        seq += 1
    btr.dump()

    # get them back
    get_back = []

    def traverse_cb(_path, item, data):
        data += item.key

    btr.traverse(traverse_cb, get_back)
    get_back = ''.join(get_back)

    logger.info(f'sorted letters:   {original}')
    logger.info(f'letters in btree: {get_back}')
    if original == get_back:
        logger.info('letter order in btree is correct')
    else:
        logger.error('letter order in btree is wrong')

    logger.info('=== iterator and sequence test ===')
    logger.info('get items by indices, like: "for item in btree[35:9:-1]"')
    for it in btr[35:9:-1]:
        logger.info(f'{it}')

    logger.info(f'btree[10]: {btr[10]}')
    logger.info(f'del btree[10]')
    del btr[10]
    logger.info(f'btree[10]: {btr[10]}')

    logger.info(f'"btree[20] in btr" is {btr[20] in btr}')

    #
    # test case for search(), delete()
    #
    logger.info('=== search() and delete() test ===')
    btr = new_btree(2)
    for key in range(14):
        btr.insert(key, f'{key}')

    for i in range(1, 8):
        btr.insert_item(btree_item(4, f'4.{i}'))

    btr.dump()

    btr.search(4)
    btr.search(40)

    item5 = btr.delete(5)
    btr.dump()

    logger.info('what happens if delete a non-exist key?')
    btr.delete(5)
    btr.dump()

    logger.info('what happens if delete a removed item?')
    btr.root.delete(5, item5)
    btr.dump()

    logger.info('delete the 4th item which key is "4"')
    if btr.delete(4, btr.search(4)[3]):
        btr.dump()

    logger.info('delete all rest items which key is "4"')
    if btr.delete_all(4):
        btr.dump()

    logger.info('delete key in reversed(range(15))')
    for key in reversed(range(15)):
        if btr.delete(key):
            btr.dump()

    #
    # test case for another minimum degree and duplicated key
    #
    btr = new_btree(4, btree_debug.DEBUG_DUMP)

    max_test_key = 1000
    logger.info(f'insert: "=key=" in range({max_test_key})')
    for key in range(max_test_key):
        btr.insert(key, f'={key}=')

    logger.info(f'delete: key in range({max_test_key})')
    for key in range(max_test_key):
        btr.delete(key)
    btr.dump()

    logger.info(f'insert: "+key+" in range({max_test_key})')
    for key in range(max_test_key):
        btr.insert(key, f'+{key}+')

    logger.info('insert: "#key###" in reversed(range(100, 200, 2))')
    for key in reversed(range(100, 200, 2)):
        btr.insert(key, f'#{key}###')
    btr.dump()

    logger.info(f'delete: key in reversed(range({max_test_key}))')
    for key in reversed(range(max_test_key)):
        btr.delete(key)
    btr.dump()

    #
    # test case for discontinuous delete()
    #
    logger.info('=== Primary Numbers ^_^ ===')
    btr = new_btree(3, btree_debug.DEBUG_DUMP)

    logger.info(f'insert: "=key=" in range({max_test_key})')
    for key in range(max_test_key):
        btr.insert(key, f'={key}=')

    for index in range(2, max_test_key):
        primary = btr[index].key
        if primary * 2 >= max_test_key:
            break
        r = range(primary * 2, max_test_key, primary)
        if index & 1:
            logger.info(f'delete: key in reversed({r})')
            for key in reversed(r):
                btr.delete(key)
        else:
            logger.info(f'delete: key in {r}')
            for key in r:
                btr.delete(key)

    logger.info('del btree[1]')
    del btr[1]
    logger.info('del btree[0]')
    del btr[0]

    logger.info('remainder items must be primary numbers')
    btr.dump()

    logger.info('test finished')
