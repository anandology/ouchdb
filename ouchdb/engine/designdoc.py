from collections import defaultdict
import json
import logging
from types import FunctionType
import hashlib

from . import errors, view

logger = logging.getLogger("ouchdb.designdoc")

class DesignDoc(dict):
    def __init__(self, database, data):
        dict.__init__(self, data)
        self.database = database
        self.function_cache = defaultdict(dict)
        
    def update(self, stale="not-ok"):
        """Updates all views in this design document if stale != "ok".
        
        Also makes sure the tables for storing view results are created.
        """
        engine = self.database.engine
        db = self.database.db
        
        table = self.get_table()
        if not engine.has_table(table):
            engine.create_view_table(table)
            
        for dbrow in self.database.get_docs_since(self.last_update_seq):
            seq = dbrow.seq
            logger.debug("updating %s for seq %s; doc=%s", self["_id"], seq, dbrow.doc)            
            rows = []
            for view, docid, key, value in self.map(dbrow.doc):
                row = dict(view=view, docid=docid, key=key, value=value, seq=seq)
                rows.append(row)
                
            # if the map function doesn't return any rows, store a placeholder
            # this required because we are currently using view rows to find the last_update_seq.
            if not rows:
                row = dict(view=None, docid=docid, key=None, value=None, seq=seq)
                rows.append(row)
            db.multiple_insert(table, rows)
    
    @property
    def last_update_seq(self):
        """Returns the sequence of last updated document.
        """
        db = self.database.db
        d = db.select(self.get_table(), what="seq", order="id desc", limit=1)
        try:
            return d[0].seq
        except IndexError:
            return 0
    
    def get_table(self):
        """Returns the name of the sql database table used to store views of this design document."""
        jsontext = json.dumps(self, sort_keys=True)
        md5 = hashlib.md5(jsontext).hexdigest()
        return "design_%s_%s" % (self.database.name, md5)
        
    def get_view(self, name):
        """Returns the view object with the given name if exists, None otherwise.
        """
        if name in self.get("views", {}):
            return view.View(self, name)
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
    