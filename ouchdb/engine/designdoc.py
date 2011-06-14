from collections import defaultdict
import json
import logging
from types import FunctionType
import hashlib

from . import errors

logger = logging.getLogger("ouchdb.designdoc")

class DesignDoc(dict):
    def __init__(self, database, *a, **kw):
        dict.__init__(self, *a, **kw)
        self.database = database
        self.function_cache = defaultdict(dict)
        
    def get_table(self):
        """Returns the name of the sql database table used to store views of this design document."""
        jsontext = json.dumps(self, sort_keys=True)
        md5 = hashlib.md5(jsontext).hexdigest()
        return "design_%s_%s" % (self.database.name, md5)
        
    def get_view(self, name):
        """Returns the view object with the given name if exists, None otherwise.
        """
        if name in self.get("views", {}):
            return View(self, name)
        else:
            raise errors.NotFound("missing_named_view")
        
    def get_map_function(self, view):
        return self.get_view_function(view, "map")
                
    def get_view_function(self, view, name="map"):
        cache = self.function_cache[view]
        if name in cache:
            return cache[name]
        else:
            code = self.get("views", {}).get(view, {}).get(name, None)
            if code:
                cache[name] = self._compile(code, "%s/%s" % (view, name))
                return cache[name]
            else:
                return None
                
    def _compile(self, code, fullname):
        # Adopted from couchdb-python
        _globals = {}
        try:
            exec code in {"log": self._log}, _globals
        except Exception, e:
            logger.error("%s - failed to compile", fullname, exc_info=True)
            raise errors.CompileError(e.args[0])
            
        if len(_globals) != 1:
            logger.error("%s - expected one value globals, found %s", fullname, _globals.keys())
            raise errors.CompileError("string must eval to a function")
        function = _globals.values()[0]
        if type(function) is not FunctionType:
            logger.error("%s - expected function, found %s", fullname, type(function))
            raise errors.CompileError("string must eval to a function")
        return function
        
    def _log(self, message):
        if not isinstance(message, basestring):
            message = json.encode(message)
        logger.log(message)
        
    def map(self, doc):
        """Returns (viewname, docid, key, value) for each key-value pair emitted by the view.
        """
        for view in self.get("views", {}):
            _map = self.get_map_function(view)
            for key, value in _map(doc):
                yield view, doc['_id'], key, value       
    