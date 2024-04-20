import streamlit as st
import pandas as pd
import requests

# Set the page to wide mode
st.set_page_config(layout="wide")

# Function to get data from the API
@st.cache(ttl=600)  # Cache the function so it only updates every 600 seconds (10 minutes)
def get_trade_data():
    url = "http://192.168.0.26:5002/api/execute_query?queryId=qvw_latest_trades_output"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()  # Assuming the API returns a JSON response that directly converts to a DataFrame
        return pd.DataFrame(data)
    else:
        st.error("Failed to retrieve data. Please check the API or network connection.")
        return pd.DataFrame()

# Fetch data from the API
df = get_trade_data()

# Sidebar - Category selection
trade_categories = df['trade_category'].unique().tolist()
selected_category = st.sidebar.selectbox('Select Trade Category', ['All'] + trade_categories)

# Main area - Display the data
# Check if a specific trade category is selected, and filter the data accordingly
if selected_category != 'All':
    df = df[df['trade_category'] == selected_category]

# Display the DataFrame in the app using full width
st.dataframe(df, width=None)

# The DataFrame will be automatically displayed in wide mode thanks to the `st.set_page_config` setting above.
