#!/usr/bin/env python3
u"""
CSCE 4013 Information Retrieval - Fall 2014.
HW2: Indexing: http://www.csce.uark.edu/~sgauch/4013-IR/F14/hw/hw2.html

After running this program, three files will be generated in the
given output directory:
    -dict: a file containing (term, num_docs, start_loc) tuples in
           local hashtable hash order.
    -post: a file containing (doc_id, tf) tuples that go with `dict.
    -map: a file containing the doc_id => actual filename mapping.

Usage:
    tok_index.py -h
    tok_index.py -i <input_dir> -o <output_dir>
"""
from __future__ import with_statement
from __future__ import division
import configs
import glob
import math
import os
import time

from collections import defaultdict
from hashtable import Hashtable
from tok import Tokenizer
from tok import remove_non_ascii
from io import open


class IndexToc(object):

    def __init__(self, inp_dir, out_dir, max_files,
                 config=configs.default_indexer):
        self.globalht = defaultdict(list)
        self.ht = None
        self._config = config
        self._inp = inp_dir
        self._out = out_dir
        self._max = max_files
        self._dict_entries = []
        self._post_entries = []
        self._filenames = []
        self._titles = []

    def run(self):
        if not os.path.exists(self._out):
            os.makedirs(self._out)
        html_files = self._inp + u'/*.html'
        for ind, path in enumerate(glob.iglob(html_files)):
            if self._max and ind >= self._max:
                break
            self._filenames.append(os.path.basename(path))
            self.process(ind, path)
        self.write_mapfile()
        self.write_titles()
        self.write_dictfile()
        self.write_postfile()
        print len(self.ht)
        print len(self._post_entries)

    def process(self, ind, path):
        tok = Tokenizer()
        tok.tokenize_html(path)
        self._titles.append(tok.title or u'Untitled')
        for token, freq in tok._counter.items():
            # Normalize by unique tokens.
            self.globalht[token].append([ind, freq / len(tok._counter)])

    def write_mapfile(self, filename=u'map'):
        out_path = os.path.join(self._out, filename)
        map_rec = self._config[u'map_rec']
        with open(out_path, u'w') as f:
            f.write(os.linesep.join(
                [name.ljust(map_rec) for name in self._filenames]))

    def write_titles(self, filename=u'titles'):
        out_path = os.path.join(self._out, filename)
        title_rec = self._config[u'title_rec']
        with open(out_path, u'w') as f:
            f.write(os.linesep.join(
                [remove_non_ascii(title.strip()[:title_rec]).ljust(title_rec)
                for title in self._titles]))

    def write_dictfile(self, filename=u'dict'):
        docs = len(self._filenames)
        max_docs = docs * self._config[u'max_frequency']
        # Remove min and max frequency words.
        for token in list(self.globalht.keys()):
            num_docs = len(self.globalht[token])
            if (num_docs < self._config[u'min_frequency']
                or num_docs >= max_docs):
                del self.globalht[token]
        # Convert to this only for the purpose of disk write.
        self.ht = Hashtable(len(self.globalht))
        for token, nodes in self.globalht.items():
            self.ht[token] = nodes
        for pair in self.ht._table:
            entry = None
            if pair:
                token, nodes = pair
                num_docs = len(nodes)
                entry = (token, num_docs, len(self._post_entries))
                idf = math.log(docs / num_docs, 2)
                # post_rec: doc_id, wt * idf * C
                for node in nodes:
                    node[1] = int(node[1] * idf * 100000)
                    self._post_entries.append(node)
            self._dict_entries.append(entry)
        out_path = os.path.join(self._out, filename)
        dict_rec = self._config[u'dict_rec']
        trunc = dict_rec[0] // 2
        with open(out_path, u'w') as f:
            for d in self._dict_entries:
                if not d:
                    d = [u'', u'', u'']
                num_docs = unicode(d[1]).ljust(dict_rec[1])
                start_pos = unicode(d[2]).ljust(dict_rec[2])
                # Truncate first and last `trunc characters.
                if len(d[0]) <= dict_rec[0]:
                    token = d[0].ljust(dict_rec[0])
                else:
                    token = d[0][:trunc] + d[0][-trunc:]
                f.write(token + u' ' + num_docs + u' ' + start_pos + os.linesep)

    def write_postfile(self, filename=u'post'):
        out_path = os.path.join(self._out, filename)
        post_rec = self._config[u'post_rec']
        with open(out_path, u'w') as f:
            f.write(os.linesep.join(
                [unicode(post[0]).ljust(post_rec[0]) + u' ' +
                 unicode(post[1]).ljust(post_rec[1])
                 for post in self._post_entries]))


if __name__ == u'__main__':
    import argparse
    p = argparse.ArgumentParser(
            description=u'Builds an index for the document collection.')
    p.add_argument(u'-i', u'--input-dir', required=True)
    p.add_argument(u'-o', u'--output-dir', required=True)
    p.add_argument(u'-n', u'--number-files', type=int,
            help=u'Maximum number of files to process in the input directory.')
    args = p.parse_args()

    indtoc = IndexToc(args.input_dir, args.output_dir, args.number_files)
    indtoc.run()
