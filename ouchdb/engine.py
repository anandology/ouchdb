# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import uuid
import json
import logging

import web
from . import schema

logger = logging.getLogger("ouchdb.engine")

class EngineException(Exception):
    pass
    
class Conflict(EngineException):
    pass

class Engine:
    def __init__(self, db):
        self.db = db
        self.init_schema()
        
    def init_schema(self):
        if "databases" not in self._list_tables():
            for s in schema.SCHEMA.split(";"):
                logger.debug("query: %s", s)
                self.db.query(s)
        
    def _list_tables(self):
        rows = self.db.query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [row.name for row in rows]
            
    def create_database(self, name):
        t = self.db.transaction()
        try:
            if not self.get_database(name):
                dbname = "db_" + name
                self.db.insert("databases", name=name)
                self.db.query(schema.DATABASE_TABLE % dbname)
                return True
        except:
            t.rollback()
            raise
        finally:
            t.commit()
        return False
            
    def delete_database(self, name):
        t = self.db.transaction()
        try:
            if self.get_database(name):
                self.db.delete("databases", where="$name=name", vars=locals())
                self.db.query("DROP TABLE db_" + name)
                return True
        except:
            t.rollback()
            raise
        finally:
            t.commit()
        return False
        
    def get_database(self, name):
        rows = self.db.query("SELECT * FROM databases WHERE name=$name", vars=locals()).list()
        if rows:
            return Database(self.db, **rows[0])
        
    def list_databases(self):
        rows = self.db.query("SELECT name FROM databases ORDER BY name")
        return [row.name for row in rows]
        
class MemoryEngine(Engine):
    def init(self):
        self.db = web.database(dbn="sqlite", db=":memory:")
        self.init_schema()
        
def generate_uuid():
    return str(uuid.uuid1()).replace("-", "")

class Database:
    def __init__(self, db, id, name, **kw):
        self.db = db
        
        self.id = id
        self.name = name
        self.__dict__.update(kw)
        self.table = "db_" + name
        
    def info(self):
        return {
            "db_name": self.name,
            "doc_count": 0,
            "doc_del_count": 0,
            "update_seq": 9,
            "purge_seq": 0,
            "compact_running": False,
            "disk_size": 0,
            "instance_start_time": "0",
            "disk_format_version": 5,
            "committed_update_seq": 0
        }
    
    def view(self, name):
        if name == "_all_docs":
            return AllDocsView(self, "_all_docs")
        
    def list(self):
        rows = self.db.query("SELECT * FROM %s" % self.table)
        return rows.list()
        
    def get_sequence(self):
        self.db.query("UPDATE databases SET sequence=sequence+1 WHERE id=$self.id", vars=locals())
        d = self.db.query("SELECT sequence FROM databases WHERE id=$self.id", vars=locals())
        return d[0].sequence
        
    def put(self, doc):
        with self.db.transaction():
            _id = doc.get("_id")
            old_doc = _id and self.get(_id)
            
            if old_doc:
                return self._update_doc(doc, old_doc['_rev'])
            else:
                return self._new_doc(doc)
    
    def _update_doc(self, doc, old_rev):
        if doc.get('_rev') != old_rev:
            raise Conflict()
        
        _id = doc['_id']
        rev = str(1 + int(old_rev))
        seq = self.get_sequence()
        doc['_rev'] = rev
        self.db.update(self.table, where="docid=$_id", rev=rev, seq=seq, doc=json.dumps(doc), vars=locals())
        return doc['_id'], doc['_rev']
        
    def _new_doc(self, doc):
        _id = doc.get("_id")
        if not _id:
            _id = generate_uuid()
            doc['_id'] = _id
    
        rev = "1"
        seq = self.get_sequence()
        doc['_rev'] = rev
        self.db.insert(self.table, docid=_id, rev=rev, seq=seq, doc=json.dumps(doc))
        return doc['_id'], doc['_rev']
    
    def get(self, docid):
        rows = self.db.select(self.table, where="docid=$docid", vars=locals()).list()
        if rows:
            return json.loads(rows[0].doc)
            
    def delete(self, docid, rev):
        with self.db.transaction():
            old_doc = self.get(docid)
            if not old_doc:
                return None
            else:
                doc = {"_id": docid, '_rev': rev, '_deleted': True}
                return self._update_doc(doc, rev)
        
class View:
    def __init__(self, database, viewname):
        self.database = database
        self.name = viewname
        
    def query(self, **kwargs):
        include_docs = kwargs.get("include_docs", False)
        descending = kwargs.get("descending", False)
        
        if descending:
            # Reverse startkey and endkey since couchdb expects the descending
            # option to be applied before key filtering.
            
            # None could be a valid value for startkey/endkey. Using a stub instead of None.
            nothing = object()
            startkey = kwargs.pop("startkey", nothing)
            endkey = kwargs.pop("endkey", nothing)
            if startkey is not nothing:
                kwargs['endkey'] = startkey
            if endkey is not nothing:
                kwargs['startkey'] = endkey
        
        tables = self.get_tables(include_docs=include_docs)
        what = self.get_what(include_docs=include_docs)
        where = self.get_wheres(**kwargs) or ["1 = 1"]
        where = web.SQLQuery.join(where, " AND ")
        
        kw = {}
        if 'limit' in kwargs:
            kw['limit'] = kwargs.pop('limit')
        if 'skip' in kwargs:
            kw['offset'] = kwargs.pop('skip')
            
        kw['order'] = self.get_order(descending)
                    
        rows = self.database.db.select(tables, what=what, where=where, **kw).list()
            
        rows = [self.process_row(row) for row in rows]
        return {"total_rows": 0, "offset": 0, "rows": rows}
        
    def process_row(self, row):
        return dict(row)
        
    def get_tables(self, include_docs=False):
        raise NotImplementedError()
        
    def get_what(self, include_docs=False):
        raise NotImplementedError()
        
    def get_wheres(self, **kwargs):
        raise NotImplementedError()
        
    def get_order(self, descending):
        if descending:
            return "key DESC"
        else:
            return "key"
        
class AllDocsView(View):
    def get_tables(self, include_docs=False):
        return self.database.table
        
    def get_what(self, include_docs=False):
        if include_docs:
            return "docid as key, rev, doc"
        else:
            return "docid as key, rev"

    def get_wheres(self, **kwargs):
        wheres = []
        
        def add(name, op, value):
            q = web.SQLQuery([name, op, web.sqlparam(value)])
            wheres.append(q)
        
        if "key" in kwargs:
            key = kwargs['key']
            add("key", " = ", key)
        elif "startkey" in kwargs or "endkey" in kwargs:
            if "startkey" in kwargs:
                startkey = kwargs["startkey"]
                add("key", " >= ", startkey)
            if "endkey" in kwargs:
                endkey = kwargs["endkey"]
                add("key", " < ", endkey)
        return wheres
        
    def process_row(self, row):
        d = {
            "id": row.key,
            "key": row.key,
            "value": {"rev": row.rev}
        }
        if "doc" in row:
            d["doc"] = json.loads(row.doc)
        return d