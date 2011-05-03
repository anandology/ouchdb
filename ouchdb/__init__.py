"""OuchDB is CouchDB implementation on SQL.
"""

from version import VERSION
import webapp

webapp.setup()

__version__ = VERSION

wsgi = webapp.app.wsgifunc()