#!/usr/bin/env python
# coding: utf-8

# # Capstone Project: Melbourne Relocation Assistant 

# ### Import all relevant libraries

# In[53]:


# Library to handle requests for pulling data from online sources
import requests 

# Data analsysis library
import pandas as pd 

#import numpy as np # library to handle data in a vectorized manner

# Module to convert an address into latitude and longitude values
from geopy.geocoders import Nominatim 

# Libraries for displaying images
from IPython.display import Image 
from IPython.core.display import HTML 
    
# Tranforming json file into a pandas dataframe library
from pandas.io.json import json_normalize

# Library used for plotting maps and visualisations 
import folium 


# ### Build Foursquare ID used for running query 

# In[8]:


CLIENT_ID = 'SJ0P5AZDZ22XDSINA0UWM5SBSTYYJLGYJKFVRY1GSY0RUBHU' # your Foursquare ID
CLIENT_SECRET = 'KY0DTRFZHN4FR3P51GP3Q4HATIZ1VOQ2FLEHU4H2QB3EGRVH' # your Foursquare Secret
VERSION = '20180604'
LIMIT = 30


# ### Set location to central Melbourne for query and obtain coordinates 

# In[9]:


address = '91 Rose St, Fitzroy VIC '

geolocator = Nominatim(user_agent="foursquare_agent")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print(latitude, longitude)


# ### Pull data for public transport and bus stops 

# In[10]:


search_query1 = 'Train Station'
radius = 300000
url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, search_query1, radius, LIMIT)
pt_results = requests.get(url).json()

search_query2 = 'Bus Stop'
radius = 300000
url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, search_query2, radius, LIMIT)
bs_results = requests.get(url).json()

search_query1 = 'Grocery Store'
radius = 300000
url = 'https://api.foursquare.com/v2/venues/search?client_id={}&client_secret={}&ll={},{}&v={}&query={}&radius={}&limit={}'.format(CLIENT_ID, CLIENT_SECRET, latitude, longitude, VERSION, search_query1, radius, LIMIT)
gs_results = requests.get(url).json()


# ### Pull relevant part of JSON file and convert to dataframes

# In[11]:


pt_results = pt_results['response']['venues']
bs_results = bs_results['response']['venues']
gs_results = gs_results['response']['venues']

# Tranform public transport and bus stop results into dataframes
pt1 = pd.json_normalize(pt_results)
bs1 = pd.json_normalize(bs_results)
gs1 = pd.json_normalize(gs_results)


gs1.head()


# ### Filter dataframes to discard irrelevant information

# In[12]:


# Keep only columns that include venue name and location related information
pt_columns = ['name', 'categories'] + [col for col in pt1.columns if col.startswith('location.')] + ['id']
pt_filtered = pt1.loc[:, pt_columns]

bs_columns = ['name', 'categories'] + [col for col in bs1.columns if col.startswith('location.')] + ['id']
bs_filtered = bs1.loc[:, bs_columns]

gs_columns = ['name', 'categories'] + [col for col in gs1.columns if col.startswith('location.')] + ['id']
gs_filtered = gs1.loc[:, gs_columns]


# Function that extracts the category of the venue
def get_category_type(row):
    try:
        categories_list = row['categories']
    except:
        categories_list = row['venue.categories']
        
    if len(categories_list) == 0:
        return None
    else:
        return categories_list[0]['name']

# Filter the category for each row
pt_filtered['categories'] = pt_filtered.apply(get_category_type, axis=1)
bs_filtered['categories'] = bs_filtered.apply(get_category_type, axis=1)
gs_filtered['categories'] = gs_filtered.apply(get_category_type, axis=1)


# Clean column names by keeping only last term
pt_filtered.columns = [column.split('.')[-1] for column in pt_filtered.columns]
bs_filtered.columns = [column.split('.')[-1] for column in bs_filtered.columns]
gs_filtered.columns = [column.split('.')[-1] for column in gs_filtered.columns]

pt_filtered.head(50)
gs_filtered.head(50)


# ## Filter the relevant location related information to the databases

# In[83]:


pt_filtered = pt_filtered[['name','categories','lat','lng']]

bs_filtered = bs_filtered[['name','categories','lat','lng']]

gs_filtered = gs_filtered[['name','categories','lat','lng']]

gs_filtered


# ## Validate only relevant items are stored in the dataframes

# In[14]:


pt_filtered.categories.value_counts()


# In[15]:


bs_filtered.categories.value_counts()


# In[16]:


gs_filtered.categories.value_counts()


# In[17]:


t_list = ['Train Station', 'Metro Station']
train_df = pt_filtered.loc[pt_filtered.categories.isin(t_list),]
train_df


# In[18]:


bs_list = ['Bus Stop', 'Bus Station']
bstop_df = bs_filtered.loc[bs_filtered.categories.isin(bs_list),]
bstop_df


# In[19]:


gs_list = ['Grocery Store']
gs_df = gs_filtered.loc[gs_filtered.categories.isin(gs_list),]
gs_df


# ## Check to see if dataframes were filtered correctly

# In[20]:


train_df.categories.value_counts()


# In[21]:


bstop_df.categories.value_counts()


# In[22]:


gs_df.categories.value_counts()


# In[25]:


train_locationlist = train_df[['lat', 'lng']].values.tolist()
bus_locationlist = bstop_df[['lat', 'lng']].values.tolist()
gs_locationlist = gs_df[['lat', 'lng']].values.tolist()


# In[26]:


from folium.plugins import MarkerCluster

address = 'Melbourne, VIC'

geolocator = Nominatim(user_agent="to_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude

# create map of Toronto using latitude and longitude values
mel_map = folium.Map(location=[latitude, longitude],tiles="OpenStreetMap", zoom_start=12)

    
# add markers to map
for lat, lng, ts, cat in zip(train_df['lat'], train_df['lng'],
                                           train_df['name'],train_df['categories']):
    label = '{}, {}'.format(ts,cat)
    label = folium.Popup(label, parse_html=True)
    folium.Marker(
        location=[lat, lng],
        popup=label,
        icon = folium.Icon(icon="train", prefix="fa",color = 'red')).add_to(mel_map)  
    
# add markers to map
for lat, lng, ts, cat in zip(bstop_df['lat'], bstop_df['lng'],
                                           bstop_df['name'],bstop_df['categories']):
    label = '{}, {}'.format(ts,cat)
    label = folium.Popup(label, parse_html=True)
    folium.Marker(
        location=[lat, lng],
        popup=label,
        icon = folium.Icon(icon="bus", prefix="fa",color = 'blue')).add_to(mel_map)  
    
# add markers to map
for lat, lng, ts, cat in zip(gs_df['lat'], gs_df['lng'],
                                           gs_df['name'],gs_df['categories']):
    label = '{}, {}'.format(ts,cat)
    label = folium.Popup(label, parse_html=True)
    folium.Marker(
        location=[lat, lng],
        popup=label,
        icon = folium.Icon(icon="shopping-cart", prefix="fa",color = 'green')).add_to(mel_map)      
    
mel_map


# In[27]:


from folium.plugins import MarkerCluster

address = 'Melbourne, VIC'

geolocator = Nominatim(user_agent="to_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude

# create map of Toronto using latitude and longitude values
mel_map = folium.Map(location=[latitude, longitude],tiles="OpenStreetMap", zoom_start=12)

marker_cluster = MarkerCluster().add_to(mel_map)
    
# add markers to map
for lat, lng, ts, cat in zip(train_df['lat'], train_df['lng'],
                                           train_df['name'],train_df['categories']):
    label = '{}, {}'.format(ts,cat)
    label = folium.Popup(label, parse_html=True)
    folium.Marker(
        location=[lat, lng],
        popup=label,
        icon = folium.Icon(icon="train", prefix="fa",color = 'red')).add_to(marker_cluster)  
    
# add markers to map
for lat, lng, ts, cat in zip(bstop_df['lat'], bstop_df['lng'],
                                           bstop_df['name'],bstop_df['categories']):
    label = '{}, {}'.format(ts,cat)
    label = folium.Popup(label, parse_html=True)
    folium.Marker(
        location=[lat, lng],
        popup=label,
        icon = folium.Icon(icon="bus", prefix="fa",color = 'blue')).add_to(marker_cluster)  
    
# add markers to map
for lat, lng, ts, cat in zip(gs_df['lat'], gs_df['lng'],
                                           gs_df['name'],gs_df['categories']):
    label = '{}, {}'.format(ts,cat)
    label = folium.Popup(label, parse_html=True)
    folium.Marker(
        location=[lat, lng],
        popup=label,
        icon = folium.Icon(icon="shopping-cart", prefix="fa",color = 'green')).add_to(marker_cluster)      
    
mel_map


# ## Read in the Crime Data from modified Excel File

# In[28]:


crime_data = pd.read_excel (r'C:\Users\ChristopherVandeVyve\Documents\IBM Data Science Coursera\Capstone Project\Crime_Data_Melbourne_LGA V0.xlsx')

#Remove white space before words in LGA column
crime_data["LGA"] = crime_data["LGA"].str.strip()
crime_data.head(10)


# ## Read in the Rental Rate Data from modified Excel File

# In[29]:


rental_data = pd.read_excel (r'C:\Users\ChristopherVandeVyve\Documents\IBM Data Science Coursera\Capstone Project\Median Rents by LGA V0.xlsx')
rental_data.head(10)


# In[30]:


DF = pd.merge(rental_data.rename(columns = {'Local Government Area':'LGA'}),crime_data,on = 'LGA')


# In[84]:


DF["Rental Ranking"] = DF["Median"].rank() 
DF["Crime Ranking"] = DF["Rate per 100,000 population"].rank() 
for i in range(len(DF["Rental Ranking"])):
    DF["Combined"] = DF["Rental Ranking"]+DF["Crime Ranking"]
    DF["Overall Ranking"] = DF["Combined"].rank()
    DF = DF.drop("Combined", axis = 1)
DF.sort_values("Overall Ranking",inplace = True)
DF.reset_index(drop=True,inplace = True)
DF.head


# In[60]:


DF.columns


# In[81]:


c_df = DF[['LGA','Rate per 100,000 population','Crime Ranking']]
c_df.sort_values('Crime Ranking', inplace = True)
c_df.reset_index(drop = True, inplace = True)
c_df.head(10)


# In[82]:


r_df = DF[['LGA','Median','Rental Ranking']]
r_df.sort_values('Rental Ranking', inplace = True)
r_df.reset_index(drop = True, inplace = True)
r_df.head(10)

