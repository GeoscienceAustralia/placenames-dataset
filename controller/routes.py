from flask import Blueprint, request, Response, render_template
from model.placename import Placename
from model.place import Place
from pyldapi import ContainerRenderer
import conf
import folium
from rdflib import Graph

print(__name__)
routes = Blueprint('controller', __name__)

DEFAULT_ITEMS_PER_PAGE=50

@routes.route('/fsdf_home', strict_slashes=True)
def fsdf_home():
    return render_template('fsdf_home.html')

@routes.route('/', strict_slashes=True)
def home():
    return render_template('home.html')

@routes.route('/index.ttl', strict_slashes=True)
def ttl():
    # return render_template('index.ttl')
    g = Graph()
    g.parse('index.ttl', format='turtle')
    return Response(
                g.serialize(format='turtle'),
                mimetype='text/turtle')


@routes.route('/placename/')
def placename():
    # Search specific items using keywords
    search_string = request.values.get('search')

    try:
        # get the register length from the online DB
        sql = 'SELECT COUNT(*) FROM "PLACENAMES"'
        if search_string:
            sql += '''WHERE UPPER("ID") LIKE '%{search_string}%' OR UPPER("NAME") LIKE '%{search_string}%';
                   '''.format(search_string=search_string.strip().upper())

        no_of_items = conf.db_select(sql)[0][0]

        page = int(request.values.get('page')) if request.values.get('page') is not None else 1
        per_page = int(request.values.get('per_page')) \
                   if request.values.get('per_page') is not None else DEFAULT_ITEMS_PER_PAGE
        offset = (page - 1) * per_page

        # get the id and name for each placename record in the database
        sql = '''SELECT "ID", "NAME" FROM "PLACENAMES"'''
        if search_string:
            sql += '''WHERE UPPER("ID") LIKE '%{search_string}%' OR UPPER("NAME") LIKE '%{search_string}%'
                   '''.format(search_string=search_string.strip().upper())
        sql += '''ORDER BY "AUTHORITY", cast('0' || regexp_replace("AUTH_ID", '\D+', '') as integer), "AUTH_ID"
                OFFSET {} LIMIT {}'''.format(offset, per_page)

        items = []
        for item in conf.db_select(sql):
            items.append(
                (item[0], item[1])
            )
    except Exception as e:
        print(e)
        return Response('The Place Names database is offline', mimetype='text/plain', status=500)

    return ContainerRenderer(request=request,
                            instance_uri=request.url,
                            label='Place Names Register', 
                            comment='A register of Place Names',
                            parent_container_uri='http://linked.data.gov.au/def/placenames/PlaceName',
                            parent_container_label='Placenames',
                            members=items,
                            members_total_count=no_of_items,
                            profiles=None,
                            default_profile_token=None,
                            super_register=None,
                            page_size_max=1000,
                            register_template=None,
                            per_page=per_page,
                            search_query=search_string,
                            search_enabled=True
                            ).render()


@routes.route('/place/')
def place():
    # Search specific items using keywords
    search_string = request.values.get('search')
    # get the total register count from the XML API
    try:
        # get the register length from the online DB
        sql = '''SELECT COUNT(*) FROM "PLACENAMES"'''
        if search_string:
            sql += '''WHERE UPPER("ID") LIKE '%{search_string}%' OR UPPER("NAME") LIKE '%{search_string}%';
                   '''.format(search_string=search_string.strip().upper())
        no_of_items = conf.db_select(sql)[0][0]

        page = int(request.values.get('page')) if request.values.get('page') is not None else 1
        per_page = int(request.values.get('per_page')) if request.values.get(
            'per_page') is not None else DEFAULT_ITEMS_PER_PAGE
        offset = (page - 1) * per_page

        sql = '''SELECT "ID", "NAME" FROM "PLACENAMES"'''
        if search_string:
            sql += '''WHERE UPPER("ID") LIKE '%{search_string}%' OR UPPER("NAME") LIKE '%{search_string}%'
                   '''.format(search_string=search_string.strip().upper())
        sql += '''ORDER BY "AUTHORITY", cast('0' || regexp_replace("AUTH_ID", '\D+', '') as integer), "AUTH_ID"
                OFFSET {} LIMIT {}'''.format(offset, per_page)

        items = []
        for item in conf.db_select(sql):
            items.append(
                (item[0], item[1])
            )
    except Exception as e:
        print(e)
        return Response('The Place Names database is offline', mimetype='text/plain', status=500)

    return ContainerRenderer(request=request,
                            instance_uri=request.url,
                            label='Places Register',
                            comment='A register of Places',
                            parent_container_uri='http://linked.data.gov.au/def/placenames/PlaceName',
                            parent_container_label='Places',
                            members=items,
                            members_total_count=no_of_items,
                            profiles=None,
                            default_profile_token=None,
                            super_register=None,
                            page_size_max=1000,
                            register_template=None,
                            per_page=per_page,
                            search_query=search_string,
                            search_enabled=True
                            ).render()


@routes.route('/map')
def show_map():
    '''
    Function to render a map around the specified coordinates
    '''
    name = request.values.get('name')
    x = float(request.values.get('x'))
    y = float(request.values.get('y'))

    # create a new map object
    folium_map = folium.Map(location=[y, x], zoom_start=10)
    tooltip = 'Click for more information'
    # create markers
    folium.Marker([y, x],
                  popup = name,
                  tooltip=tooltip).add_to(folium_map),

    return folium_map.get_root().render()


@routes.route('/placename/<string:placename_id>')
def placename_item(placename_id):
    pn = Placename(request, request.base_url)
    return pn.render()


@routes.route('/place/<string:placename_id>')
def place_item(placename_id):
    pn = Place(request, request.base_url)
    return pn.render()
