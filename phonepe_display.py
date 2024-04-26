import streamlit as st
from streamlit_option_menu import option_menu
from st_btn_select import st_btn_select
import psycopg2
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px


# Define styles for a cohesive dark theme
styles = {
    "container": {"background-color": "#320d3e"},
    "menu-title": {"color": "#FFF"},
    "menu-icon": {"color": "#ffd79d"},
    "nav": {"background-color": "#320d3e"},
    "nav-item": {"color": "#FFF"},
    "nav-link": {"color": "#FFF"},
    "nav-link-selected": {"background-color": "#e3b448"},
}
st.set_page_config(layout="wide")


with st.sidebar:
    select = option_menu("Main Menu", ['HOME-PAGE 🏠', "VISUALIZE 📈", "EXPLORE-DATA 🔎","ABOUT 📝"], orientation="Vertical", styles=styles)

#FUNCTION FOR VISUALIZE
def aggregated_view():
    # ... (existing database connection and query execution code)
    query = """select state, year, sum(cast (registeredusers as int)) as total_users from users_agg_state_wise group by 1,2 order by 2 desc;"""
    query_2 = """select state,year,sum(cast(amount as bigint)) as Transactions from transaction_agg_city_data group by 1,2;"""
    my_connection = psycopg2.connect(host='localhost',
                                user = 'postgres',
                                port = "5432",
                                database = 'phonepepulse',
                                password = "Shashi@007")
    curr = my_connection.cursor()
    curr.execute(query)
    data_1 = curr.fetchall()
    final_data_visual = pd.DataFrame(data_1,columns = [i[0] for i in curr.description])

    #second query

    curr.execute(query_2)
    data_1 = curr.fetchall()
    transaction_amount_1 = pd.DataFrame(data_1,columns = [i[0] for i in curr.description])

    # Assuming final_data_visual is your DataFrame
    chart_data_1 = final_data_visual[['state','year','total_users']]
    chart_data = chart_data_1.drop_duplicates()
    transaction_amount_data_2 = transaction_amount_1[['state','year','transactions']]
    transaction_amount = transaction_amount_data_2.drop_duplicates()
    # st.metric(label="USERS",value=f'{round(max(chart_data['total_users'])/1000000000,2)} Cr',delta=f'{round(np.mean(chart_data['total_users'])/100000,2)} L')
    years = sorted(chart_data['year'].unique())

    # Create a dropdown menu for the user to select the year
    selected_year = st.selectbox('Select a Year', years)
    pivotted = chart_data[chart_data['year']==selected_year][['state','total_users']]
    result = pivotted.groupby(['state'])[['total_users']].max().reset_index().sort_values(by ='total_users',ascending = False)
    for value_h in list(result[:1:1]['state'].values):
        st.text(f'Summary💡: In year {selected_year} {value_h} had more number of users')
    # Filter the data for the selected year
    chart_data_year = chart_data[chart_data['year'] == int(selected_year)].reset_index()
    
    st.metric(label="USERS",value=f'{round(max(chart_data_year['total_users'])/10000000,2)} Cr',delta=f'{round(np.mean(chart_data_year['total_users'])/10000000,2)} Cr')
    fig = px.bar(chart_data_year, x='state', y='total_users', color='year', barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    data_expander = st.expander('Show Data 🔦', expanded=False)
    with data_expander:
        st.dataframe(chart_data_year)
        states_ = sorted(chart_data['state'].unique())
        st.subheader("STATES YEAR WISE TOTAL USERS")
        selected_state = st.selectbox('Select a state', states_)
        chart_data_state = chart_data[chart_data['state'] == selected_state].reset_index().sort_values(by='year',ascending=False)[['year','total_users']]
        chart_data_state['year'] = chart_data_state['year'].astype(str)
        fig_year_wise = px.bar(chart_data_state, x='year', y='total_users')
        st.plotly_chart(fig_year_wise, use_container_width=True)
    
    years_1 = sorted(transaction_amount['year'].unique())
    selected_year_1 = st.selectbox('Select a Year', years_1)
    transaction_amount_year = transaction_amount[transaction_amount['year'] == int(selected_year_1)]
    pivotted_t = transaction_amount[transaction_amount['year']==selected_year_1][['state','transactions']]
    result_1 = pivotted_t.groupby(['state'])[['transactions']].max().reset_index().sort_values(by ='transactions',ascending = False)
    for value_h_1 in list(result_1[:1:1]['state'].values):
        for t_value_h_1 in list(result_1[:1:1]['transactions'].values):
            st.markdown(f'<p style="color:white;">Summary💡:</p> <p style="color:green;"> 👉 In year {selected_year_1} {value_h_1} had highest Transaction </p>', unsafe_allow_html=True)
    st.metric(label="USERS",value=f'{round(max(transaction_amount_year['transactions'])/10000000,2)} Cr',delta=f'{round(np.mean(transaction_amount_year['transactions'])/10000000,2)} Cr')
    fig_1 = px.line(transaction_amount_year, x='state', y='transactions',color='year')
    st.plotly_chart(fig_1, use_container_width=True)
    
    


#Main_BUTTON IS VISULAIZE
if select == "VISUALIZE 📈":
    tab1,tab2,tab3 = st.tabs(['Aggregated View','Map View','Top View'])
    
    with tab1:
        st.write('Displaying','Aggregated', 'View...')
        aggregated_view()
