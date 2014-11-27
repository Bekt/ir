"""Various default configs."""

import configparser


cfg = configparser.ConfigParser()
cfg.read('configs.cfg')

def _load_stopwords(path):
    with open(path, 'r') as f:
        return set(f.read().splitlines())


default_tokenizer = {
    'min_len': cfg['Tokenizer'].getint('min_len'),
    'index_urls': cfg['Tokenizer'].getboolean('index_urls'),
    'stopwords': _load_stopwords(cfg['Tokenizer']['stops_path']),
}



default_indexer = {
    'min_frequency': cfg['Indexer'].getint('min_frequency'),
    'max_frequency': cfg['Indexer'].getfloat('max_frequency'),
    'dict_rec': tuple(int(d) for d in cfg['Indexer']['dict_rec'].split(',')),
    'post_rec': tuple(int(d) for d in cfg['Indexer']['post_rec'].split(',')),
    'map_rec': cfg['Indexer'].getint('map_rec'),
    'title_rec': cfg['Indexer'].getint('title_rec'),
}

