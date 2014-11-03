#!/usr/bin/env python3
"""
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
import configs
import glob
import math
import os
import time

from collections import defaultdict
from hashtable import Hashtable
from tok import Tokenizer


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

    def run(self):
        if not os.path.exists(self._out):
            os.makedirs(self._out)
        html_files = self._inp + '/*.html'
        for ind, path in enumerate(glob.iglob(html_files)):
            if self._max and ind >= self._max:
                break
            self._filenames.append(os.path.basename(path))
            self.process(ind, path)
        self.write_mapfile()
        self.write_dictfile()
        self.write_postfile()
        print(len(self.ht))
        print(len(self._post_entries))

    def process(self, ind, path):
        tok = Tokenizer()
        tok.tokenize_html(path)
        for token, freq in tok._counter.items():
            # Normalize by unique tokens.
            self.globalht[token].append([ind, freq / len(tok._counter)])

    def write_mapfile(self, filename='map'):
        out_path = os.path.join(self._out, filename)
        map_rec = self._config['map_rec']
        with open(out_path, 'w') as f:
            f.write(os.linesep.join(
                [name.ljust(map_rec) for name in self._filenames]))

    def write_dictfile(self, filename='dict'):
        docs = len(self._filenames)
        max_docs = docs * self._config['max_frequency']
        # Remove min and max frequency words.
        for token in list(self.globalht.keys()):
            num_docs = len(self.globalht[token])
            if (num_docs < self._config['min_frequency']
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
        dict_rec = self._config['dict_rec']
        trunc = dict_rec[0] // 2
        with open(out_path, 'w') as f:
            for d in self._dict_entries:
                if not d:
                    d = ['', '', '']
                num_docs = str(d[1]).ljust(dict_rec[1])
                start_pos = str(d[2]).ljust(dict_rec[2])
                # Truncate first and last `trunc characters.
                if len(d[0]) <= dict_rec[0]:
                    token = d[0].ljust(dict_rec[0])
                else:
                    token = d[0][:trunc] + d[0][-trunc:]
                f.write(token + ' ' + num_docs + ' ' + start_pos + os.linesep)

    def write_postfile(self, filename='post'):
        out_path = os.path.join(self._out, filename)
        post_rec = self._config['post_rec']
        with open(out_path, 'w') as f:
            f.write(os.linesep.join(
                [str(post[0]).ljust(post_rec[0]) + ' ' +
                 str(post[1]).ljust(post_rec[1])
                 for post in self._post_entries]))


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(
            description='Builds an index for the document collection.')
    p.add_argument('-i', '--input-dir', required=True)
    p.add_argument('-o', '--output-dir', required=True)
    p.add_argument('-n', '--number-files', type=int,
            help='Maximum number of files to process in the input directory.')
    args = p.parse_args()

    indtoc = IndexToc(args.input_dir, args.output_dir, args.number_files)
    indtoc.run()
