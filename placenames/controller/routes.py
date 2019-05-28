from flask import Blueprint, request, redirect, url_for, Response, render_template
from placenames.model.placename import Placename
from pyldapi import RegisterRenderer
import placenames._conf as conf

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

        page = request.values.get('page') if request.values.get('page') is not None else 1
        per_page = request.values.get('per_page') if request.values.get('per_page') is not None else 30
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


@routes.route('/placename/<string:placename_id>')
def placename(placename_id):
    pn = Placename(request, request.base_url)
    return pn.render()
