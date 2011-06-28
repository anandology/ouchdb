from .. import view
import simplejson
    
class TestViewResponse:
    def test_json(self):
        d = {"total_rows": 10, "offset": 0, "rows": []}
        x = view.ViewResponse(**d)
        json = "".join(x.to_json())
        assert simplejson.loads(json) == d
        
        d = {"total_rows": 10, "offset": 0, "rows": [1, 2]}
        x = view.ViewResponse(**d)
        json = "".join(x.to_json())
        assert json == (
            '{"total_rows":10,"offset":0,"rows": [\n' +
            '1,\n' +
            '2\n' +
            ']}')
        
    def test_infinite(self):
        def integers():
            i = 1
            while True:
                yield i
                i = i+1
        
        x = view.ViewResponse(total_rows=1000, offset=0, rows=integers())
        jsoniter = x.to_json()
        
        
    def test_lookahead(self):
        x = view.ViewResponse(0, 0, [])
        assert list(x.lookahead([])) == []
        assert list(x.lookahead([1])) == [(1, None)] 
        assert list(x.lookahead([1, 2])) == [(1, 2), (2, None)]
        assert list(x.lookahead([1, 2, 3, 4, 5])) == [(1, 2), (2, 3), (3, 4), (4, 5), (5, None)]
        
        assert list(x.lookahead([1], end="END")) == [(1, 'END')] 
        