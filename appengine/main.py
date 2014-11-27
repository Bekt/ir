import webapp2


# Main WSGI app.
app = webapp2.WSGIApplication([
    webapp2.Route(r'/', name='home', methods=['GET'],
                  handler='controllers.HomeHandler:index'),

    webapp2.Route(r'/api/retrieve', name='api_retrieve', methods=['GET'],
                 handler='controllers.ApiHandler:retrieve'),

    webapp2.Route(r'/api/files', name='api_files', methods=['GET'],
                 handler='controllers.ApiHandler:files'),
], debug=True)
