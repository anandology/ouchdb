from setuptools import setup, find_packages
from ouchdb.version import VERSION

setup(
    name='ouchdb',
    version=VERSION,
    description='OuchDB is an implementation of CouchDB API on relational databases',
    packages=find_packages(exclude=["ez_setup"]),
    install_requires="web.py gunicorn".split(),

    author="Anand Chitipothu",
    author_email="anandology@gmail.com",

    license="Apache License, Version 2.0",
    platforms=["any"],
)
