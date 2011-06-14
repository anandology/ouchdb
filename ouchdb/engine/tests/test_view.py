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
        
        