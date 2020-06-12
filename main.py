import folium
from geopy.distance import geodesic
import json


centre = [53.3620621,-1.5036596]# nickys #[53.39064,-1.53328]#mine
m = folium.Map(
    location=centre,
    tiles='Stamen Terrain',
    zoom_start=10,
    title = "Our Map"
    )


sitebase = "http://www.megalithic.co.uk/"
sites = "le_ajaxmapdata.php?bbox=-2.40875244140625,53.03543290697411,-0.65643310546875,53.78361508880527"

site ="megaliths.json" #"https://www.megalithic.co.uk/le_ajaxmapdata.php?bbox=-2.467803955078125,53.15088840824353,-0.597381591796875,53.669866612978275"
types = {}



article = "article.php?sid="

file=open(site)
data = json.load(file)

orglen = len(data["features"])
icons = "images/mapic/"#tr22.gif


def near(item):
    print(item)
    dist =geodesic((centre[1],centre[0]), item["geometry"]["coordinates"]).miles
    #print(dist)
    if int(item["properties"]["acc"]) < 5:
        return False
    if item["properties"]["sitetype"] in ["Museum"]:
        return False
    return dist<=30

def process(item):
    item["properties"]["url"] = '<a href="'+sitebase + article + item["properties"]["sid"]+'" target="_blank">'+item["properties"]["title"]+'</a>'
    dist =geodesic((centre[1],centre[0]), item["geometry"]["coordinates"]).miles

    return item

data["features"] = [ process(item) for item in data["features"] if near(item) ]



currlen = len(data["features"])

print(orglen, currlen)

def toGraphHopperService(item):
    return {
    "name": item["properties"]["title"],
    "address":{
        "lon":item["geometry"]["coordinates"][1],
        "lat":item["geometry"]["coordinates"][0]
        },
    "duration":30*60*1000
    }

def getVehicle(id):
    return {
      "vehicle_id": "camper "+str(id),
      "type_id":"camper",
      "start_address": {
          "location_id": "nicky's",
          "lon": centre[1],
          "lat": centre[0]
      },
      "end_address": {
          "location_id": "nicky's",
          "lon": centre[1],
          "lat": centre[0]
      },
      "earliest_start":13*60*60,
      "latest_end":17*60*60

    }

request = {
    "vehicles" : [getVehicle(id) for id in range(1,5)],
    "vehicle_types": {
                "type_id":"camper",
                "profile": "car"
            },
    "services": [ toGraphHopperService(item) for item in data["features"]],

}

def sites_function(feature):
    return {'click':None}

def sites_styles(item):
    icon_url = sitebase+icons+item["properties"]["icon"]+".gif"
    site_icon = folium.features.CustomIcon(
        icon_url,
        icon_size=(14, 14)
    )
    #item["icon"] = site_icon

    #return item
    return {
        "icon": site_icon
    }


siteslayer = folium.GeoJson(
    data,#site,#base+sites,
    name='Sites',
    #highlight_function = sites_function
    #style_function = sites_styles,

    popup= folium.features.GeoJsonPopup(
        fields=['url', 'sitetype', 'cond', 'amb', 'acc'],
        aliases=['Site', 'Type',  'Condition', 'Ambience', 'Access'],
        labels=True,
        show=True,
        click=None
    ),


    ).add_to(m)
'''

).add_to(siteslayer)

'''

folium.features.LatLngPopup().add_to(m)

m.fit_bounds(m.get_bounds(),padding=(10,10))





m.save('index.html')
