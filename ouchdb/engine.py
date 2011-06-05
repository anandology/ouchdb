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
        rows = self.db.query("SELECT name FROM databases")
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
            if _id:
                old_doc = self.get(_id)
            else:
                _id = generate_uuid()
                doc['_id'] = _id
                old_doc = None
                
            
            if old_doc:
                if old_doc['_rev'] != doc.get('_rev'):
                    raise Conflict()
                    
                
                rev = str(1 + int(old_doc['_rev']))
                seq = self.get_sequence()
                doc['_rev'] = rev
                self.db.update(self.table, where="id=$_id", rev=rev, seq=seq, doc=json.dumps(doc), vars=locals())
            else:
                rev = "1"
                seq = self.get_sequence()
                doc['_rev'] = rev
                self.db.insert(self.table, id=_id, rev=rev, seq=seq, doc=json.dumps(doc))
            
            return _id, rev
    
    def get(self, docid):
        rows = self.db.select(self.table, where="id=$docid", vars=locals()).list()
        if rows:
            return json.loads(rows[0].doc)
