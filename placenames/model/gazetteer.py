# -*- coding: utf-8 -*-
from flask import render_template, Response
from rdflib import Graph, URIRef, RDF, RDFS, XSD, OWL, Namespace, Literal, BNode
import placenames._conf as conf
from psycopg2 import sql
import json
import decimal
from pyldapi import Renderer, View

#GAZETTEER_URI_PREFIX = 'http://localhost:5000/gazetteer/'
GAZETTEER_URI_PREFIX = 'http://linked.data.gov.au/dataset/placenames/gazetteer/'

# setup a dictionary of GAZETTEERS
#need to insert uri_id's to point to the authority though the naming authorities dictionary below
GAZETTEERS = {
    'AAD': {
        'label': 'Australian Antarctic Place Names Gazetteer',
        'uri_id': 'https://data.aad.gov.au/aadc/gaz/'
    },
    'ACT': {
        'label': 'Australian Capital Territory Place Names Gazetteer',
        'uri_id': 'http://app.actmapi.act.gov.au/actmapi/index.html?viewer=pn'
    },
    'AHO': {
        'label': 'Australian Hydrographic Office Place Names Gazetteer',
        'uri_id': 'http://www.hydro.gov.au/'
    },
    'NSW': {
        'label': 'New South Wales Place Names Gazetteer',
        'uri_id': 'http://www.gnb.nsw.gov.au/place_naming/placename_search'
    },
    'NT': {
        'label': 'Northern Territory Place Names Gazetteer',
        'uri_id': 'https://www.ntlis.nt.gov.au/placenames/'
    },
    'QLD': {
        'label': 'Queensland Place Names Gazetteer',
        'uri_id': 'https://www.dnrm.qld.gov.au/qld/environment/land/place-names/search'
    },
    'SA': {
        'label': 'South Australian Place Names Gazetteer',
        'uri_id': 'https://www.sa.gov.au/topics/planning-and-property/planning-and-land-management/suburb-road-and-place-names/place-names-search'
    },
    'TAS': {
        'label': 'Tasmanian Place Names Gazetteer',
        'uri_id': 'https://www.placenames.tas.gov.au/#p0'
    },
    'VIC': {
        'label': 'Victorian Place Names Gazetteer',
        'uri_id': 'https://maps.land.vic.gov.au/lassi/VicnamesUI.jsp'
    },
    'WA': {
        'label': 'Western Australian Place Names Gazetteer',
        'uri_id': 'https://www0.landgate.wa.gov.au/maps-and-imagery/wa-geographic-names'
    }
}

DATE_MODIFIED = '2019-06-06 12:18:00.525998'

class Gazetteer(Renderer):
    """
    This class represents a gazetteer and methods in this class allow a gazetteer to be loaded from the GA placenames database
    and to be exported in a number of formats including RDF, according to the 'PlaceNames Ontology'

    [[and an expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.]]??
    """

    def __init__(self, request, uri):
        views = {
            'gz': View(
                'Gazetteer View',
                'This view is the standard view delivered by the Place Names dataset in accordance with the '
                'Place Names Profile',
                ['text/html', 'text/turtle', 'application/ld+json'],
                'text/html'
            )
        }

        super(Gazetteer, self).__init__(request, uri, views, 'gz', None)
        self.id = uri.split('/')[-1]

        self.hasName = {
            'uri': 'http://linked.data.gov.au/def/placenames/hasName',
            'label': 'has name',
            'comment': 'The Entity has a name (label) which is a text sting.',
            'value': None
        }
        # setup a dictionary of gazetteers
        #need to insert uri_id's to point to the authority though the naming authorities dictionary below
        self.register = {
            'label': None,
            'uri': None
        }

        self.wasNamedBy = {
            'label': None,
            'uri': None
        }

        self.hasNameFormality = {
            'label': 'Official',
            'uri': 'http://linked.data.gov.au/def/placenames/nameFormality/Official'
        }

        self.modifiedDate = None

        self.hasPronunciation = 'abcABCabc'

        self.hasName['value'] = str(GAZETTEERS[self.id]['label'])
        self.register['label'] = str(GAZETTEERS[self.id]['label'])
        self.register['uri'] = GAZETTEER_URI_PREFIX + str(GAZETTEERS[self.id]['uri_id'])
        self.modifiedDate = DATE_MODIFIED

        # need to build this naming Authorities dictionary out
        naming_authorities = {
            'ACT': {
                'label': 'Australian Capital Territory',
                'uri_id': 'act'
            },
            'AAD': {
                'label': 'Australian Antarctic Division',
                'uri_id': 'aad'
            },
            'WA': {
                'label': 'Western Australian Government',
                'uri_id': 'wa'
            }  # add the uri to the naming Authority
        }  # add all states, territories and other naming bodies

    # maybe should call this function something else - it seems to clash ie Overrides the method in Renderer
    def render(self):
        if self.view == 'alternates':
            return self._render_alternates_view()   # this function is in Renderer
        elif self.format in ['text/turtle', 'application/ld+json']:
            return self.export_rdf()                # this one exists below
        else:  # default is HTML response: self.format == 'text/html':
            return self.export_html()               # this one exists below

    def export_html(self):
        return Response(        # Response is a Flask class imported at the top of this script
            render_template(     # render_template is also a Flask module
                'gazetteer.html',   # uses the placenames.html template send all this data to it.
                id=self.id,
                hasName=self.hasName,
                hasPronunciation=self.hasPronunciation,
                register=self.register,
                wasNamedBy=self.wasNamedBy,
                hasNameFormality=self.hasNameFormality,
                modifiedDate=self.modifiedDate
                # schemaorg=self.export_schemaorg()
            ),
            status=200,
            mimetype='text/html'
        )
        # if we had multiple views, here we would handle a request for an illegal view
        # return NotImplementedError("HTML representation of View '{}' is not implemented.".format(view))

    def export_rdf(self):
        g = Graph()  # make instance of a RDF graph

        GZ = Namespace('http://linked.data.gov.au/def/gazetteer/')   #rdf neamespace declaration
        g.bind('gz', GZ)


        #loop through the next 3 lines to get subject, predicate, object for the triple store adding each time??
        me = URIRef(self.uri)   # URIRef is a RDF class
        g.add((me, RDF.type, URIRef('http://linked.data.gov.au/def/gazetteer/PlaceName')))  # GZ.PlaceName))
        g.add((me, GZ.hasName, Literal(self.hasName['value'], datatype=XSD.string)))

        if self.format == 'text/turtle':
            return Response(
                g.serialize(format='turtle'),
                mimetype='text/turtle'
            )
        else:  # JSON-LD
            return Response(
                g.serialize(format='json-ld'),
                mimetype='application/ld+json'
            )
    # for schema dot org format
    def export_schemaorg(self):  #this is all for GNAF - needs to adapted to Placenames
        data = {
            '@context': 'http://schema.org',
            '@type': 'Place',
            'address': {
                '@type': 'PostalAddress',
                'streetAddress': self.address_string.split(',')[0],
                'addressLocality': self.locality_name,
                'addressRegion': self.state_prefLabel,    #change these for placenames attributes
                'postalCode': self.postcode,
                'addressCountry': 'AU'
            },
            'geo': {
                '@type': 'GeoCoordinates',
                'latitude': self.latitude,                # keep this for placenames?
                'longitude': self.longitude
            },
            'name': 'Geocoded Address ' + self.id
        }

        #return json.dumps(data, cls=DecimalEncoder) #
        return json.dumps(data, cls=decimal)  # changed to suit import


if __name__ == '__main__':
    # a = Address('GANSW703902211', focus=True)  # not functional because from GNAF - this is placenames
    # print(a.export_rdf().decode('utf-8'))

    print('main process has not been built yet - when build it will test ask for a gazetteer like the code Gnaf above')


