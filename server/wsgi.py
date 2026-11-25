"""
PythonAnywhere WSGI entry: /home/samthropic/JAYDES/server/wsgi.py

Set MONGO_PASSWD in the web-app Environment variables UI (do not commit it).
"""
import os
import sys

PROJ_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJ_DIR not in sys.path:
    sys.path.insert(0, PROJ_DIR)

os.environ.setdefault('CLOUD_MONGO', '1')

from server.endpoints import app  # noqa: E402

application = app
