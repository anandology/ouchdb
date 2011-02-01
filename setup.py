from setuptools import setup, find_packages
import stat

def executable(path):
    st = os.stat(path)[stat.ST_MODE]
    return (st & stat.S_IEXEC) and not stat.S_ISDIR(st)

setup(
    name='ouchdb',
    version='0.0.1',
    description='OuchDB is CouchDB on SQL',
    packages=find_packages(exclude=["ez_setup"]),
    scripts=filter(executable, glob.glob('scripts/*')),
    install_requires="web.py gunicorn".split()
)
