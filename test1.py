import pandas as pd
import requests
from bs4 import BeautifulSoup
import streamlit as st
from datetime import *
from streamlit_folium import folium_static
import folium
from folium.plugins import MarkerCluster
import json
from folium.features import GeoJson, GeoJsonTooltip, GeoJsonPopup

#Block for current time and date
time = datetime.now()
day = date.today()
current_time = time.strftime("%H:%M:%S")
current_day = day.strftime("%B %d, %Y")

#Application title and basic info
st.title('COVID-19 pandemic tracker')
st.write('Data sources:')
st.write('Scrapping webpage:', 'https://www.worldometers.info/coronavirus/')
st.write('For geolocation:', 'https://clck.ru/U5wL4')
st.write('Date when information updated:', current_time, '-', current_day, '(GMT+6)')

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
Covid = Covid.rename(columns={'Country,Other': 'Country'})
Covid['Country'] = Covid['Country'].replace(['Réunion'], ['Reunion'])
Covid['Country'] = Covid['Country'].replace(['Curaçao'], ['Curacao'])

#Separate DataFrame for Continents
Covid_Continents_test = Covid.drop(Covid.index[7:])
Covid_Continents = Covid_Continents_test.sort_values(by=['TotalCases'], ascending=False)
Covid_Continents = Covid_Continents.reset_index(drop=True)
Covid_Continents = Covid_Continents.fillna('-')
Covid_Continents = Covid_Continents.rename(columns={'Country': 'Continents'})

#Separate DataFrame for Countries
Covid_Countries_test = Covid.drop(Covid.index[0:7])
Covid_Countries = Covid_Countries_test.reset_index(drop=True)
Covid_Countries = Covid_Countries.fillna(0)

#For displaying table of World and all continents(except Antarctica) data
st.write("""## Table of World and all continents(except Antarctica) data""")
data_continents = pd.DataFrame(Covid_Continents, columns=['Continents', 'TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths', 'TotalRecovered', 'NewRecovered', 'ActiveCases'])
st.table(data_continents)

#For taking geolocation(latitude, longitude) for each country
Coordinates = pd.read_csv('Coordinates.csv') #Used data from kaggle(link above)
df = pd.DataFrame(Coordinates)

Lat = list(df['latitude'])
Lon = list(df['longitude'])
Cou = list(df['country'])
Country_Code = list(df['country_code'])

latitude = []
longitude = []
Code = []

for i in (Covid_Countries['Country']):
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

#Filtering data by Continents

default_Attributes = ['TotalCases', 'NewCases', 'TotalDeaths', 'NewDeaths', 'TotalRecovered', 'NewRecovered', 'ActiveCases']
list_of_columns = list(Covid_Countries.columns)

st.write("""## For filtering data by Continents""")
For_Continent = []
for i in list_of_columns:
    if i != 'Continent' and i != 'Country':
        For_Continent.append(i)
Selected_Continent = st.multiselect('Continent and Other', list(sorted(set(Covid_Countries['Continent']))))
Selected_Attributes_for_Continent = st.multiselect('Attribute', For_Continent, default_Attributes)

Attributes_for_Continent = ['Continent', 'Country']

for i in Selected_Attributes_for_Continent:
    Attributes_for_Continent.append(i)

Covid_Countries_filter_test1 = Covid_Countries[Attributes_for_Continent]
Covid_Countries_filter1 = Covid_Countries_filter_test1[Covid_Countries_filter_test1.Continent.isin(Selected_Continent)]
st.dataframe(Covid_Countries_filter1)

#Filtering data by Countries
st.write("""## For filtering data by Countries""")

Selected_Countries = st.multiselect('Country', list(sorted(Covid_Countries['Country'])))
Selected_Attributes_for_Countries = st.multiselect('Attribute', list_of_columns[1:], default_Attributes)

Attributes_for_Countries = ['Country']

for i in Selected_Attributes_for_Countries:
    Attributes_for_Countries.append(i)

Covid_Countries_filter_test = Covid_Countries[Attributes_for_Countries]
Covid_Countries_filter = Covid_Countries_filter_test[Covid_Countries_filter_test.Country.isin(Selected_Countries)]
st.dataframe(Covid_Countries_filter)

#SELECTBOX widgets MAP
metrics = ['TotalCases', 'TotalDeaths', 'TotalRecovered', 'ActiveCases', 'TotalTests','Population']
cols = st.selectbox('Covid metric to view', metrics)

# let's ask the user which column should be used as Index
if cols in metrics:
    metric_to_show_in_covid_Layer = cols

#Load Data
world_map = json.load(open('mpmp.json'))
data = Covid_Countries
Country = data['Country']
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
    folium.Marker(location=[lat, lon], popup=[Country,elevation], icon=folium.Icon(color = color_change(elevation))).add_to(map)

folium_static(map)


#Create base map
map1 = folium.Map(location=[0,0], zoom_start = 2)
max1 = max(list(data["TotalCases"]))
min1 = min(list(data["TotalCases"]))
#Method to create Choropleth map, All parameters are mandatory
popup = GeoJsonPopup(
    fields=['name', 'TotalCases', 'TotalDeaths', 'ActiveCases', 'Population'],
    aliases=['Country:', 'Total Cases:', 'TotalDeaths', 'ActiveCases', 'Population'],
    localize=True,
    labels=True,
    style="background-color: yellow;",
)
tooltip = GeoJsonTooltip(
    fields=['name', 'TotalCases', 'TotalDeaths', 'ActiveCases', 'Population'],
    aliases=['Country:', 'Total Cases:', 'TotalDeaths', 'ActiveCases', 'Population'],
    localize=True,
    sticky=False,
    labels=True,
    max_width=800,
)
heatmap = folium.Choropleth(
    geo_data=world_map, data=data,
    name='Covid-19',
    columns=['Country', 'TotalCases'],
    key_on='properties.name',
    bins=[min1, 10000, 50000, 100000, 300000, 500000, 1000000, 5000000, 15000000, max1+1],
    fill_color='YlOrRd',
    fill_opacity=0.9, line_opacity=0.6,
    legend_name='Total Cases',
    highlight=True,
).add_to(map1)
folium.GeoJson(
    world_map,
    style_function=lambda feature: {
        'fillColor': '#ffff00',
        'color': 'black',
        'weight': 0.2,
        'dashArray': '5, 5'
    },
    tooltip=tooltip,
    popup=popup).add_to(heatmap)

folium_static(map1)
