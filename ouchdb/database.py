import web
import json

from .webapp import app, engine
from . import http
from .engine import Conflict

class all_docs(app.page):
    path = "/([^_/][^/]*)/_all_docs"

    def GET(self, dbname):
        db = engine.get_database(dbname)
        if db:
            web.header("Content-Type", "text/plain;charset=utf-8")
            # TODO: Implement real all docs
            return '{"total_rows":0,"offset":0,"rows":[]}'
        else:
            raise http.NotFound({"error": "not_found", "reason": "no_db_file"})

class document(app.page):
    path = "/([^_/][^/]*)/([^_/][^/]*)"

    def GET(self, dbname, docid):
        db = engine.get_database(dbname)
        doc = db.get(docid)
        if doc:
            web.header("Content-Type", "text/plain;charset=utf-8")
            return json.dumps(doc)
        else:
            raise http.NotFound({"error": "not_found", "reason": "missing"})
            
    def PUT(self, dbname, docid):
        db = engine.get_database(dbname)
        if not db:
            raise http.NotFound({"error": "not_found", "reason": "no_db_file"})
        
        data = json.loads(web.data())
        data['_id'] = docid
        
        try:
            _id, _rev = db.put(data)
        except Conflict:
            raise http.Conflict({"error": "conflict", "reason": "Document update conflict."})
        
        return json.dumps({"ok": True, "id": _id, "rev": _rev})