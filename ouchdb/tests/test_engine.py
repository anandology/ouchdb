from .. import engine
import web

class TestEngine:
    def setup_method(self, m):
        db = web.database(dbn="sqlite", db=":memory:")
        self.engine = engine.Engine(db)
    
    def test_init(self):
        print self.engine._list_tables()
        self.engine.list_databases() == []
        
    def test_create_database(self):
        self.engine.create_database("foo")
        self.engine.list_databases() == ["foo"]
        