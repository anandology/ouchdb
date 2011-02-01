"""OuchDB is CouchDB implementation on SQL.
"""

from version import VERSION
from webapp import app

__version__ = VERSION

wsgi = app.wsgifunc()