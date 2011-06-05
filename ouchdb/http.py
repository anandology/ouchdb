"""HTTP Error codes.
"""
import web
import urlparse
import json

class Created(web.HTTPError):
    def __init__(self, location, data):
        location = urlparse.urljoin(web.ctx.path, location)
        if location.startswith('/'):
            location = web.ctx.home + location
        headers = {
            "Location": location
        }
        web.HTTPError.__init__(self, '201 Created', headers=headers, data=json.dumps(data))


class NotFound(web.HTTPError):
    def __init__(self, data):
        web.HTTPError.__init__(self, '404 Object Not Found', headers={}, data=json.dumps(data))


class Conflict(web.HTTPError):
    def __init__(self, data):
        web.HTTPError.__init__(self, '409 Conflict', headers={}, data=json.dumps(data))


class PreconditionFailed(web.HTTPError):
    def __init__(self, data):
        HTTPError.__init__(self, '412 Precondition Failed', headers={}, data=json.dumps(data))
