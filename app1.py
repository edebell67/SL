import streamlit as st
import pandas as pd
import requests

# Function to fetch data from the API
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        return pd.DataFrame(data)
    except requests.RequestException as e:
        return pd.DataFrame({'Error': [str(e)]})

# URL of the API
url = "http://192.168.0.26:5002/api/execute_query?queryId=qapi_algo_trade_result_blog"

# Fetching the data
df = fetch_data(url)

# Display the data in the app
st.title('Algorithm Trade Result Data')
st.write(df)
