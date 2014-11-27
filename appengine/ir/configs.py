u"""Various default configs."""

from __future__ import with_statement
import ConfigParser
import os
from io import open

base = 'ir'

cfg = ConfigParser.ConfigParser()
cfg.read(os.path.join(base, u'configs.cfg'))


def _load_stopwords(path):
    with open(os.path.join(base, path), u'r') as f:
        return set(f.read().splitlines())


default_tokenizer = {
    u'min_len': cfg.getint('Tokenizer', 'min_len'),
    u'index_urls': cfg.getboolean('Tokenizer', 'index_urls'),
    u'stopwords': _load_stopwords(cfg.get(u'Tokenizer', u'stops_path')),
}



default_indexer = {
    u'min_frequency': cfg.getint(u'Indexer', u'min_frequency'),
    u'max_frequency': cfg.getfloat(u'Indexer', u'max_frequency'),
    u'dict_rec': tuple(int(d) for d in cfg.get(u'Indexer', u'dict_rec').split(u',')),
    u'post_rec': tuple(int(d) for d in cfg.get(u'Indexer', u'post_rec').split(u',')),
    u'map_rec': cfg.getint(u'Indexer', u'map_rec'),
    u'title_rec': cfg.getint(u'Indexer', u'title_rec'),
}

