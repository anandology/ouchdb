import web

from webapp import app, engine

class all_docs(app.page):
    path = "/([^_/][^/]*)/_all_docs"

    def GET(self, dbname):
        db = engine.get_database(dbname)
        if db:
            web.header("Content-Type", "text/plain;charset=utf-8")
            return '{"total_rows":0,"offset":0,"rows":[]}'
        else:
            raise NotFound({"error":"not_found","reason":"no_db_file"})
            
