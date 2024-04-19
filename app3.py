import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# Define a function to fetch company information
def get_company_info(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    return info

# Define a function to get historical data and return a Plotly figure
def get_historical_data(ticker_symbol, period='1y', interval='1d'):
    df = yf.download(ticker_symbol, period=period, interval=interval)
    fig = px.line(df, x=df.index, y='Close')
    fig.update_layout(title=f'{ticker_symbol} Historical Data', xaxis_title='Date', yaxis_title='Price')
    return fig

# Streamlit UI
st.sidebar.title('Options')
company_list = pd.DataFrame({
    'label': ['AAPL - Apple Inc.', 'MSFT - Microsoft Corporation', 'GOOGL - Alphabet Inc.', 'AMZN - Amazon.com, Inc.'],
    'ticker': ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
})
ticker_symbol = st.sidebar.selectbox('Select asset', company_list['label']).split(' - ')[0]

num_quotes = st.sidebar.slider('Number of quotes', 30, 2000, 500)
sma = st.sidebar.slider('SMA Period', 5, 200, 50)
sma2 = st.sidebar.slider('SMA2 Period', 5, 200, 150)

# Main area - Company information and Stock chart in two columns
if st.sidebar.checkbox('View company info') or st.sidebar.checkbox('View chart'):
    col1, col2 = st.columns(2)

    with col1:
        if st.sidebar.checkbox('View company info', value=True):
            st.subheader(f'{ticker_symbol} - Company Information')
            info = get_company_info(ticker_symbol)
            st.json(info)  # Displaying the information in a JSON format for better readability

    with col2:
        if st.sidebar.checkbox('View chart', value=True):
            st.subheader(f'{ticker_symbol} - Stock Chart')
            fig = get_historical_data(ticker_symbol)
            st.plotly_chart(fig)
            
if st.sidebar.checkbox('View statistic'):
    st.header(f'{ticker_symbol} - Statistics')
    # Placeholder for statistical analysis code

st.sidebar.info('This app is a simple example of using Streamlit to create a financial data web app. It is maintained by Paduel.')
