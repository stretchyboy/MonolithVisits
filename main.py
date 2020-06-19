import folium
from geopy.distance import geodesic
import json
from geocluster import GeoCluster
from urllib.parse import urlencode


colors = ["red", "blue", "green", "purple", "orange", "darkred",
    "lightred", "beige", "darkblue", "darkgreen", "cadetblue",
    "darkpurple", "white", "pink", "lightblue", "lightgreen",
    "gray", "black", "lightgray"]


radius = 20 #miles
maxcrowflies = 50
maxsites = 4
closestsitetosurrentnext = False
furthestfirst = True

center = [53.3620621,-1.5036596]# nickys #[53.39064,-1.53328]#mine
m = folium.Map(
    location=center,
    tiles='OpenStreetMap', #'Stamen Terrain',
    zoom_start=10,
    title = "Our Map",
    control_scale = True
    )

folium.map.Layer('Stamen Terrain').add_to(m)


sitebase = "http://www.megalithic.co.uk/"
sites = "le_ajaxmapdata.php?bbox=-2.40875244140625,53.03543290697411,-0.65643310546875,53.78361508880527"

site ="megaliths.json" #"https://www.megalithic.co.uk/le_ajaxmapdata.php?bbox=-2.467803955078125,53.15088840824353,-0.597381591796875,53.669866612978275"
types = {}

done = [18768]

article = "article.php?sid="

file=open(site)
data = json.load(file)

orglen = len(data["features"])
icons = "images/mapic/"#tr22.gif


def near(item):
    print(item)
    dist =geodesic((center[1],center[0]), item["geometry"]["coordinates"]).miles
    #print(dist)
    if int(item["properties"]["acc"]) < 5:
        return False
    if item["properties"]["sitetype"] in ["Museum"]:
        return False
    if int(item["properties"]["sid"]) in done:
        return False
    return dist<=radius

def process(item):
    item["properties"]["url"] = '<a href="'+sitebase + article + item["properties"]["sid"]+'" target="_blank">'+item["properties"]["title"]+'</a>'
    dist =geodesic((center[1],center[0]), item["geometry"]["coordinates"]).miles
    item["properties"]["dist"] = dist
    item['lat'] = item["geometry"]["coordinates"][1]
    item['lng'] = item["geometry"]["coordinates"][0]

    return item

data["features"] = [ process(item) for item in data["features"] if near(item) ]

sorted_sites = sorted(data["features"],key=lambda item: item["properties"]["dist"])



togroup = sorted_sites

def processlocal(item):
    localdist =geodesic(currcoords, item["geometry"]["coordinates"]).miles
    item["properties"]["localdist"] = localdist


    return item



groups = []
grouped = []
groupnum = 0
while len(togroup):
    '''
    pop the nearest site
    add the closest to that site until max distance is reached
    '''
    togroup.sort(key=lambda item: item["properties"]["dist"])
    if furthestfirst:
        togroup.reverse()
    groupnum += 1
    group = []
    group.append(togroup.pop(0))
    grouped.append(group[-1])
    currdist = grouped[-1]["properties"]["dist"]
    grouped[-1]["properties"]['group'] = groupnum
    currcoords = group[-1]["geometry"]["coordinates"]

    togroup = [ processlocal(item) for item in togroup ]

    while len(togroup):
        if len(group) >= maxsites:
            break
        togroup = [ processlocal(item) for item in togroup ]
        togroup.sort(key=lambda item: item["properties"]["localdist"])
        if currdist + togroup[0]["properties"]["localdist"] +togroup[0]["properties"]["dist"] > maxcrowflies:
            break
        currdist += togroup[0]["properties"]["localdist"]
        group.append(togroup.pop(0))
        grouped.append(group[-1])
        grouped[-1]["properties"]['group'] = groupnum
        grouped[-1]["properties"]['tripdist'] = currdist
        if closestsitetosurrentnext:
            currcoords = grouped[-1]["geometry"]["coordinates"]



    currdist += grouped[-1]["properties"]["dist"]
    grouppoints = [(x["geometry"]["coordinates"][1], x["geometry"]["coordinates"][0]) for x in group]
    print(grouppoints)

    gbase = "https://www.google.com/maps/dir/?"

    googleparams=urlencode({
        "api":1,
        "origin":",".join([str(num) for num in center]),
        #"destination":",".join([str(num) for num in grouppoints[0]]),
        "destination":",".join([str(num) for num in center]),
        #"waypoints":"|".join([",".join([str(num) for num in coord]) for num in coord]) for coord in grouppoints])

        "waypoints":"|".join([",".join([str(x["geometry"]["coordinates"][1]), str(x["geometry"]["coordinates"][0])]) for x in group]),
        "waypoint_place_ids":"|".join([x["properties"]["title"] for x in group])
    })
    print(googleparams)
    grouppoints.insert(0,center)
    grouppoints.append(center)
    color = colors[(group[-1]["properties"]['group']-1)%len(colors)]
    text = "Trip: " +str(group[-1]["properties"]['group'])
    text += "  Dist :"+str(round(currdist,1))+ " Miles"
    text += ' <a target="_blank" href="'+gbase+googleparams+'">Route planner</a>'

    folium.vector_layers.PolyLine(
        grouppoints,
        #tooltip=text,
        popup=text,
        color=color
    ).add_to(m)

    '''datagroup = data
    datagroup["features"] = group
    groups.append(datagroup)
    '''
data["features"] = grouped
currlen = len(data["features"])

print(orglen, currlen)

def sites_function(feature):
    return {'click':None}


def sites_styles(item):

    color = colors[(item['properties']['group']-1)%len(colors)]
    print(color)
    return {
        'fillColor': color
    }
    '''icon_url = sitebase+icons+item["properties"]["icon"]+".gif"
    site_icon = folium.features.CustomIcon(
        icon_url,
        icon_size=(14, 14)
    )
    #item["icon"] = site_icon

    #return item
    return {
        "icon": site_icon
    }'''

style_function2 = lambda x: {'fillColor': '#ff0000'}

siteslayer = folium.GeoJson(
    data,#site,#base+sites,
    name='Sites',
    #highlight_function = sites_function
    style_function = style_function2,


    popup= folium.features.GeoJsonPopup(
        fields=['url', 'dist','group','sitetype', 'cond', 'amb', 'acc'],
        aliases=['Site', 'Miles','Trip','Type',  'Condition', 'Ambience', 'Access'],
        labels=True,
        show=True,
        click=None
    ),
    tooltip=folium.features.GeoJsonTooltip(
        fields=['url', 'dist','group','sitetype', 'cond', 'amb', 'acc'],
        aliases=['Site', 'Miles','Trip','Type',  'Condition', 'Ambience', 'Access'],
        labels=True,
        show=True,
        click=None
    ),
).add_to(m)
'''

).add_to(siteslayer)

'''

#folium.features.LatLngPopup().add_to(m)


m.fit_bounds(m.get_bounds(),padding=(10,10))

folium.map.LayerControl().add_to(m)




m.save('index.html')

'''

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
          "lon": center[1],
          "lat": center[0]
      },
      "end_address": {
          "location_id": "nicky's",
          "lon": center[1],
          "lat": center[0]
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
'''



'''
cluster = GeoCluster()

#west,south,east,north
north = 53.78361508880527
south = 53.03543290697411
east = -0.65643310546875
west = -2.40875244140625

cluster.set_bounds(north=north, south=south, east=east, west=west)
cluster.set_grid(4, 10)
cluster.populate(data)

data_clusturized_as_a_dictionary = cluster.to_json()

print("data_clusturized_as_a_dictionary", data_clusturized_as_a_dictionary)
'''
