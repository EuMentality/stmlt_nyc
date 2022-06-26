import requests   
import pytz
import folium 
import streamlit as st
import pandas as pd
import numpy as np
import osmnx as ox
import networkx as nx
from datetime import datetime
from geopy.geocoders import Nominatim
from streamlit_folium import folium_static


# 1. Sidebar Settings

## 1.1: Trip Config
st.sidebar.header('Information About The Trip')
st.sidebar.subheader('Follow this link:  [Google Maps](https://www.google.com/maps/@40.7508729,-73.9704699,13.46z)')
page_names = ['Enter Address', 'Enter Coordinates']
page = st.sidebar.radio('Choose The Navigation Type', page_names)

if page == 'Enter Coordinates':
    pickup_latitude = st.sidebar.number_input('Pickup Latitude', 40.700000, 40.840010, 40.765990, step=0.00001, format="%.6f")
    pickup_longitude = st.sidebar.number_input('Pickup Longitude', -74.020000, -73.930100, -73.980000, step=0.00001, format="%.6f")
    dropoff_latitude = st.sidebar.number_input('Dropoff Latitude', 40.700000, 40.840010, 40.770000, step=0.00001, format="%.6f")
    dropoff_longitude = st.sidebar.number_input('Dropoff Longitude', -74.020000, -73.9301, -73.990000, step=0.00001, format="%.6f")
    pickup_datetime = datetime.now(pytz.timezone('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S")
    st.sidebar.write(f'Time Now in NYC:  {str(pickup_datetime)}')
    passenger_count = st.sidebar.slider('Number of Passengers', 1, 9, 1)
    vendor_id = int(np.random.choice([1, 2], 1)[0])
    store_and_fwd_flag = str(np.random.choice(['N', 'Y'], 1)[0])
else:
    pickup_address = st.sidebar.text_input('Pickup Address', 'Empire State Building')
    dropoff_address = st.sidebar.text_input('Dropoff Address', 'Museum of the NYC')
    loc = Nominatim(user_agent="GetLoc")
    getloc_start = loc.geocode(pickup_address)
    getloc_end = loc.geocode(dropoff_address)
    pickup_latitude = getloc_start.latitude
    pickup_longitude = getloc_start.longitude
    dropoff_latitude = getloc_end.latitude
    dropoff_longitude = getloc_end.longitude
    pickup_datetime = datetime.now(pytz.timezone('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S")
    st.sidebar.write(f'Time Now in NYC:  {str(pickup_datetime)}')
    passenger_count = st.sidebar.slider('Number of Passengers', 1, 9, 1)
    vendor_id = int(np.random.choice([1, 2], 1)[0])
    store_and_fwd_flag = str(np.random.choice(['N', 'Y'], 1)[0])

data = {'pickup_latitude': pickup_latitude,
        'pickup_longitude': pickup_longitude, 
        'dropoff_latitude': dropoff_latitude,
        'dropoff_longitude': dropoff_longitude,
        'pickup_datetime': pickup_datetime,
        'passenger_count': passenger_count,
        'vendor_id': vendor_id,
        'store_and_fwd_flag': store_and_fwd_flag}

## 1.2: Predicting Trip Duration
def predict(url, json_obj):
    resp = requests.post(f'{url}',
                    json=json_obj)
    return resp.json()


url_backend = 'https://taxi-nyc-fastapi.herokuapp.com/predict'
if st.sidebar.button('Predict Trip Duration!'):
    ans = predict(url_backend, data)
    ans_text = f'The duration of your trip will be {int(ans["prediction"])} minutes!'
    title = f'<p style="font-family:sans-serif; color:Black; font-size: 14px;">{ans_text}</p>'
    st.sidebar.write(title, unsafe_allow_html=True)


# 2. Main Page Seggings
st.write(' # Manhattan Taxi Trip Duration')
ox.config(log_console=True, use_cache=True)

## 2.1
def find_shortest_route():
    start_latlng = (pickup_latitude, pickup_longitude)
    end_latlng = (dropoff_latitude, dropoff_longitude)
    place = 'Manhattan, New York, United States'
    mode = 'drive'        
    optimizer = 'length' 
    graph = ox.graph_from_place(place, network_type = mode)
    orig_node = ox.get_nearest_node(graph, start_latlng)
    dest_node = ox.get_nearest_node(graph, end_latlng)
    shortest_route = nx.shortest_path(graph, source=orig_node, target=dest_node, weight=optimizer)
    shortest_route_map = ox.plot_route_folium(graph, shortest_route, tiles='openstreetmap', route_color='#6495ED')
    start_latlng = (start_latlng[0],start_latlng[1])
    end_latlng   = (end_latlng[0],end_latlng[1])
    start_marker = folium.Marker(location = start_latlng, icon = folium.Icon(color='green'))
    end_marker = folium.Marker(location = end_latlng, icon = folium.Icon(color='red'))
    start_marker.add_to(shortest_route_map)
    end_marker.add_to(shortest_route_map)
    return shortest_route_map


page_names = ["I'm not interested", 'Show The Route of the Trip on The Map!']
page = st.radio('You know what to choose!', page_names)
if page ==  'Show The Route of the Trip on The Map!':
    with st.spinner('Please wait 15 seconds, calculating the optimal route is resource-intensive ^_^'):
        shortest_route = find_shortest_route()
        st_data = folium_static(shortest_route, width=700)
    st.success('Done!')
