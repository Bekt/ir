import configs
import string

from bs4 import BeautifulSoup
from collections import Counter


class Tokenizer(object):
    """Text tokenizer."""

    # Maps uppercase to lowercase, and deletes any punctuation.
    trans = str.maketrans(string.ascii_uppercase,
                          string.ascii_lowercase,
                          string.punctuation + string.digits)

    def __init__(self, config=configs.default_tokenizer, path=None):
        self._counter = Counter()
        self._config = config
        self.title = None

    def tokenize_html(self, path):
        """Tokenizes the contents of the given HTML file.
        Uses bs4 with lxml for HTML parsing.
        - Strips out script, style, and head tags.
        - Ignores the comments.
        - Removes non-UTF8 characters.
        - Lowercases everything.
        - Removes any punctuation."""
        with open(path, errors='ignore') as f:
            soup = BeautifulSoup(f, 'lxml')
            if soup.title:
                self.title = soup.title.text
            junk = ['head', 'script', 'style']
            for e in soup(junk):
                e.decompose()
            text = soup.get_text(separator=' ')
            self.tokenize(text)
            if self._config['index_urls']:
                self.tokenize_href(soup)

    def tokenize_href(self, soup):
        """Tokenizes the 'href' attribute of all a tags."""
        for a in soup.find_all('a'):
            href = a.attrs.get('href', '')
            # Absolute URLs only.
            if (href.startswith('//') or
                href.startswith('http://') or
                href.startswith('https://')):
                self.tokenize(href)

    def tokenize(self, text):
        """Splits the given text on whitespace and updates the counter.
        The text is first converted to ascii characters only.
        """
        # Ignore non-ASCII characters.
        text = ''.join(c for c in text if ord(c) > 31 and ord(c) < 127)
        text = text.translate(Tokenizer.trans)
        tokens = [t for t in text.split() 
                  if len(t) >= self._config['min_len']
                  and t not in self._config['stopwords']]
        self._counter.update(tokens)
