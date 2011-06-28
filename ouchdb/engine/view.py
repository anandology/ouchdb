"""OuchDB views.
"""
import json
import web
import logging

logger = logging.getLogger("ouchdb.view")

class ViewResponse:
    def __init__(self, total_rows, offset, rows):
        self.total_rows = total_rows
        self.offset = offset
        self.rows = rows
        
    def to_json(self):
        """Returns an iterator with JSON.
        """
        try:
            yield '{"total_rows":%d,"offset":%d,"rows": [' % (self.total_rows, self.offset)
            for row, ahead in self.lookahead(self.rows):
                yield "\n"
                yield json.dumps(row, sort_keys=True, separators=(",", ":"))
                if ahead:
                    yield ","
                else:
                    yield "\n"
            yield ']}'
        except:
            import traceback
            traceback.print_exc()
            raise StopIteration
        
    def as_dict(self):
        return {
            "total_rows": self.total_rows,
            "offset": self.offset,
            "rows": list(self.rows)
        }
        
    def lookahead(self, it, end=None):
        """Returns an iterator over current and next value. Next value will be None for the last value.
        """
        it = iter(it)
        current = it.next()
        
        for ahead in it:
            yield current, ahead
            current = ahead
        
        yield current, end
        
class Query:
    def __init__(self, db, tables=[]):
        self.db = db
        
        self.tables = tables
        self.what = "*"
        self.order = "key"
        self.wheres = []
        self.offset = None
        self.limit = None
        
    def execute(self, options):
        self.process_descending(options)
        self.process_wheres(options)
        
        self.limit = options.get("limit")
        self.offset = options.get("offset")
        
        _test = options.get("_test", False)
        
        if isinstance(self.what, list):
            what = ", ".join(self.what)
        else:
            what = self.what
        
        where = web.SQLQuery.join(self.wheres or ["1 = 1"], " AND ")
        return self.db.select(self.tables, what=what, where=where, offset=self.offset, limit=self.limit, order=self.order, _test=_test)
        
    def process_wheres(self, options):
        def add(name, op, value):
            q = web.SQLQuery([name, op, web.sqlparam(value)])
            self.wheres.append(q)

        if "key" in options:
            key = options['key']
            add("key", " = ", key)
        elif "startkey" in options or "endkey" in options:
            if "startkey" in options:
                startkey = options["startkey"]
                add("key", " >= ", startkey)
            if "endkey" in options:
                endkey = options["endkey"]
                add("key", " < ", endkey)
        
    def process_descending(self, options):
        descending = options.get("descending", False)
        
        if descending:
            self.order = "key desc"
            
            # Reverse startkey and endkey since couchdb expects the descending
            # option to be applied before key filtering.
            
            # None could be a valid value for startkey/endkey. Using a stub instead of None.
            nothing = object()
            startkey = options.pop("startkey", nothing)
            endkey = options.pop("endkey", nothing)
            if startkey is not nothing:
                options['endkey'] = startkey
            if endkey is not nothing:
                options['startkey'] = endkey
    
class View:
    def __init__(self, designdoc, viewname):
        self.designdoc = designdoc
        self.name = viewname
        
    def __repr__(self):
        name = self.designdoc['_id'] + "/_view/" + self.name
        return "<View: %r>" % name

    def update(self, stale=None):
        self.designdoc.update(stale=stale)
        
    def query(self, **options):
        stale = options.get("stale", "not-ok")
        self.update(stale=stale)
        
        query = self.make_query(options)
        rows = query.execute(options)
        rows = [self.process_row(row) for row in rows]
        return ViewResponse(total_rows=0, offset=0, rows=rows)
        
    def make_query(self, options):
        db = self.designdoc.database.db
        table = self.designdoc.get_table()
        q = Query(db, [table + " as design"])
        q.what = ["design.docid as id", "design.key", "design.value"]
        
        include_docs = options.get("include_docs", False)
        if include_docs:
            db_table = self.designdoc.database.table
            q.tables.append(db_table + " as doc")
            q.what.append("doc.doc")
            q.wheres.append("design.docid = doc.docid")
        return q
        
    def process_row(self, row):
        if "doc" in row:
            row["doc"] = json.loads(row["doc"])
        return row

class AllDocsView(View):
    def __init__(self, database):
        self.database = database
        
    def update(self, stale=None):
        # Nothing to update
        pass
        
    def make_query(self, options):
        q = Query(self.database.db, self.database.table)
        
        if options.get("include_docs"):
            q.what = "docid, docid as key, rev, doc"
        else:
            q.what = "docid, docid as key, rev"
        return q
        
    def process_row(self, row):
        d = {
            "id": row.key,
            "key": row.key,
            "value": {"rev": row.rev}
        }
        if "doc" in row:
            d["doc"] = json.loads(row.doc)
        return d
