from flask import Blueprint, request, redirect, url_for, Response, render_template, send_file
import flask
from placenames.model.placename import Placename
from placenames.model.gazetteer import Gazetteer, GAZETTEERS
from pyldapi import RegisterRenderer
import placenames._conf as conf
import folium
import os

routes = Blueprint('controller', __name__)

DEFAULT_ITEMS_PER_PAGE=50


@routes.route('/', strict_slashes=True)
def home():
    return render_template('home.html')


@routes.route('/placename/')
def placenames():
    # Search
    search_string = request.values.get('search')
    # get the total register count from the XML API
    try:
        # get the register length from the online DB
        sql = '''SELECT COUNT(*) FROM "PLACENAMES"
'''
        if search_string:
            sql += '''WHERE UPPER("ID") LIKE '%{search_string}%' OR UPPER("NAME") LIKE '%{search_string}%';
'''.format(search_string=search_string.strip().upper())
        #print(sql)
        no_of_items = conf.db_select(sql)[0][0]

        page = int(request.values.get('page')) if request.values.get('page') is not None else 1
        per_page = int(request.values.get('per_page')) if request.values.get('per_page') is not None else DEFAULT_ITEMS_PER_PAGE
        offset = (page - 1) * per_page
        items = []
        sql = '''SELECT "ID", "NAME" 
FROM "PLACENAMES"
'''
        if search_string:
            sql += '''WHERE UPPER("ID") LIKE '%{search_string}%' OR UPPER("NAME") LIKE '%{search_string}%'
'''.format(search_string=search_string.strip().upper())
            
        sql += '''ORDER BY "AUTHORITY", cast('0' || regexp_replace("AUTH_ID", '\D+', '') as integer), "AUTH_ID"
OFFSET {}
LIMIT {}
'''.format(offset, per_page)
        #print(sql)
        for item in conf.db_select(sql):
            items.append(
                (item[0], item[1])
            )
    except Exception as e:
        print(e)
        return Response('The Place Names database is offline', mimetype='text/plain', status=500)

    return RegisterRenderer(request=request, 
                            uri=request.url, 
                            label='Place Names Register', 
                            comment='A register of Place Names', 
                            register_items=items,
                            contained_item_classes=['http://linked.data.gov.au/def/placenames/PlaceName'], 
                            register_total_count=no_of_items, 
                            views=None, 
                            default_view_token=None, 
                            super_register=None,
                            page_size_max=1000, 
                            register_template=None, 
                            per_page=per_page, 
                            search_query=search_string,
                            search_enabled=True
                            ).render()

#@routes.route('/map/')
#def map():
#    print('map here')


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
def placename(placename_id):
    pn = Placename(request, request.base_url)
    return pn.render()

@routes.route('/gazetteer/')
def gazetteers():
    # get the total register count from the XML API
    try:
        # get the register length from the hard-coded dict
        no_of_items = len(GAZETTEERS)

        page = int(request.values.get('page')) if request.values.get('page') is not None else 1
        per_page = int(request.values.get('per_page')) if request.values.get('per_page') is not None else DEFAULT_ITEMS_PER_PAGE
        offset = (page - 1) * per_page
        items = []
        
        for key in sorted(GAZETTEERS.keys()):
            items.append(
                (key, GAZETTEERS[key]['label'])
            )
    except Exception as e:
        print(e)
        return Response('The Gazetteers Register is offline', mimetype='text/plain', status=500)

    return RegisterRenderer(
        request,
        request.url,
        'Gazetteers Register',
        'A register of Gazetteers',
        items,
        ['http://linked.data.gov.au/def/placenames/gazetteer'],
        no_of_items,
        per_page=per_page
    ).render()


@routes.route('/gazetteer/<string:gazetteer_id>')
def gazetteer(gazetteer_id):
    gz = Gazetteer(request, request.base_url)
    return gz.render()
