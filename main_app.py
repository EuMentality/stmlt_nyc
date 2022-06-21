import streamlit as st
import pandas as pd
import numpy as np
import pytz
from datetime import datetime
from src.model import make_prediction
from src.features import add_features



def user_trip_info():
    
    pickup_latitude = st.sidebar.slider('Pickup Latitude', 40.70001, 40.84001, 40.76000)
    pickup_longitude = st.sidebar.slider('Pickup Longitude', -74.0201, -73.9301,-73.9800 )
    dropoff_latitude = st.sidebar.slider('Dropoff Latitude', 40.70001, 40.84001, 40.77000)
    dropoff_longitude = st.sidebar.slider('Dropoff Longitude', -74.0201, -73.9301,-73.9900)
    pickup_datetime = datetime.now(pytz.timezone('US/Eastern')).strftime("%Y-%m-%d %H:%M:%S")
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

    return data

x = user_trip_info()


st.write(' # Manhattan Taxi Trip Duration')

st.sidebar.header('Information about the trip')

df = pd.DataFrame(x, index=[0])

st.subheader('User Input Parameters')
st.write(df)



def predict(json_obj):
    trip_params = pd.DataFrame({key: [value] for key, value in dict(json_obj).items()})
    trip_params = add_features(trip_params, purpose='predict')
    prediction = make_prediction(trip_params)
    return prediction


if st.button('predict trip duration'):
    st.write(f'The duration of your trip will be {round(predict(x))} minute')

