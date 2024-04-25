import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit import session_state

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


# Setting up the page
#st.set_page_config(layout="wide")

# Tabs for different views
#tab1, tab2 = st.tabs(["Current Trades Analysis", "Weekly Tradeable Summary"])
tab1, tab2, tab3 = st.tabs(["Current Trades Analysis", "Weekly Tradeable Summary", "Live Trade Descriptions"])

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


# In Tab 2 of your Streamlit app
# Assuming Tab 2 implementation here:



with tab2:
    df_weekly = get_data("http://192.168.0.26:5002/api/execute_pg_query?queryId=pvw_tbl_algo_sum_net_by_tradeable_signal_by_wk")
    if not df_weekly.empty:
        st.write("Weekly Tradeable Summary Data")
        # Display dataframe with a button in each row for selection
        selected_indices = st.multiselect('Select rows:', df_weekly.index)
        
        if selected_indices:
            # Assuming there's only one selection for simplicity; use selected_indices[0] for actual selection if multiple
            selected_row = df_weekly.loc[selected_indices[0]]
            filtered_df = df_weekly[(df_weekly['id'] == selected_row['id']) &
                                    (df_weekly['signal'] == selected_row['signal']) &
                                    (df_weekly['tradeable'] == selected_row['tradeable'])]
            filtered_df = filtered_df.sort_values('update_time')  # Sorting by update_time
            
            if not filtered_df.empty:
                fig = px.line(filtered_df, x='update_time', y='net', title='Net Over Time')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No data available for selected criteria.")
  

with tab3:
    df_trade_desc = get_data("http://192.168.0.26:5002/api/execute_query?queryId=qvw_get_trade_descritption")
    if not df_trade_desc.empty:
        # Sidebar filtering for Tab 3
        with st.sidebar:
            st.markdown("#### Trade Description Filters")  # Header for Tab 3
            selected_id_tab3 = st.selectbox('Select ID for Descriptions', ['All'] + df_trade_desc['id'].unique().tolist(), key='id_tab3')
            st.markdown("---")  # Adding a separator for Tab 3

        # Apply ID filter if not 'All'
        if selected_id_tab3 != 'All':
            df_trade_desc = df_trade_desc[df_trade_desc['id'] == selected_id_tab3]

        # Filter for rows with positive and negative net_return and add HTML styling
        trade_texts = []
        for index, row in df_trade_desc.iterrows():
            color = 'green' if row['net'] > 0 else 'red'
            trade_texts.append(f"<span style='color: {color};'>{row['entry_datetime']} - {row['trade_desc']}</span><br>")

        scrolling_text_html = f"""
        <div style="height: 100vh; width: 100%; overflow: hidden; position: relative;">
            <div style="position: absolute; width: 100%; height: 100%; animation: scroll-text 10s linear infinite;">
                {''.join(trade_texts)}
            </div>
        </div>
        <style>
        @keyframes scroll-text {{
            0% {{ transform: translateY(100%); }}
            100% {{ transform: translateY(-100%); }}
        }}
        </style>
        """

        st.markdown(scrolling_text_html, unsafe_allow_html=True)
