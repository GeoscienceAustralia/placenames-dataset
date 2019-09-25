# -*- coding: utf-8 -*-
import decimal
import json
import os
from flask import render_template, Response

import folium
import placenames._conf as conf
from pyldapi import Renderer, View
from rdflib import Graph, URIRef, RDF, XSD, Namespace, Literal

from .gazetteer import GAZETTEERS, NAME_AUTHORITIES

# for DGGS zone attribution
from AusPIXengine import dggs
rdggs = dggs.RHEALPixDGGS()


#import branca


class Placename(Renderer):
    """
    This class represents a placename and methods in this class allow a placename to be loaded from the GA placenames database
    and to be exported in a number of formats including RDF, according to the 'PlaceNames Ontology'

    [[and an expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.]]??
    """

    def __init__(self, request, uri):
        views = {
            'pn': View(
                'Place Names View',
                'This view is the standard view delivered by the Place Names dataset in accordance with the '
                'Place Names Profile',
                ['text/html', 'text/turtle', 'application/ld+json'],
                'text/html'
            )
        }

        super(Placename, self).__init__(request, uri, views, 'pn', None)

        self.id = uri.split('/')[-1]

        self.hasName = {
            'uri': 'http://linked.data.gov.au/def/placenames/',
            'label': 'from National Composite Gazetteer of Australia (beta version 0.2):',
            'comment': 'The Entity has a name (label) which is a text sting.',
            'value': None
        }

        self.thisCell = {
            'label': None,
            'uri': None
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
            # for item in placename:
            #     print(item)
            #print(placename)
            #print(placename[0], placename[1], placename[2], placename[3], placename[4], placename[5]), placename[6], placename[7]
            # set up x y location from database
            self.y = placename[6]
            self.x = placename[7]

            self.hasName['value'] = str(placename[0]) + " (" + str(placename[3]).capitalize() + ")"

            self.featureType['label'] = str(placename[3])
            self.featureType['uri'] = 'http://vocabs.ands.org.au/repository/api/lda/ga/place-type/v1-0/resource?uri=http://pid.geoscience.gov.au/def/voc/ga/PlaceType/' + str(placename[3]).replace(' ','_')

            #self.hasCategory = str(placename[4])
            self.hasCategory['label'] = str(placename[4])
            self.hasCategory['uri'] = 'http://vocabs.ands.org.au/repository/api/lda/ga/place-type/v1-0/resource?uri=http://pid.geoscience.gov.au/def/voc/ga/PlaceType/' + str(placename[4]).replace(' ','_')

            #self.hasGroup = str(placename[5])
            self.hasGroup['label'] = str(placename[5])
            self.hasGroup['uri'] = 'http://vocabs.ands.org.au/repository/api/lda/ga/place-type/v1-0/resource?uri=http://pid.geoscience.gov.au/def/voc/ga/PlaceType/' + str(placename[5]).replace(' ','_')

            self.authority['label'] = (NAME_AUTHORITIES[str(placename[1])]['label'])
            self.authority['web'] = (NAME_AUTHORITIES[str(placename[1])]['web'])
            self.email = (NAME_AUTHORITIES[str(placename[1])]['email'])

            #print('authority', self.authority)

            self.register['uri'] = (GAZETTEERS[str(placename[1])]['uri_id'])
            self.register['label'] = (GAZETTEERS[str(placename[1])]['label'])

            #self.register['uri'] = 'http://linked.data.gov.au/dataset/placenames/gazetteer/' + str(placename[1])

            #print('name auth', naming_authorities[str(placename[1])]['label'])

            self.supplyDate = placename[2]
            #DGGS function
            resolution = 7
            self.thisDGGSCell = None

            # coords = (longi, lati)  # format required like this
            coords = (self.x, self.y)
            self.thisDGGScell = rdggs.cell_from_point(resolution, coords, plane=False)  # false = on the elipsoidal curve
            print(self.thisDGGScell)
            self.thisCell['label'] = str(self.thisDGGScell)
            self.thisCell['uri']= 'http://ec2-52-63-73-113.ap-southeast-2.compute.amazonaws.com/AusPIX-DGGS-dataset/ausPIX/' + str(self.thisDGGScell)

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
                'placename.html',   # uses the placenames.html template send all this data to it.
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

    def export_rdf(self):
        g = Graph()  # make instance of a RDF graph

        PN = Namespace('http://linked.data.gov.au/def/placename/')   #rdf neamespace declaration
        g.bind('pn', PN)


        #generate all the data available as rdf for export to rdf file
        me = URIRef(self.uri)   # URIRef is a RDF class
        g.add((me, RDF.type, URIRef('http://linked.data.gov.au/def/placename/PlaceName')))  # PN.PlaceName))
        g.add((me, PN.hasName, Literal(self.hasName['value'], datatype=XSD.string)))
        g.add((me, PN.longitude, Literal(self.x, datatype=XSD.float )))
        g.add((me, PN.latitude, Literal(self.y, datatype=XSD.float)))
        g.add((me, PN.featureType, Literal(self.featureType, datatype=XSD.string)))
        g.add((me, PN.hasCategory, Literal(self.hasCategory, datatype=XSD.string)))
        g.add((me, PN.hasGroup, Literal(self.hasGroup, datatype=XSD.string)))
        g.add((me, PN.hasRegister, Literal(self.register, datatype=XSD.string)))
        g.add((me, PN.hasNameFormality, Literal(self.hasNameFormality, datatype=XSD.string)))
        g.add((me, PN.ausPIX_DGGS, Literal(str(self.thisCell), datatype=XSD.string)))
        g.add((me, PN.supplyDate, Literal(str(self.supplyDate), datatype=XSD.string)))




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

    print('main process has not been built yet - when build it will test ask for a placename like the code Gnaf above')


