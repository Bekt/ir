#!/usr/bin/env python3
"""
CSCE 4013 Information Retrieval - Fall 2014.
HW1: Tokenizer
    http://www.csce.uark.edu/~sgauch/4013-IR/F14/hw/hw1.html

Usage:
    tok_docs.py -h
"""

import glob
import os

from collections import Counter
from tok import Tokenizer


class DocTok(object):

    def __init__(self, inp_dir, out_dir, num):
        # Counter across all documents.
        self._counter = Counter()
        self._inp = inp_dir
        self._out = out_dir
        self._num = num

    def run(self):
        if not os.path.exists(self._out):
            os.makedirs(self._out)
        html_files = self._inp + '/*.html'
        for ind, path in enumerate(glob.iglob(html_files)):
            if self._num and ind > self._num:
                break
            self.process(path)
        self.write_sorted('sorted_tokens', sorted(self._counter.items()))
        self.write_sorted('sorted_freq',
                sorted(self._counter.items(), key=lambda x: x[1], reverse=True))

    def process(self, path):
        tok = Tokenizer()
        tok.tokenize_html(path)
        self._counter.update(tok._counter)
        self.write_tokens(path, tok._counter.keys())

    def write_tokens(self, path, tokens):
        out_path = os.path.join(
            self._out, os.path.basename(path) + '.tokens')
        with open(out_path, 'w') as f:
            f.write(os.linesep.join(tokens))

    def write_sorted(self, filename, tuples):
        out_path = os.path.join(self._out, filename)
        with open(out_path, 'w') as f:
            f.write(os.linesep.join(k + ' ' + str(v) for k, v in tuples))


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(
            description='Tokenize documents in a directory.')
    p.add_argument('-i', '--input-dir', required=True)
    p.add_argument('-o', '--output-dir', required=True)
    p.add_argument('-n', '--number-files',type=int,
            help='Maximum number of files to process in the input directory.')
    args = p.parse_args()

    dt = DocTok(args.input_dir, args.output_dir, args.number_files)
    dt.run()
