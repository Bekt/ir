#!/usr/bin/env python3
u"""
This is a hash table implementation that performs linear probing
in case of a collision.

Usage:
    # Approximate size should be known upfront.
    ht = Hashtable(size=10)

    # Insert.
    # Keys are strings only, while values can be anything.
    ht.insert('a', 2) # same as ht['a'] = 2
    ht['b'] = 'hello'
    ht['c'] = [10, 20, 30]

    # Retrieve.
    ht.get('a') # 2
    ht['a'] # 2
    ht['c'] # [10, 20, 30]

    # Iterate.
    for entry in ht._table:
        if not entry:
            print('This spot is empty.')
        else:
            key, value = entry
            print('key=%s, value=%s' % (key, str(value)))

Future enhancements:
    -make iteratable using __iter__() and next()
    -implement update and delete methods
    -make resizeable (don't rely on initial size)
"""

__author__ = u'Kanat Bektemirov'
__credits__ = [u'Susan Gauch']


class Hashtable(object):

    def __init__(self, size):
        self._size = size * 3
        # Items are stored in _table as (key, value) tuple.
        self._table = [None] * self._size
        self.used = 0
        self.collisions = 0
        self.lookups = 0

    def __len__(self):
        return self.used

    def __setitem__(self, key, value):
        self.insert(key, value)

    def insert(self, key, value):
        ind = self.index(key)
        # If not already in the table, insert it.
        if self._table[ind] == None:
            self._table[ind] = (key, value)
            self.used += 1
        # Else do nothing.

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key):
        ind = index(key)
        self.lookups += 1
        ent = self._table[ind]
        if ent:
            return ent[1]

    def index(self, key):
        assert(type(key) == unicode)
        s = 0
        for c in key:
            s = (s * 19) + ord(c)
        ind = s % self._size
        while self._table[ind] != None and self._table[ind][0] != key:
            ind = (ind + 1) % self._size
            self.collisions += 1
        return ind
