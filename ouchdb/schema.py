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
    docid text primary key,
    rev text,
    seq integer unique,
    doc text
)"""

VIEW_TABLE = """
create table %s (
    id integer primary key,
    docid text,
    key text,
    value text,
    seq integer
)"""
