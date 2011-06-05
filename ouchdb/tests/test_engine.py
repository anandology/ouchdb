from .. import engine
import web

def test_engine():
    db = web.database(dbn='sqlite', db=":memory:")
    e = engine.Engine(db)
        
    assert e.list_databases() == []
    assert e.get_database("foo") is None

    e.create_database("foo")
    assert e.list_databases() == ["foo"]
    assert e.get_database("foo") is not None

    e.create_database("bar")
    assert e.list_databases() == ["foo", "bar"]
    assert e.get_database("bar") is not None

    e.delete_database("foo")
    assert e.list_databases() == ["bar"]
    assert e.get_database("foo") is None    
    
class TestDatabase:
    def setup_method(self, method):
        db = web.database(dbn='sqlite', db=":memory:")
        e = engine.Engine(db)
        e.create_database("foo")

        self.db = e.get_database("foo")
        
    def test_put(self):
        id, rev = self.db.put({"_id": "foo", "x": 1})
        assert id == "foo"
        assert rev == "1"
        
        doc = self.db.get("foo")
        assert doc == {
            "_id": "foo", 
            "_rev": "1",
            "x": 1
        }
        
    def test_put_rev(self):
        for i in range(10):
            id, rev = self.db.put({"_id": "foo", "x": i, "_rev": str(i)})
            assert id == "foo"
            assert rev == str(i+1)
            
            id, rev = self.db.put({"_id": "bar", "x": i, "_rev": str(i)})
            assert id == "bar"
            assert rev == str(i+1)

    def test_list(self):
        assert self.db.list() == []