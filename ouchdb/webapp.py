import web
web.config.debug = True

from engine import Engine

app = web.auto_application()

db = web.database(dbn="sqlite", db="ouch.db")
engine = Engine(db)

def setup():
    import server
    import database