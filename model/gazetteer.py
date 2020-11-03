# -*- coding: utf-8 -*-

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
NAME_AUTHORITIES = {
    'AAD': {
        'label': 'Australian Antarctic Place Names Gazetteer',
        'web': 'http://data.aad.gov.au',
        'email':'placenames@antarctica.gov.au'
            },
    'ACT': {
        'label': 'ACT Environment, Planning and Sustainable Development Directorate',
        'web': 'https://www.planning.act.gov.au/tools_resources/place_names',
        'email':'placenames@act.gov.au  '
    },
    'AHO': {
        'label': 'Australian Hydrographic Office',
        'web': 'http://www.hydro.gov.au/',
        'email':'datacentre@hydro.gov.au'
    },
    'NSW': {
        'label': 'NSW Spatial Services',
        'web': 'http://www.gnb.nsw.gov.au',
        'email': 'Ss-gnb@finance.nsw.gov.au'
    },
    'NT': {
        'label': 'NT Dept of Infrastructure, Planning and Logistics',
        'web': 'https://www.ntlis.nt.gov.au/placenames/',
        'email':'place.names@nt.gov.au'
    },
    'QLD': {
        'label': 'QLD Dept of Natural Resources, Mines and Energy ',
        'web': 'https://www.dnrm.qld.gov.au/qld/environment/land/place-names/search',
        'email':'qldplacenames@dnrme.qld.gov.au'
    },
    'SA': {
        'label': 'SA Dept for Transport, Energy & Infrastructure',
        'web': 'www.sa.gov.au/landservices/namingproposals',
        'email':'LSGPlaceNames@sa.gov.au'
    },
    'TAS': {
        'label': 'Tasmanian Dept of Primary Industries, Parks, Water and Environment',
        'web': 'www.placenames.tas.gov.au',
        'email':'Nomenclature.Office@dpipwe.tas.gov.au'
    },
    'VIC': {
        'label': 'Victorian Dept of Environment, Land, Water & Planning',
        'web': 'https://www.propertyandlandtitles.vic.gov.au/naming-places-features-and-roads/naming-rules-for-places-in-victoria',
        'email':'geo.names@delwp.vic.gov.au'
    },
    'WA': {
        'label': 'WA Landgate',
        'web': 'http://www.landgate.wa.gov.au',
        'email':'geographicnames@landgate.wa.gov.au  '
    }
}




