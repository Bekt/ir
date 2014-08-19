#!/usr/bin/env python3

"""
CSCE 5013 Information Retrieval - Fall 2013.
HW1: Tokenizer.
Description and requirements:
    http://www.csce.uark.edu/~sgauch/5533/F13/index.html
TODO: What to do with title and metadata tags?
"""

import glob
import os
import string
import sys

from bs4 import BeautifulSoup
from collections import Counter

# Used for str.translate().
# Maps uppercase to lowercase, and deletes any punctuation.
trans = str.maketrans(string.ascii_uppercase,
                      string.ascii_lowercase, string.punctuation)


def print_usage():
    msg = """Usage: \n
    {} input_dir output_dir \n
input_dir: the input directory with HTML files to tokenize.
output_dir: the output directory to store the tokens.""".format(sys.argv[0])
    print(msg)


def run(inp, out):
    if not os.path.exists(out):
        os.makedirs(out)
    tok = Tokenizer(inp, out)
    html_files = inp + '/*.html'
    for path in glob.iglob(html_files):
        tok.process(path)


class Tokenizer(object):

    def __init__(self, inp_dir, out_dir):
        self._inp_dir = inp_dir
        self._out_dir = out_dir

    def get_clean_text(self, path):
        """Returns the content of the given file with
        HTML tags stripped, punctuations removed, and lowercased.

        TODO: consider using global soup and soup.clear() in here."""
        global trans
        with open(path) as f:
            soup = BeautifulSoup(f)
            text = soup.get_text(separator=' ')
            return text.translate(trans)

    def write_tokens(self, path, tokens):
        out_path = os.path.join(
            self._out_dir, os.path.basename(path) + '.tokens')
        with open(out_path, 'w') as f:
            f.write(os.linesep.join(tokens))

    def process(self, path):
        text = self.get_clean_text(path)
        self.write_tokens(path, text.split())


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)
    run(sys.argv[1], sys.argv[2])
