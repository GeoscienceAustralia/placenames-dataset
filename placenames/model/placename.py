# -*- coding: utf-8 -*-
from flask import render_template, Response
from rdflib import Graph, URIRef, RDF, RDFS, XSD, OWL, Namespace, Literal, BNode
import placenames._conf as conf
from psycopg2 import sql
import json
import decimal
from pyldapi import Renderer, View


class Placename(Renderer):
    """
    This class represents an Address and methods in this class allow an Address to be loaded from the GNAF database
    and to be exported in a number of formats including RDF, according to the 'GNAF Ontology' and an
    expression of the Dublin Core ontology, HTML, XML in the form according to the AS4590 XML schema.
    """

    def __init__(self, request, uri):
        views = {
            'pn': View(
                'Plane Names View',
                'This view is the standard view delivered by the Place Names dataset in accordance with the '
                'Place Names Profile',
                ['text/html', 'text/turtle', 'application/ld+json'],
                'text/html'
            )
        }

        super(Placename, self).__init__(request, uri, views, 'pn', None)
        self.id = uri.split('/')[-1]

        self.hasName = {
            'uri': 'http://linked.data.gov.au/def/placename/hasName',
            'label': 'has name',
            'comment': 'The Entity has a name (label) which is a text sting.',
            'value': None
        }

        gazetteers = {
            'AAD': {
                'label': 'Australian Antarctica Gazetteer',
                'uri_id': 'aag'
            },
            'ACT': {
                'label': 'Australian Antarctica Gazetteer',
                'uri_id': 'aag'
            },
            'AHO': {
                'label': 'Australian Antarctica Gazetteer',
                'uri_id': 'aag'
            },
            'NSW': {
                'label': 'Australian Antarctica Gazetteer',
                'uri_id': 'aag'
            },
            'NT': {
                'label': 'Australian Antarctica Gazetteer',
                'uri_id': 'aag'
            },
            'QLD': {
                'label': 'Australian Antarctica Gazetteer',
                'uri_id': 'aag'
            },
            'SA': {
                'label': 'Australian Antarctica Gazetteer',
                'uri_id': 'aag'
            },
            'TAS': {
                'label': 'Australian Antarctica Gazetteer',
                'uri_id': 'aag'
            },
            'VIC': {
                'label': 'Australian Antarctica Gazetteer',
                'uri_id': 'aag'
            },
            'WA': {
                'label': 'Western Australia\'s Place Names Gazetteer',
                'uri_id': 'wa'
            }
        }

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

        q = '''
            SELECT 
              	"NAME",
                "AUTHORITY",
                "SUPPLY_DATE"
            FROM "PLACENAMES"
            WHERE "ID" = '{}'
        '''.format(self.id)
        for placename in conf.db_select(q):
            self.hasName['value'] = str(placename[0])
            self.register['label'] = str(placename[1])
            self.register['uri'] = 'http://linked.data.gov.au/dataset/placenames/gazetteer/' + str(placename[1])
            self.modifiedDate = placename[2]


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
            }
        }

    def render(self):
        if self.view == 'alternates':
            return self._render_alternates_view()
        elif self.format in ['text/turtle', 'application/ld+json']:
            return self.export_rdf()
        else:  # default is HTML response: self.format == 'text/html':
            return self.export_html()

    def export_html(self):
        return Response(
            render_template(
                'placename.html',
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
        g = Graph()

        PN = Namespace('http://linked.data.gov.au/def/placename/')
        g.bind('pn', PN)

        me = URIRef(self.uri)

        g.add((me, RDF.type, URIRef('http://linked.data.gov.au/def/placename/PlaceName')))  # PN.PlaceName))
        g.add((me, PN.hasName, Literal(self.hasName['value'], datatype=XSD.string)))

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

    def export_schemaorg(self):
        data = {
            '@context': 'http://schema.org',
            '@type': 'Place',
            'address': {
                '@type': 'PostalAddress',
                'streetAddress': self.address_string.split(',')[0],
                'addressLocality': self.locality_name,
                'addressRegion': self.state_prefLabel,
                'postalCode': self.postcode,
                'addressCountry': 'AU'
            },
            'geo': {
                '@type': 'GeoCoordinates',
                'latitude': self.latitude,
                'longitude': self.longitude
            },
            'name': 'Geocoded Address ' + self.id
        }

        return json.dumps(data, cls=DecimalEncoder)


if __name__ == '__main__':
    a = Address('GANSW703902211', focus=True)
    print(a.export_rdf().decode('utf-8'))

# has alias for which it can't get address subclass: GAACT715069724. Alias is GAACT718348352
# GAACT718348352 has subclass UnknownVillaAddress
