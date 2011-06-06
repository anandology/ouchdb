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

import json
import web
import os

from .webapp import app, engine
from .version import VERSION
from .engine import Conflict, generate_uuid
from . import http

class ouchdb(app.page):
    path = "/"
    
    def GET(self):
        web.header("Content-Type", "text/plain;charset=utf-8")
        d = {"ouchdb": "Welcome", "version": VERSION}
        return json.dumps(d)

class all_dbs(app.page):
    path = "/_all_dbs"
    
    def GET(self):
        web.header("Content-Type", "text/plain;charset=utf-8")
        dbs = engine.list_databases()
        return json.dumps(dbs)
        
class session(app.page):
    path = "/_session"
    
    def GET(self):
        return '{"ok":true,"userCtx":{"name":null,"roles":["_admin"]},"info":{"authentication_db":"_users","authentication_handlers":["oauth","cookie","default"],"authenticated":"default"}}'

class _uuids(app.page):
    path = "/_uuids"

    def GET(self):
        web.header("Content-Type", "text/plain;charset=utf-8")
        try:
            i = web.input(count=1)
            count = int(i.count)
        except ValueError:
            return '{"error":"unknown_error","reason":"badarg"}'

        uuids = [generate_uuid() for i in range(count)]
        return json.dumps({"uuids": uuids})

class _utils(app.page):
    path = "/_utils"
    def GET(self):
        raise web.redirect("/_utils/")

class utils(app.page):
    path = "/_utils/(.*)"
    
    def GET(self, name):
        if not name:
            name = "index.html"
        
        path = os.path.join("static", name)
        if os.path.exists(path):
            return open(path).read()
        else:
            return web.notfound("")
            
class database(app.page):
    path = "/([^_/][^/]*)/?"
    
    def GET(self, name):
        db = engine.get_database(name)

        web.header("Content-Type", "text/plain;charset=utf-8")
        if db:
            return json.dumps(db.info())
        else:
            raise http.NotFound({"error":"not_found","reason":"no_db_file"})
            
    def POST(self, name):
        db = engine.get_database(name)
        if not db:
            raise http.NotFound({"error": "not_found", "reason": "no_db_file"})

        data = json.loads(web.data())
        try:
            _id, _rev = db.put(data)
        except Conflict:
            raise http.Conflict({"error": "conflict", "reason": "Document update conflict."})
        
        return json.dumps({"ok": True, "id": _id, "rev": _rev})

    def PUT(self, name):
        web.header("Content-Type", "text/plain;charset=utf-8")

        db = engine.get_database(name)
        if db is None:
            engine.create_database(name)
            raise http.Created("/" + name, {"ok": True})
        else:
            raise http.PreconditionFailed({"error": "file_exists", "reason": "The database could not be created, the file already exists."})

    def DELETE(self, name):
        web.header("Content-Type", "text/plain;charset=utf-8")

        if engine.delete_database(name):
            return json.dumps({"ok": True})
        else:
            raise http.NotFound({"error":"not_found","reason":"no_db_file"})

class config(app.page):
    """Dummy config"""
    
    path = "/_config/.*"
    
    def GET(self):
        web.header("Content-Type", "text/plain;charset=utf-8")        
        return '{}'
        
class active_tasks(app.page):
    path = "/_active_tasks"
    
    def GET(self):
        web.header("Content-Type", "text/plain;charset=utf-8")        
        return '[]'
        
class session(app.page):
    path = "/_session"
    
    def GET(self):
        web.header("Content-Type", "text/plain;charset=utf-8")        
        return '{"ok":true}'
        