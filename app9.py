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
    if not df.empty:
        # Sidebar - Analysis toggles and Category selection for Tab 1
        with st.sidebar:
            st.header('Analysis Options for Current Trades')
            show_volume = st.checkbox('Show Trade Volume by Product', True, key='show_volume')
            show_returns = st.checkbox('Show Average Net Return', True, key='show_returns')
            show_commissions = st.checkbox('Show Commission Costs', True, key='show_commissions')
            show_status = st.checkbox('Show Trade Status Distribution', True, key='show_status')
            show_temporal = st.checkbox('Show Temporal Analysis of Trades', True, key='show_temporal')
            st.markdown("---")  # Adding a separator

        trade_categories = df['trade_category'].unique().tolist()
        selected_category = st.sidebar.selectbox('Select Trade Category', ['All'] + trade_categories)
        if selected_category != 'All':
            df = df[df['trade_category'] == selected_category]

        st.write("Trades Data")
        st.dataframe(df, use_container_width=True)

        col1, col2 = st.columns(2)
        if show_volume:
            trade_volume = df.groupby('product')['trade_quantity'].sum().reset_index()
            fig = px.bar(trade_volume, x='product', y='trade_quantity', title='Trade Volume by Product')
            col1.plotly_chart(fig)
        if show_returns:
            avg_net_return = df.groupby('trade_category')['net_return'].mean().reset_index()
            fig = px.bar(avg_net_return, x='trade_category', y='net_return', title='Average Net Return by Trade Category')
            col2.plotly_chart(fig)
        if show_commissions:
            commission_costs = df.groupby('product')['commission'].sum().reset_index()
            fig = px.line(commission_costs, x='product', y='commission', title='Commission Costs by Product')
            col1.plotly_chart(fig)
        if show_status:
            status_distribution = df['trade_status'].value_counts().reset_index()
            fig = px.pie(status_distribution, values='trade_status', names='index', title='Trade Status Distribution')
            col2.plotly_chart(fig)
        if show_temporal:
            df['entry_time'] = pd.to_datetime(df['Entry'])
            trades_over_time = df.resample('H', on='entry_time')['trade_id'].count()
            fig = px.line(trades_over_time, title='Trades Over Time by Hour')
            col1.plotly_chart(fig)

with tab2:
    df_weekly = get_data("http://192.168.0.26:5002/api/execute_pg_query?queryId=pvw_tbl_algo_sum_net_by_tradeable_signal_by_wk")
    st.write("Weekly Tradeable Summary Data")
    st.dataframe(df_weekly, use_container_width=True)  # Display unfiltered data

    # Sidebar - Filtering options for Tab 2
    with st.sidebar:
        st.header('Filter Options for Graphs Only')
        selected_id = st.selectbox('Select ID for Graphs', ['All'] + df_weekly['id'].unique().tolist(), key='id_2')
        selected_tradeable = st.selectbox('Select Tradeable for Graphs', ['All'] + df_weekly['tradeable'].unique().tolist(), key='tradeable_2')
        selected_signal = st.selectbox('Select Signal for Graphs', ['All'] + df_weekly['signal'].unique().tolist(), key='signal_2')
        show_net_graph = st.checkbox('Show Net Over Time', True, key='show_net_graph')

    # Apply filtering directly before plotting graphs
    if show_net_graph:
        filtered_df = df_weekly.copy()
        if selected_id != 'All':
            filtered_df = filtered_df[filtered_df['id'] == int(selected_id)]
        if selected_tradeable != 'All':
            filtered_df = filtered_df[filtered_df['tradeable'] == int(selected_tradeable)]
        if selected_signal != 'All':
            filtered_df = filtered_df[filtered_df['signal'] == selected_signal]

        filtered_df['update_time'] = pd.to_datetime(filtered_df['update_time'])
        fig = px.line(filtered_df, x='update_time', y='net', title='Net Over Time', markers=True)
        st.plotly_chart(fig, use_container_width=True)
