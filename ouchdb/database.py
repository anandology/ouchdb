# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import web
import json

from .webapp import app, engine
from . import http
from .engine import errors

def get_db(name):
    db = engine.get_database(name)
    if db:
        return db
    else:
        raise http.NotFound({"error": "not_found", "reason": "no_db_file"})


class document(app.page):
    path = "/([^_/][^/]*)/([^_/][^/]*)"

    def GET(self, dbname, docid):
        db = get_db(dbname)
        doc = db.get(docid)
        if doc:
            web.header("Content-Type", "text/plain;charset=utf-8")
            if doc.get("_deleted"):
                raise http.NotFound({"error": "not_found", "reason": "deleted"})
            return json.dumps(doc)
        else:
            raise http.NotFound({"error": "not_found", "reason": "missing"})
            
    def PUT(self, dbname, docid):
        db = get_db(dbname)
        
        data = json.loads(web.data())
        data['_id'] = docid
        
        try:
            _id, _rev = db.put(data)
        except errors.Conflict:
            raise http.Conflict({"error": "conflict", "reason": "Document update conflict."})
        
        return json.dumps({"ok": True, "id": _id, "rev": _rev})
        
    def DELETE(self, dbname, docid):
        db = get_db(dbname)
        
        try:
            i = web.input(rev=None)
            _id, _rev = db.delete(docid, i.rev)
        except errors.Conflict:
            raise http.Conflict({"error": "conflict", "reason": "Document update conflict."})
        
        return json.dumps({"ok": True, "id": _id, "rev": _rev})

class view(app.page):
    path = "/([^_/][^/]*)/(_design/[^_/][^/]*)/_view/([^_/][^/]*)"
    
    def GET(self, dbname, designdoc, viewname=None):
        web.header("Content-Type", "text/plain;charset=utf-8")
        db = get_db(dbname)
        
        try:
            view = self.get_view(db, designdoc, viewname)
        except errors.NotFound, e:
            raise http.NotFound(e.data)
        
        kwargs = self.process_input(web.input())
        view_result = view.query(**kwargs)
        return view_result.to_json()
        
    def get_view(self, db, designdoc, viewname):
        ddoc = db.get_design_doc(designdoc)
        return ddoc.get_view(viewname)
            
    def process_input(self, input):
        d = {}

        for k in ["key", "startkey", "endkey"]:
            if k in input:
                d[k] = json.loads(input[k])

        for k in ["include_docs", "inclusive_end", "reduce", "descending"]:
            if k in input:
                d[k] = (input[k] == "true")
        
        for k in ["skip", "limit"]:
            if k in input:
                d[k] = int(input[k])
        
        for k in ["stale"]:
            if k in input:
                d[k] = input[k]

        return d

class _all_docs(view):
    path = "/([^_/][^/]*)/(_all_docs)"

    def get_view(self, db, designdoc, viewname):
        return db.get_all_docs_view()
    
class db_compact(app.page):
    path = "/([^_/][^/]*)/_compact"
    
    def POST(self, dbname):
        db = get_db(dbname)
        
        web.header("Content-Type", "text/plain;charset=utf-8")
        return json.dumps({"ok": True})


class view_compact(app.page):
    path = "/([^_/][^/]*)/_compact/(.*)"

    def POST(self, dbname, designdoc):
        db = get_db(dbname)
        
        web.header("Content-Type", "text/plain;charset=utf-8")
        return json.dumps({"ok": True})


class view_cleanup(app.page):
    path = "/([^_/][^/]*)/_view_cleanup"

    def POST(self, dbname):
        db = get_db(dbname)
        
        web.header("Content-Type", "text/plain;charset=utf-8")
        return json.dumps({"ok": True})
