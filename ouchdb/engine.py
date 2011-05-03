import web
from . import schema


class Engine:
    def __init__(self):
        self.init()
        
    def init(self):
        self.db = web.database(dbn="sqlite", db="ouch.db")
        self.init_schema()
        
    def init_schema(self):
        if "databases" not in self._list_tables():
            for s in schema.SCHEMA.split(";"):
                print s
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
            return Database(**rows[0])
        
    def list_databases(self):
        rows = self.db.query("SELECT name FROM databases")
        return [row.name for row in rows]
        
class MemoryEngine(Engine):
    def init(self):
        self.db = web.database(dbn="sqlite", db=":memory:")
        self.init_schema()
        
class Database:
    def __init__(self, id, name, **kw):
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
        
    def list_docs(self):
        rows = db.query("SELECT * FROM %s" % self.table)
        return rows.list()
        
    def add_doc(self, doc):
        pass
    