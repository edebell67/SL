import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Set the page to wide mode
st.set_page_config(layout="wide")

def get_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return pd.DataFrame(data)
    else:
        st.error("Failed to retrieve data. Please check the API or network connection.")
        return pd.DataFrame()

# Tabs for different views
tab1, tab2 = st.tabs(["Current Trades Analysis", "Weekly Tradeable Summary"])

with tab1:
    df = get_data("http://192.168.0.26:5002/api/execute_query?queryId=qvw_latest_trades_output")
    # Sidebar for Tab 1
    with st.sidebar:
        st.header('Analysis Options for Current Trades')
        # Adding a separator
        st.markdown("---")  

    # Display the DataFrame at the top of the page
    st.write("Trades Data")
    st.dataframe(df, use_container_width=True)

with tab2:
    df_weekly = get_data("http://192.168.0.26:5002/api/execute_pg_query?queryId=pvw_tbl_algo_sum_net_by_tradeable_signal_by_wk")

    # Sidebar for Tab 2
    with st.sidebar:
        st.header('Filter Options for Weekly Summary')
        selected_id = st.selectbox('Select ID', ['All'] + df_weekly['id'].unique().tolist(), key='id_2')
        show_graphs = st.checkbox('Show Detailed Graphs', True)

    if not df_weekly.empty:
        if selected_id != 'All':
            df_weekly = df_weekly[df_weekly['id'] == selected_id]

        # Display the filtered DataFrame in Tab 2
        st.write("Weekly Tradeable Summary Data")
        st.dataframe(df_weekly, use_container_width=True)

        if show_graphs:
            # First row of graphs
            col1, col2 = st.columns(2)
            with col1:
                df_filtered = df_weekly[(df_weekly['signal'] == 'buy') & (df_weekly['tradeable'] == 0)]
                fig = px.line(df_filtered, x='update_time', y='net', title='Net Return for Buy & Tradeable 0', markers=True)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                df_filtered = df_weekly[(df_weekly['signal'] == 'buy') & (df_weekly['tradeable'] == -1)]
                fig = px.line(df_filtered, x='update_time', y='net', title='Net Return for Buy & Tradeable -1', markers=True)
                st.plotly_chart(fig, use_container_width=True)

            # Second row of graphs
            col3, col4 = st.columns(2)
            with col3:
                df_filtered = df_weekly[(df_weekly['signal'] == 'sell') & (df_weekly['tradeable'] == 0)]
                fig = px.line(df_filtered, x='update_time', y='net', title='Net Return for Sell & Tradeable 0', markers=True)
                st.plotly_chart(fig, use_container_width=True)

            with col4:
                df_filtered = df_weekly[(df_weekly['signal'] == 'sell') & (df_weekly['tradeable'] == -1)]
                fig = px.line(df_filtered, x='update_time', y='net', title='Net Return for Sell & Tradeable -1', markers=True)
                st.plotly_chart(fig, use_container_width=True)
