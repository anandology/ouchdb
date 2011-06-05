"""SQL schema for ouchdb.
"""

SCHEMA = """
create table databases (
    id integer primary key,
    name text UNIQUE,
    sequence integer default 0    
);

create table views (
    id integer primary key,
    database_id integer,
    name text,
    sequence text,
    
    FOREIGN KEY(database_id) REFERENCES databases(id)
);
"""

DATABASE_TABLE = """
create table %s (
    id text primary key,
    rev text,
    seq integer unique,
    doc text
)"""

VIEW_TABLE = """
create table %s (
    id integer primary key,
    key text,
    value text,
    seq integer
)"""
