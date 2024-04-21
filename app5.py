import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Set the page to wide mode
st.set_page_config(layout="wide")

# Function to get data from the API
@st.cache_data(ttl=600)  # Updated caching mechanism
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

# Sidebar - Analysis toggles
st.sidebar.header('Analysis Options')
show_volume = st.sidebar.checkbox('Show Trade Volume by Product', True)
show_returns = st.sidebar.checkbox('Show Average Net Return', True)
show_commissions = st.sidebar.checkbox('Show Commission Costs', True)
show_status = st.sidebar.checkbox('Show Trade Status Distribution', True)
show_temporal = st.sidebar.checkbox('Show Temporal Analysis of Trades', True)

# Data filtering by trade category
trade_categories = df['trade_category'].unique().tolist()
selected_category = st.sidebar.selectbox('Select Trade Category', ['All'] + trade_categories)


# Main area - Analysis displayed across columns and rows
col1, col2 = st.columns(2)

# Display the DataFrame in the app using full width
st.dataframe(df, width=None)

# Trade Volume by Product
if show_volume:
    with col1:
        trade_volume = df.groupby('product')['trade_quantity'].sum().reset_index()
        fig = px.bar(trade_volume, x='product', y='trade_quantity', title='Trade Volume by Product')
        st.plotly_chart(fig)

# Average Net Return by Trade Category
if show_returns:
    with col2:
        avg_net_return = df.groupby('trade_category')['net_return'].mean().reset_index()
        fig = px.bar(avg_net_return, x='trade_category', y='net_return', title='Average Net Return by Trade Category')
        st.plotly_chart(fig)

# Commission Costs by Product
if show_commissions:
    with col1:
        commission_costs = df.groupby('product')['commission'].sum().reset_index()
        fig = px.line(commission_costs, x='product', y='commission', title='Commission Costs by Product')
        st.plotly_chart(fig)

# Trade Status Distribution
if show_status:
    with col2:
        status_distribution = df['trade_status'].value_counts().reset_index()
        fig = px.pie(status_distribution, values='trade_status', names='index', title='Trade Status Distribution')
        st.plotly_chart(fig)

# Temporal Analysis of Trades
if show_temporal:
    with col1:
        df['entry_time'] = pd.to_datetime(df['Entry'])
        trades_over_time = df.resample('H', on='entry_time')['trade_id'].count()
        fig = px.line(trades_over_time, title='Trades Over Time by Hour')
        st.plotly_chart(fig)

# The above layout uses two columns and places different charts based on the user's selection from the sidebar.

if selected_category != 'All':
    df = df[df['trade_category'] == selected_category]