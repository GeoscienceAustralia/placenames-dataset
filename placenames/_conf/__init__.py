from os.path import dirname, realpath, join, abspath
import os
import psycopg2
from psycopg2 import extras
import secrets


APP_DIR = dirname(dirname(realpath(__file__)))
TEMPLATES_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'templates')
STATIC_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'static')


LOGFILE = APP_DIR + '/flask.log'
DEBUG = True
PLACE_NAMES_DB_CON = secrets['PLACE_NAMES_DB_CON']
if PLACE_NAMES_DB_CON is None:
      print('You must set an environment variable for the DB connection called PLACE_NAMES_DB_CON')
      exit()
else:
     PLACE_NAMES_DB_CON = os.environ['PLACE_NAMES_DB_CON']
     print('from config')
     print(PLACE_NAMES_DB_CON)
     print(os.environ)

JURISDICTION_INSTANCE_URI_STEM = 'http://localhost:5000/jurisdiction/'
GAZETTEER_INSTANCE_URI_STEM = 'http://localhost:5000/gazetteer/'


def db_select(q):
    try:

        conn = psycopg2.connect(PLACE_NAMES_DB_CON)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(q)
        return cur.fetchall()
    except Exception as e:
        print(e)
