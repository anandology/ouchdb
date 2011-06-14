from ..designdoc import DesignDoc
from ..errors import CompileError

import pytest

class TestDesignDoc:
    
    def test_map_with_empty_designdoc(self):
        ddoc = DesignDoc(None, {})
        doc = {}
        assert list(ddoc.map(doc)) == []
    
    def test_map(self):
        ddoc = {
            "views": {
                "foo": {
                    "map": "def f(doc): yield doc['name'], 1"
                }
            }
        }
        ddoc = DesignDoc(None, ddoc)
        
        doc = {"_id": "doc1", "name": "ouchdb"}
        assert list(ddoc.map(doc)) == [
            ("foo", "doc1", "ouchdb", 1)
        ]
        
    def test_map_with_error(self):
        ddoc = {
            "views": {
                "foo": {
                    "map": "x"
                }
            }
        }
        ddoc = DesignDoc(None, ddoc)
        with pytest.raises(CompileError):
            list(ddoc.map({}))
        
    def _get_compile_error(self, code):
        try:
            ddoc = DesignDoc(None, {})
            ddoc._compile(code, fullname="")
        except CompileError, e:
            return e.args[0]
        
    def test_compile_errors(self):
        assert self._get_compile_error("def f(doc): pass") is None
        assert self._get_compile_error("x") == "name 'x' is not defined"
        assert self._get_compile_error("") == "string must eval to a function"
        assert self._get_compile_error("def f(doc): pass\ndef g(doc): pass") == "string must eval to a function"
        
