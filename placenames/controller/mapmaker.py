import foliumOLD
import branca

# create a new map object
m = foliumOLD.Map(location=[-66.27777778, 110.55], zoom_start=13)


tooltip = 'Click for more information'


# create markers
foliumOLD.Marker([-66.27777778, 110.55],
                 popup = '<strong>Brown Bay</strong>',
                 tooltip = tooltip).add_to(m),

foliumOLD.Marker([-66.24, 110.57],
                 popup = '<strong>Location One</strong>',
                 tooltip = tooltip).add_to(m),

# generate map
m.save(r'C:\Users\u82871\PycharmProjects\PlacenamesAPI\placenames\view\templates/map.html')


