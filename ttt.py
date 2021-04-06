import pandas as pd
import geopandas
import requests
from bs4 import BeautifulSoup
import streamlit as st
from streamlit_folium import folium_static
import folium
from folium.plugins import MarkerCluster
import json
from folium.features import GeoJson, GeoJsonTooltip, GeoJsonPopup

#Parser block
url = 'https://www.worldometers.info/coronavirus/'
req = requests.get(url)
page = BeautifulSoup(req.content, 'html.parser')
table = page.find_all('table', id="main_table_countries_today")[0]
Covid_test = pd.read_html(str(table), displayed_only=False)[0]

#Make a pure worksheet without any bugs
Covid = Covid_test.drop(Covid_test.index[[6, 229, 230, 231, 232, 233, 234, 235, 236]])
Covid['Continent'] = Covid['Continent'].replace([None], 'Cruise ship')
Covid = Covid.drop('#', 1)

#Separate DataFrame for Continents
Covid_Continents_test = Covid.drop(Covid.index[7:])
Covid_Continents = Covid_Continents_test.sort_values(by=['TotalCases'], ascending=False)
Covid_Continents = Covid_Continents.reset_index(drop=True)
Covid_Continents = Covid_Continents.fillna('-')

#Separate DataFrame for Countries
Covid_Countries_test = Covid.drop(Covid.index[0:7])
Covid_Countries = Covid_Countries_test.reset_index(drop=True)
Covid_Countries = Covid_Countries.fillna(0)

#For taking geolocation(latitude, longitude) for each country
Lat = []
Lon = []
Cou = []
Country_Code = []

data = pd.read_csv('Coordinates.csv') #Used data from kaggle(link above)
df = pd.DataFrame(data)
Lat = list(df['latitude'])
Lon = list(df['longitude'])
Cou = list(df['country'])
Country_Code = list(df['country_code'])

latitude = []
longitude = []
Code = []
for i in (Covid_Countries['Country,Other']):
    for k, index in enumerate(Cou):
        if i == index:
            latitude.append(Lat[k])
            longitude.append(Lon[k])
            Code.append(Country_Code[k])
        else:
            continue

Covid_Countries['latitude'] = latitude
Covid_Countries['longitude'] = longitude
Covid_Countries['Country_Code'] = Code

metrics = ['TotalCases', 'TotalDeaths', 'TotalRecovered', 'ActiveCases', 'TotalTests']
cols = st.selectbox('Covid metric to view', metrics)

# let's ask the user which column should be used as Index
if cols in metrics:
    metric_to_show_in_covid_Layer = cols

#Load Data
geo_data = json.load(open("custom.geo.json"))
data = Covid_Countries
Country = data['Country,Other']
lat = data['latitude']
lon = data['longitude']
code = data['Country_Code']
elevation = data[metric_to_show_in_covid_Layer]

def color_change(elev):
    if(elev < 1000):
        return('green')
    elif(1000 <= elev <10000):
        return('orange')
    else:
        return('red')

map = folium.Map(location=[0,0], zoom_start = 2)

marker_cluster = MarkerCluster().add_to(map)

for lat, lon, elevation, Country in zip(lat, lon, elevation, Country):
    folium.Marker(location=[lat, lon], popup=str(elevation), icon=folium.Icon(color = color_change(elevation))).add_to(marker_cluster)

folium_static(map)

#Create base map
map1 = folium.Map(location=[0,0], zoom_start = 2)

#Method to create Choropleth map, All parameters are mandatory
heatmap = folium.Choropleth(
    geo_data=geo_data, data=data,
    name='Covid-19',
    columns=['Country,Other', metric_to_show_in_covid_Layer],
    key_on='feature.properties.name',
    fill_color='YlGn', fill_opacity=0.7, line_opacity=0.4,
    legend_name='Covid Cases',
    highlight=True,
).add_to(map1)

f = folium.Figure(width=680, height=750)
m = folium.Map([23.53, 78.3], maxZoom=6, minZoom=4.8, zoom_control=True, zoom_start=5,
               scrollWheelZoom=True, maxBounds=[[40, 68], [6, 97]], tiles=white_tile, attr='white tile',
               dragging=True).add_to(f)
# Add layers for Popup and Tooltips
popup = GeoJsonPopup(
    fields=['st_nm', 'cartodb_id'],
    aliases=['State', "Data points"],
    localize=True,
    labels=True,
    style="background-color: yellow;",
)
tooltip = GeoJsonTooltip(
    fields=['st_nm', 'cartodb_id'],
    aliases=['State', "Data points"],
    localize=True,
    sticky=False,
    labels=True,
    style="""
        background-color: #F0EFEF;
        border: 1px solid black;
        border-radius: 3px;
        box-shadow: 3px;
    """,
    max_width=800,
)
# Add choropleth layer
g = folium.Choropleth(
    geo_data=india,
    data=gdf,
    columns=['st_nm', 'cartodb_id'],
    key_on='properties.st_nm',
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.4,
    legend_name='Data Points',
    highlight=True,

).add_to(m)
folium.GeoJson(
    india,
    style_function=lambda feature: {
        'fillColor': '#ffff00',
        'color': 'black',
        'weight': 0.2,
        'dashArray': '5, 5'
    },
    tooltip=tooltip,
    popup=popup).add_to(g)
folium_static(map1)
