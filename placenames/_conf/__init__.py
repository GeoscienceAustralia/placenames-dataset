from os.path import dirname, realpath, join, abspath
import os
import psycopg2
from psycopg2 import extras
import yaml



APP_DIR = dirname(dirname(realpath(__file__)))
TEMPLATES_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'templates')
STATIC_DIR = join(dirname(dirname(abspath(__file__))), 'view', 'static')


LOGFILE = APP_DIR + '/flask.log'
DEBUG = True

# get db conn settings from yaml file
directory = os.path.dirname(os.path.realpath(__file__))
file = os.path.join(directory, "secrets.yml")
PLACE_NAMES_DB_CON_DICT = yaml.safe_load(open(file))

if PLACE_NAMES_DB_CON_DICT is None:
    print('You must set up a secrets.yml file containing the DB login credentials')
    exit()


JURISDICTION_INSTANCE_URI_STEM = 'http://localhost:5000/jurisdiction/'
GAZETTEER_INSTANCE_URI_STEM = 'http://localhost:5000/gazetteer/'


def db_select(q):
    try:
        # print(PLACE_NAMES_DB_CON_DICT['place_names_db_con'])
        # host = PLACE_NAMES_DB_CON_DICT['place_names_db_con']['host']
        # port = PLACE_NAMES_DB_CON_DICT['place_names_db_con']['port']
        # dbname = PLACE_NAMES_DB_CON_DICT['place_names_db_con']['dbname']
        # user = PLACE_NAMES_DB_CON_DICT['place_names_db_con']['user']
        # password = PLACE_NAMES_DB_CON_DICT['place_names_db_con']['password']
        #conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        conn = psycopg2.connect(**PLACE_NAMES_DB_CON_DICT['place_names_db_con'])

        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(q)
        return cur.fetchall()
    except Exception as e:
        print(e)
