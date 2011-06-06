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
        
    def test_delete(self):
        id, rev = self.db.put({"_id": "foo", "x": 1})
        self.db.delete("foo", rev=rev)
        
        assert self.db.get("foo") == {"_id": "foo", "_rev": "2", "_deleted": True}
        
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
        
    def test_all_docs(self):
        view = self.db.view("_all_docs")
        assert view.query() == {"total_rows": 0, "offset": 0, "rows": []}
        
        self.db.put({"_id": "foo", "x": 1})
        assert view.query() == {"total_rows": 0, "offset": 0, "rows": [
            {"id": "foo", "key": "foo", "value": {"rev": "1"}}
        ]}
