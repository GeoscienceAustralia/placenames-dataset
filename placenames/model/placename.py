# -*- coding: utf-8 -*-
import decimal
import json
from flask import render_template, Response

import placenames._conf as conf
from pyldapi import Renderer, View
from rdflib import Graph, URIRef, RDF, XSD, Namespace, Literal, BNode
from rdflib.namespace import XSD, DCTERMS, RDFS   #imported for 'export_rdf' function

from .gazetteer import GAZETTEERS, NAME_AUTHORITIES

# for DGGS zone attribution
from rhealpixdggs import dggs
rdggs = dggs.RHEALPixDGGS()

class Placename(Renderer):
    """
    This class represents a placename and methods in this class allow a placename to be loaded from the GA placenames
    database and to be exported in a number of formats including RDF, according to the 'PlaceNames Ontology'

    [[and an expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.]]??
    """

    def __init__(self, request, uri):
        views = {
            'NCGA': View(
                'Place Names View',
                'This view is the combined view of places and placenmaes delivered by the Place Names dataset in '
                'accordance with the Place Names Profile',
                ['text/html', 'text/turtle', 'application/ld+json'],
                'text/html'
            ),
            'pn': View(
                'Place Names View',
                'This view is the standard view (separating places and placenames) delivered by the Place Names dataset'
                ' in accordance with the Place Names Profile',
                ['text/html', 'text/turtle', 'application/ld+json'],
                'text/html'
            )
        }

        super(Placename, self).__init__(request, uri, views, 'NCGA', None)

        self.id = uri.split('/')[-1]
        self.auth_id = self.id.split('_')[-1]

        self.hasName = {
            'uri': 'http://linked.data.gov.au/def/placenames/',
            'label': 'from National Composite Gazetteer of Australia (beta version 0.2):',
            'comment': 'The Entity has a name (label) which is a text sting.',
            'value': None
        }

        self.register = {
            'label': None,
            'uri': None
        }

        self.featureType = {
            'label': None,
            'uri': None
        }

        self.hasCategory = {
            'label': None,
            'uri': None
        }

        self.hasGroup = {
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

        self.authority = {
            'label': None,
            'web': None
        }
        self.email = None

        self.modifiedDate = None

        self.hasPronunciation = None   # None == don't display
        # pronunciation will only be displyed on webpage if it exists

        q = '''
            SELECT 
              	"NAME",
                "AUTHORITY",
                "SUPPLY_DATE", 
                "FEATURE",
                "CATEGORY",
                "GROUP",
                "LATITUDE",
                "LONGITUDE"
            FROM "PLACENAMES"
            WHERE "ID" = '{}'
        '''.format(self.id)

        for placename in conf.db_select(q):
            # set up x y location from database
            self.y = placename[6]
            self.x = placename[7]

            self.hasName['value'] = str(placename[0])

            self.featureType['label'] = str(placename[3])
            self.featureType['uri'] = 'http://vocabs.ands.org.au/repository/api/lda/ga/place-type/v1-0/resource?' \
                                      'uri=http://pid.geoscience.gov.au/def/voc/ga/PlaceType/' + str(placename[3])\
                                      .replace(' ','_')

            self.hasCategory['label'] = str(placename[4])
            self.hasCategory['uri'] = 'http://vocabs.ands.org.au/repository/api/lda/ga/place-type/v1-0/resource?' \
                                      'uri=http://pid.geoscience.gov.au/def/voc/ga/PlaceType/' + str(placename[4])\
                                      .replace(' ','_')

            self.hasGroup['label'] = str(placename[5])
            self.hasGroup['uri'] = 'http://vocabs.ands.org.au/repository/api/lda/ga/place-type/v1-0/resource?' \
                                   'uri=http://pid.geoscience.gov.au/def/voc/ga/PlaceType/' + str(placename[5])\
                                   .replace(' ','_')

            self.authority['label'] = (NAME_AUTHORITIES[str(placename[1])]['label'])
            self.authority['web'] = (NAME_AUTHORITIES[str(placename[1])]['web'])
            self.email = (NAME_AUTHORITIES[str(placename[1])]['email'])

            self.register['uri'] = (GAZETTEERS[str(placename[1])]['uri_id'])
            self.register['label'] = (GAZETTEERS[str(placename[1])]['label'])

            self.supplyDate = placename[2]
            #DGGS function
            resolution = 9
            # coords = (longi, lati)  # format required like this
            coords = (self.x, self.y)
            self.thisCell = rdggs.cell_from_point(resolution, coords, plane=False)  # false = on the elipsoidal curve


    def render(self):
        if self.view == 'alternates':
            return self._render_alternates_view()   # this function is in Renderer
        elif self.format in ['text/turtle', 'application/ld+json']:
            return self.export_rdf(self.view)                # this one exists below
        else:  # default is HTML response: self.format == 'text/html':
            return self.export_html(self.view)               # this one exists below


    def export_html(self, model_view='NCGA'):
        if model_view == 'NCGA':
            html_page = 'placename_ncga.html'
        else:
            html_page = 'placename.html'
        return Response(        # Response is a Flask class imported at the top of this script
            render_template(     # render_template is also a Flask module
                html_page,   # uses the placenames.html template send all this data to it.
                id=self.id,
                hasName=self.hasName,
                hasPronunciation=self.hasPronunciation,
                hasFeature = self.featureType,
                featureType = self.featureType,
                featureTypeURI= 'http://pid.geoscience.gov.au/def/voc/ga/PlaceType/' + str(self.featureType),
                hasCategory = self.hasCategory,
                hasGroup = self.hasGroup,
                authority=self.authority,
                authority_email = self.email,
                register=self.register,
                hasNameFormality=self.hasNameFormality,
                supplyDate=self.supplyDate,
                longitude = self.x,
                latitude = self.y,
                ausPIX_DGGS = self.thisCell
                # schemaorg=self.export_schemaorg()
            ),
            status=200,
            mimetype='text/html'
        )
        # if we had multiple views, here we would handle a request for an illegal view
        # return NotImplementedError("HTML representation of View '{}' is not implemented.".format(view))

    def _generate_wkt(self):
        if self.id is not None and self.x is not None and self.y is not None:
            # return '<http://www.opengis.net/def/crs/EPSG/0/4326> POINT({} {})'.format(self.x, self.y)
            return 'POINT({} {})'.format(self.y, self.x)
        else:
            return ''

    def _generate_dggs(self):
        if self.id is not None and self.thisCell is not None:
            return '{}'.format(self.thisCell)
        else:
            return ''

    def export_rdf(self, model_view='NCGA'):
        g = Graph()  # make instance of a RDF graph

        # namespace declarations
        dcterms = Namespace('http://purl.org/dc/terms/')  # already imported
        g.bind('dcterms', dcterms)
        geo = Namespace('http://www.opengis.net/ont/geosparql#')
        g.bind('geo', geo)
        owl = Namespace('http://www.w3.org/2002/07/owl#')
        g.bind('owl', owl)
        rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
        g.bind('rdfs', rdfs)

        # specific to placename datasdet
        place = Namespace('http://linked.data.gov.au/dataset/placenames/place/')
        g.bind('place', place)
        pname = URIRef('http://linked.data.gov.au/dataset/placenames/placenames/')
        g.bind('pname', pname)
        # made the cell ID the subject of the triples
        auspix = URIRef('http://ec2-52-63-73-113.ap-southeast-2.compute.amazonaws.com/AusPIX-DGGS-dataset/')
        g.bind('auspix', auspix)
        pn = Namespace('http://linked.data.gov.au/def/placenames/')
        g.bind('pno', pn)

        geox = Namespace('http://linked.data.gov.au/def/geox#')
        g.bind('geox', geox)
        g.bind('xsd', XSD)
        sf = Namespace('http://www.opengis.net/ont/sf#')
        g.bind('sf', sf)
        ptype = Namespace('http://pid.geoscience.gov.au/def/voc/ga/PlaceType/')
        g.bind('ptype', ptype)

        # build the graphs
        official_placename = URIRef('{}{}'.format(pname, self.id))
        this_place = URIRef('{}{}'.format(place, self.id))
        g.add((official_placename, RDF.type, URIRef(pn + 'OfficialPlaceName')))
        g.add((official_placename, dcterms.identifier, Literal(self.id, datatype=pn.ID_GAZ)))
        g.add((official_placename, dcterms.identifier, Literal(self.auth_id, datatype=pn.ID_AUTH)))
        g.add((official_placename, dcterms.issued, Literal(str(self.supplyDate), datatype=XSD.dateTime)))
        g.add((official_placename, pn.name, Literal(self.hasName['value'], lang='en-AU')))
        g.add((official_placename, pn.placeNameOf, this_place))
        g.add((official_placename, pn.wasNamedBy, URIRef(self.authority['web'])))
        g.add((official_placename, rdfs.label, Literal(self.hasName['value'])))

        # if NCGA view, add the place info as well
        if model_view == 'NCGA':
            g.add((this_place, RDF.type, URIRef(pn + 'Place')))
            g.add((this_place, dcterms.identifier, Literal(self.id, datatype=pn.ID_GAZ)))
            g.add((this_place, dcterms.identifier, Literal(self.auth_id, datatype=pn.ID_AUTH)))

            place_point = BNode()
            g.add((place_point, RDF.type, URIRef(sf + 'Point')))
            g.add((place_point, geo.asWKT, Literal(self._generate_wkt(), datatype=geo.wktLiteral)))
            g.add((this_place, geo.hasGeometry, place_point))

            place_dggs = BNode()
            g.add((place_dggs, RDF.type, URIRef(geo + 'Geometry')))
            g.add((place_dggs, geo.asDGGS, Literal(self._generate_dggs(), datatype=geox.dggsLiteral)))
            g.add((this_place, geo.hasGeometry, place_dggs))

            g.add((this_place, pn.hasPlaceClassification, URIRef(ptype + self.featureType['label'])))
            g.add((this_place, pn.hasPlaceClassification, URIRef(ptype + self.hasCategory['label'])))
            g.add((this_place, pn.hasPlaceClassification, URIRef(ptype + self.hasGroup['label'])))
            g.add((this_place, pn.hasPlaceName, official_placename))

        if self.format == 'text/turtle':
            return Response(
                g.serialize(format='turtle'),
                mimetype = 'text/turtle'
            )
        else: # JSON-LD
            return Response(
                g.serialize(format='json-ld'),
                mimetype = 'application/ld+json'
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
    pass



