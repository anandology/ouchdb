import json
import web
import os

from webapp import app, engine
from version import VERSION

class NotFound(web.HTTPError):
    def __init__(self, data):
        web.HTTPError.__init__(self, '404 Object Not Found', {}, json.dumps(data))

class PreconditionFailed(web.HTTPError):
    def __init__(self, data):
        web.HTTPError.__init__(self, '412 Precondition Failed', {}, json.dumps(data))

class Created(web.HTTPError):
    def __init__(self, data):
        web.HTTPError.__init__(self, '201 Created', {}, json.dumps(data))

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
    path = "/([^_/][^/]*)"
    
    def GET(self, name):
        db = engine.get_database(name)

        web.header("Content-Type", "text/plain;charset=utf-8")
        if db:
            return json.dumps(db.info())
        else:
            raise NotFound({"error":"not_found","reason":"no_db_file"})

    def PUT(self, name):
        web.header("Content-Type", "text/plain;charset=utf-8")

        db = engine.get_database(name)
        if db is None:
            engine.create_database(name)
            raise Created({"ok": True})
        else:
            raise PreconditionFailed({"error": "file_exists", "reason": "The database could not be created, the file already exists."})

    def DELETE(self, name):
        web.header("Content-Type", "text/plain;charset=utf-8")

        if engine.delete_database(name):
            return json.dumps({"ok": True})
        else:
            raise NotFound({"error":"not_found","reason":"no_db_file"})

class all_docs(app.page):
    path = "/([^_/][^/]*)/_all_docs"

    def GET(self, dbname):
        db = engine.get_database(dbname)
        if db:
            web.header("Content-Type", "text/plain;charset=utf-8")
            return '{"total_rows":0,"offset":0,"rows":[]}'
        else:
            raise NotFound({"error":"not_found","reason":"no_db_file"})