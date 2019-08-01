from flask import Blueprint, request, redirect, url_for, Response, render_template, send_file
import flask
from placenames.model.placename import Placename
from pyldapi import RegisterRenderer
import placenames._conf as conf
import folium
import os

routes = Blueprint('controller', __name__)


@routes.route('/', strict_slashes=True)
def home():
    return render_template('home.html')


@routes.route('/placename/')
def placenames():
    # get the total register count from the XML API
    try:
        # get the register length from the online DB
        no_of_items = conf.db_select('SELECT COUNT(*) FROM "PLACENAMES";')[0][0]

        page = int(request.values.get('page')) if request.values.get('page') is not None else 1
        per_page = int(request.values.get('per_page')) if request.values.get('per_page') is not None else 1000
        offset = (page - 1) * per_page
        items = []
        q = '''
            SELECT "ID", "NAME" FROM "PLACENAMES"
            ORDER BY "ID"
            OFFSET {}
            LIMIT {}
        '''.format(offset, per_page)
        for item in conf.db_select(q):
            items.append(
                (item[0], item[1])
            )
    except Exception as e:
        print(e)
        return Response('The Place Names Register is offline', mimetype='text/plain', status=500)

    return RegisterRenderer(
        request,
        request.url,
        'Place Names Register',
        'A register of Place Names',
        items,
        ['http://linked.data.gov.au/def/placenames/PlaceName'],
        no_of_items
    ).render()

#@routes.route('/map/')
#def map():
#    print('map here')


@routes.route('/map')
def map():
    '''
    Function to render a map around the specified coordinates
    '''
    name = request.values.get('name')
    x = float(request.values.get('x'))
    y = float(request.values.get('y'))
    # create a new map object  # ==========================================================
    folium_map = folium.Map(location=[y, x], zoom_start=10)
    tooltip = 'Click for more information'
    # create markers
    folium.Marker([y, x],
                     #popup='<strong>"self.hasName"</strong>',
                     popup = name,
                     tooltip=tooltip).add_to(folium_map),

    # folium.Marker([-66.24, 110.57],
    #               popup='<strong>Location One</strong>',
    #               tooltip=tooltip).add_to(m),
    # generate and save map
    # m.save(r'C:\Users\Joseph\PycharmProjects\pyLD_API\PlacenamesAPI\placenames\view\templates\map.html')
    # map_temp = m.save(tempfile.TemporaryFile())
    print("tell")
    #print(map_temp)
    #print("tell: " + str(map_temp.tell()))
    return folium_map.get_root().render()
    # ====================================================================================



@routes.route('/placename/<string:placename_id>')
def placename(placename_id):
    pn = Placename(request, request.base_url)
    return pn.render()






