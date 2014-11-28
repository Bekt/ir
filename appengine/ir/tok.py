from __future__ import with_statement
import configs
import string

from bs4 import BeautifulSoup
from collections import Counter
from io import open


def remove_non_ascii(text):
    return ''.join(c for c in text if 127 > ord(c) > 31)


class Tokenizer(object):
    u"""Text tokenizer."""

    # Maps uppercase to lowercase, and deletes any punctuation.
    trans = { ord(string.ascii_uppercase[i]) : ord(string.ascii_lowercase[i]) 
              for i in range(26) }
    trans.update({ ord(c): None for c in string.punctuation + string.digits })


    def __init__(self, config=configs.default_tokenizer, path=None):
        self._counter = Counter()
        self._config = config
        self.title = None

    def tokenize_html(self, path):
        u"""Tokenizes the contents of the given HTML file.
        Uses bs4 with lxml for HTML parsing.
        - Strips out script, style, and head tags.
        - Ignores the comments.
        - Removes non-UTF8 characters.
        - Lowercases everything.
        - Removes any punctuation."""
        with open(path, errors=u'ignore') as f:
            soup = BeautifulSoup(f, u'lxml')
            if soup.title:
                self.title = soup.title.text
            junk = [u'head', u'script', u'style']
            for e in soup(junk):
                e.decompose()
            text = soup.get_text(separator=u' ')
            self.tokenize(text)
            if self._config[u'index_urls']:
                self.tokenize_href(soup)

    def tokenize_href(self, soup):
        u"""Tokenizes the 'href' attribute of all a tags."""
        for a in soup.find_all(u'a'):
            href = a.attrs.get(u'href', u'')
            # Absolute URLs only.
            if (href.startswith(u'//') or
                href.startswith(u'http://') or
                href.startswith(u'https://')):
                self.tokenize(href)

    def tokenize(self, text):
        u"""Splits the given text on whitespace and updates the counter.
        The text is first converted to ascii characters only.
        """
        # Ignore non-ASCII characters.
        text = remove_non_ascii(text)
        text = text.translate(Tokenizer.trans)
        tokens = [t for t in text.split() 
                  if len(t) >= self._config[u'min_len']
                  and t not in self._config[u'stopwords']]
        self._counter.update(tokens)
