#!/usr/bin/env python3

from __future__ import with_statement
from collections import Counter
from tok import Tokenizer

import configs
import os
from io import open


def _hash(key, size):
    u"""TODO: This does not belong here. Move to hashtable.py"""
    assert(type(key) == unicode)
    s = 0
    for c in key:
        s = (s * 19) + ord(c)
    return s % size


class Retriever(object):

    def __init__(self, path):
        self._dict = os.path.join(path, u'dict')
        self._post = os.path.join(path, u'post')

    def top(self, query, num):
        tok = Tokenizer()
        tok.tokenize(query)

        acc = Counter()
        for token in tok._counter:
            dict_entry = self.dict_entry(token)
            print token, dict_entry
            if not dict_entry:
                continue
            post_entries = self.post_entries(dict_entry[1], dict_entry[2])
            # Adjust weights so that we don't open files multiple times in
            # cases of repeated tokens. (e.g: dog cat dog cat dog)
            for docid in post_entries:
                post_entries[docid] *= tok._counter[token]
            acc.update(post_entries)
        return acc.most_common(num), len(acc)

    def dict_entry(self, query):
        with open(self._dict, u'r') as f:
            rec_size = 3 + sum(configs.default_indexer[u'dict_rec'])
            file_size = os.path.getsize(self._dict)
            lines = file_size // rec_size
            index = _hash(query, lines)
            k = configs.default_indexer[u'dict_rec'][0] // 2

            entry = [u'', u'', u'']
            while entry and index < lines:
                if len(query) <= k*2 and entry[0] == query:
                    break
                if (len(query) > k*2 and query[:k] == entry[0][:k]
                    and query[-k:] == entry[0][-k:]):
                    break
                f.seek(rec_size * index)
                entry = f.read(rec_size).split()
                index += 1
            if entry:
                return (entry[0], int(entry[1]), int(entry[2]))

    def post_entries(self, num_docs, pos):
        with open(self._post, u'r') as f:
            post_size = 2 + sum(configs.default_indexer[u'post_rec'])
            posts = {}
            for i in xrange(num_docs):
                f.seek(post_size * (pos + i))
                entry = f.read(post_size).split()
                posts[int(entry[0])] = int(entry[1])
            return posts


if __name__ == u'__main__':
    import argparse
    p = argparse.ArgumentParser(
            description=u'Retrieves top N results for the given query.')
    p.add_argument(u'-q', u'--query', required=True)
    p.add_argument(u'-p', u'--path', required=True)
    p.add_argument(u'-n', u'--number', type=int, default=10)
    args = p.parse_args()

    retriever = Retriever(args.path)
    ranks = retriever.top(args.query, args.number)
    with open(os.path.join(args.path, u'map')) as f:
        map_rec = configs.default_indexer[u'map_rec']
        for rank in ranks:
            f.seek(rank[0] * (map_rec + 1))
            print f.read(map_rec), rank
