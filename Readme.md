# OuchDB

OuchDB is CouchDB implementation on SQL.

It is in early development and the goal is to implement complete CouchDB API.

Once it is ready, you will be able to run futon, use couchdb-lucene and replicate to/from a couchdb database.

# Running OuchDB

Start gunicorn webserver

    $ gunicorn ouchdb:wsgi
    
And visit futon
    
    http://127.0.0.1:8000/_utils/
