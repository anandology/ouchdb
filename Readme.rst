OuchDB
======

OuchDB is an implementation of CouchDB_ API on relational databases.

.. _CouchDB: http://couchdb.apache.org/

The current version works only with the SQLite and support of other databases will be available in future releases.

Supported Features:

* Creating databases
* Creating documents
* Accessing Futon at /_utils/

Running OuchDB
==============

Start gunicorn webserver

    $ gunicorn ouchdb:wsgi
    
And visit futon
    
    http://127.0.0.1:8000/_utils/


Installing OuchDB
=================

OuchDB can be installed from pypi using::

    $ pip install ouchdb
    
License
=======

Copyright 2011 Anand Chitipothu

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
