import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
from streamlit_folium import folium_static
import folium
from folium.plugins import MarkerCluster

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

data = pd.read_csv('Coordinates.csv') #Used data from kaggle(link above)
df = pd.DataFrame(data)
Lat = list(df['latitude'])
Lon = list(df['longitude'])
Cou = list(df['country'])

latitude = []
longitude = []

metrics = ['TotalCases', 'TotalDeaths', 'TotalRecovered', 'ActiveCases', 'TotalTests']
cols = st.selectbox('Covid metric to view', metrics)

# let's ask the user which column should be used as Index
if cols in metrics:
    metric_to_show_in_covid_Layer = cols

for i in (Covid_Countries['Country,Other']):
    for k, index in enumerate(Cou):
        if i == index:
            latitude.append(Lat[k])
            longitude.append(Lon[k])
        else:
            continue

Covid_Countries['latitude'] = latitude
Covid_Countries['longitude'] = longitude

data = Covid_Countries
lat = data['latitude']
lon = data['longitude']
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

for lat, lon, elevation in zip(lat, lon, elevation):
    folium.Marker(location=[lat, lon], popup=str(elevation), icon=folium.Icon(color = color_change(elevation))).add_to(marker_cluster)

folium_static(map)





