import ir
import os
import json
import logging
import webapp2

from ir.retrieve import Retriever
from webapp2_extras import jinja2


# Default jinja2 configs.
jinja2.default_config['template_path'] = 'views'


class HomeHandler(webapp2.RequestHandler):

    def index(self):
        self.render('index.html', {})

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render(self, template, context):
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)


class ApiHandler(webapp2.RequestHandler):

    # Inverted files directory.
    inv_path = 'files'

    def files(self):
        """Returns the list of all indexed files.

        Note: Disable this API if the list becomes too big.
        """
        response = {}
        with open(os.path.join(self.inv_path, 'map'), 'r') as f:
                response['urls'] = f.read().splitlines()
        self.write(response)

    def retrieve(self):
        """Retrieve (aka query) API.

        Note: All the logic should not really happen in the
        controller. Since there is only one API right now, yolo?
        """
        query = self.request.get('query', '')
        num = int(self.request.get('num', 10))
        response = {
                'total': 0,
                'query': query,
                'ranks': [],
        }
        retriever = Retriever(self.inv_path)
        ranks, total = retriever.top(query, num)
        response['total'] = total
        with open(os.path.join(self.inv_path, 'map'), 'r') as mapf, open(os.path.join(self.inv_path, 'titles'), 'r') as titlef:
            map_rec = ir.configs.default_indexer['map_rec']
            tit_rec = ir.configs.default_indexer['title_rec']
            # rank = (doc_id, weight)
            for rank in ranks:
                mapf.seek(rank[0] * (map_rec + 1))
                titlef.seek(rank[0] * (tit_rec + 1))
                datum = {
                        'doc_url': mapf.read(map_rec),
                        'doc_title': titlef.read(tit_rec),
                        'doc_weight': rank[1],
                        }
                response['ranks'].append(datum)
        self.write(response)

    def write(self, obj):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(obj))
