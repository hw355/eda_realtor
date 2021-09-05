#!/usr/bin/env python
# coding: utf-8

# # Exploratory Analysis on Housing Data in Python

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')
import numpy as np
import requests
import pandas as pd
import seaborn as sns
import matplotlib as mat

sns.set(color_codes = True)

import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from ipynb.fs.full.Credentials import *


# ## Data Collection

# In[2]:


api_key = Realtor_API_KEY_1

city = 'New York City'
state = 'NY'
prop_type = 'single_family'
radius = '1'


# In[228]:


def getDataFromProperty(api_key, city, state, prop_type, radius):
    table = []
    url = "https://realtor.p.rapidapi.com/properties/v2/list-for-sale"

    querystring = {"city":city,
                   "limit":"200",
                   "offset":"0",
                   "beds_min":"1",
                   "baths_min":"1",
                   "sqft_min":"1",
                   "state_code":state,
                   "prop_type":prop_type,
                   "radius":radius}

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "realtor.p.rapidapi.com"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    for item in response.json()['properties']:
        item['city'] = item['address']['city']
        item['zipcode'] = item['address']['postal_code']
        item['state'] = item['address']['state_code']
        item['county'] = item['address']['county']
        item['longitude'] = item['address']['lon']
        item['latitude'] = item['address']['lat']
        item['combined_loc'] = item['city'] + ', ' + item['county'] + ', ' + item['state']
        item['size(sqft)'] = item['building_size']['size']
        data = pd.DataFrame.from_dict(item, orient = 'index').T
        row = data[['property_id', 'price', 'beds', 'baths','size(sqft)',
                    'city', 'county', 'state', 'zipcode', 'combined_loc', 'longitude', 'latitude', 'last_update']]
        
        table.append(row)
    
    table = pd.concat(table, axis = 0, ignore_index = True, sort = False)
    
    table['price'] = table['price'].astype(int)
    table['price'].describe().apply(lambda x: format(x, 'f'))
    table['size(sqft)'] = table['size(sqft)'].astype(int)
    table['size(sqft)'].describe().apply(lambda x: format(x, 'f'))
    table['longitude'] = table['longitude'].astype(float)
    table['latitude'] = table['latitude'].astype(float)
    table['last_update'] = pd.to_datetime(table['last_update'], format='%Y-%m-%dT%H:%M:%SZ', errors='coerce')
        
    return table


# In[229]:


Table = getDataFromProperty(api_key, city, state, prop_type, radius)
Table


# ## Exploratory Data Analysis

# In[230]:


Table.info()
Table.describe().apply(lambda s: s.apply('{0:.2f}'.format))


# In[231]:


#Boxplot - price
sns.boxplot(x = Table['price'])


# In[232]:


#Histogram - state
Table.state.value_counts().nlargest(40).plot(kind = 'bar', figsize=(10,5))


# In[233]:


#Scatter plot - price, baths
fig, ax = mat.pyplot.subplots(figsize=(10,6))
ax.scatter(Table['baths'], Table['price'])
ax.get_yaxis().set_major_formatter(
mat.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
ax.set_xlabel('baths')
ax.set_ylabel('price')
mat.pyplot.show()


# In[239]:


#Scatter plot - price, beds
fig, ax = mat.pyplot.subplots(figsize=(10,6))
ax.scatter(Table['beds'], Table['price'])
ax.get_yaxis().set_major_formatter(
mat.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
ax.set_xlabel('beds')
ax.set_ylabel('price')
mat.pyplot.show()


# In[243]:


#Scatter plot - state, price, size(sqft)
sns.set(rc={'figure.figsize':(15,8)})
sns.scatterplot(x = "size(sqft)", y = "price", hue="state",
             data = Table.groupby(['state']).apply(lambda x: x.sort_values(by=['price'])))
mat.pyplot.show()


# In[237]:


#Scatter plot - longitude, latitude, size(sqft), price
Table.plot(kind="scatter", x="longitude", y="latitude",
           s=Table['size(sqft)']/10, label="size(sqft)",
           c="price", cmap=mat.pyplot.get_cmap("jet"),
           colorbar=True, alpha=0.4, figsize=(20,15))
mat.pyplot.show()

