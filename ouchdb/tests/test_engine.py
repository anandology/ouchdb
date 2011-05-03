from .. import engine
import web

class TestEngine:
    def setup_method(self, m):
        self.engine = engine.MemoryEngine()
    
    def test_init(self):
        print self.engine._list_tables()
        self.engine.list_databases() == []
        
    def test_create_database(self):
        assert self.engine.create_database("foo") is True
        assert self.engine.list_databases() == ["foo"]

        assert self.engine.create_database("foo") is False
        assert self.engine.list_databases() == ["foo"]

    def test_delete_database(self):
        assert self.engine.delete_database("foo") is False
        
        self.engine.create_database("foo")
        assert self.engine.list_databases() == ["foo"]

        assert self.engine.delete_database("foo") is True
        assert self.engine.list_databases() == []

        assert self.engine.delete_database("foo") is False
        