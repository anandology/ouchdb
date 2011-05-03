import web
from engine import Engine

app = web.auto_application()

engine = Engine()

def setup():
    import server
