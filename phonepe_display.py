import streamlit as st
from streamlit_option_menu import option_menu
from st_btn_select import st_btn_select
import psycopg2
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
import time
from PIL import Image, ImageDraw, ImageFont
from streamlit_star_rating import st_star_rating



# Define styles for a cohesive dark theme
styles = {
    "container": {"background-color": "#320d3e"},
    "menu-title": {"color": "#FFF"},
    "menu-icon": {"color": "#ffd79d"},
    "nav": {"background-color": "#320d3e"},
    "nav-item": {"color": "#FFF"},
    "nav-link": {"color": "#FFF"},
    "nav-link-selected": {"background-color": "#034569"},
}
st.set_page_config(layout="wide")

with st.sidebar:
    select = option_menu("Main Menu", ['HOME-PAGE 🏠', "VISUALIZE 📈", "EXPLORE-DATA 🔎","ABOUT 📝"], orientation="Vertical", styles=styles)

#FUNCTION FOR VISUALIZE
def aggregated_view():
    # ... (existing database connection and query execution code)
    query = """select states,years,sum(transaction_count)as total_transactions from aggregated_user group by  1,2;"""
    query_2 = """select states,years,sum(cast (transaction_amount as bigint)) as total_amount from aggregated_transaction group by 1,2 order by years asc;"""
    my_connection = psycopg2.connect(host='localhost',
                                user = 'postgres',
                                port = "5432",
                                database = 'phone_pe_pulse_data',
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
    chart_data_1 = final_data_visual[['states','years','total_transactions']]
    chart_data = chart_data_1.drop_duplicates()
    transaction_amount_data_2 = transaction_amount_1[['states','years','total_amount']]
    transaction_amount = transaction_amount_data_2.drop_duplicates()
    # st.metric(label="USERS",value=f'{round(max(chart_data['total_users'])/1000000000,2)} Cr',delta=f'{round(np.mean(chart_data['total_users'])/100000,2)} L')
    years = sorted(chart_data['years'].unique())

    # Create a dropdown menu for the user to select the year
    selected_year = st.selectbox('Select a Year', years)
    pivotted = chart_data[chart_data['years']==selected_year][['states','total_transactions']]
    result = pivotted.groupby(['states'])[['total_transactions']].max().reset_index().sort_values(by ='total_transactions',ascending = False)
    for value_h in list(result[:1:1]['states'].values):
        st.text(f'Summary💡: In year {selected_year} {value_h} had more number of Transactions')
    # Filter the data for the selected year
    chart_data_year = chart_data[chart_data['years'] == int(selected_year)].reset_index()
    
    st.metric(label="TRANSACTIONS",value=f'{round(max(chart_data_year['total_transactions'])/10000000,2)} Cr',delta=f'{round(np.mean(chart_data_year['total_transactions'])/10000000,2)} Cr')
    fig = px.bar(chart_data_year, x='states', y='total_transactions', color='years', barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    data_expander = st.expander('Show Data 🔦', expanded=False)
    with data_expander:
        st.dataframe(chart_data_year)
        states_ = sorted(chart_data['states'].unique())
        st.subheader("STATES YEAR WISE TOTAL TRANSACTIONS")
        selected_state = st.selectbox('Select a state', states_)
        chart_data_state = chart_data[chart_data['states'] == selected_state].reset_index().sort_values(by='years',ascending=False)[['years','total_transactions']]
        chart_data_state['years'] = chart_data_state['years'].astype(str)
        fig_year_wise = px.bar(chart_data_state, x='years', y='total_transactions')
        st.plotly_chart(fig_year_wise, use_container_width=True)
    
    years_1 = sorted(transaction_amount['years'].unique())
    selected_year_1 = st.selectbox('Select a Year', years_1)
    transaction_amount_year = transaction_amount[transaction_amount['years'] == int(selected_year_1)]
    pivotted_t = transaction_amount[transaction_amount['years']==selected_year_1][['states','total_amount']]
    result_1 = pivotted_t.groupby(['states'])[['total_amount']].max().reset_index().sort_values(by ='total_amount',ascending = False)
    for value_h_1 in list(result_1[:1:1]['states'].values):
        for t_value_h_1 in list(result_1[:1:1]['total_amount'].values):
            st.markdown(f'<p style="color:white;">Summary💡:</p> <p style="color:green;"> 👉 In year {selected_year_1} {value_h_1} had highest Transaction </p>', unsafe_allow_html=True)
    st.metric(label="USERS",value=f'{round(max(transaction_amount_year['total_amount'])/10000000,2)} Cr',delta=f'{round(np.mean(transaction_amount_year['total_amount'])/10000000,2)} Cr')
    fig_1 = px.line(transaction_amount_year, x='states', y='total_amount',color='years')
    st.plotly_chart(fig_1, use_container_width=True)
    
    
def explore_func():
    sql_code = st.text_area("Write your SQL code here:", value="SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ", height=200)
    st.code(sql_code, language="python", line_numbers=False) 
    query_for_sql = sql_code
    my_connection = psycopg2.connect(host='localhost',
                                user = 'postgres',
                                port = "5432",
                                database = 'phone_pe_pulse_data',
                                password = "Shashi@007")
    curr = my_connection.cursor()
    curr.execute(query_for_sql)
    data_for_sql = curr.fetchall()
    query_answer = pd.DataFrame(data_for_sql,columns = [i[0] for i in curr.description])
    st.dataframe(query_answer)

def type_text_animation(text):
    html_template = """
    <style>
        .typing-animation {
            font-family: Arial, sans-serif;
            font-size: 30px;
            color: #39FF14; /* Neon green color */
            white-space: nowrap;
            overflow: hidden;
            animation: typing 3s steps(40, end), blink-caret .5s step-end infinite alternate;
        }
        @keyframes typing {
            from {
                width: 0;
            }
            to {
                width: 100%;
            }
        }
        @keyframes blink-caret {
            from, to {
                border-color: transparent;
            }
            50% {
                border-color: #39FF14; /* Neon green color */
            }
        }
    </style>
    <div class="typing-animation">{}</div>
    """.format(text)
    st.markdown(html_template, unsafe_allow_html=True)
def about():
    
    st.title('About Webpage')

    st.markdown("""
    ## Project
    This is a project of PhonePe Pulse.

    ## Developer
    This app is developed by Shanth.

    ## About Shanth
    Shanth is currently pursuing data science and has worked on several projects.
    """) 
# For beautiful typing
    

def home_page():
    st.title("Welcome to Your Website")
    st.markdown("---")

    # Call the function to display typing animation
    st.text("This website is a clone or duplicate of phone pe pulse and it uses data of phone pe. It might be not accurate.")

    rating = {'Name':[],'Stars':[]}
    Name = st.text_input("Enter Your Name:")
    stars = st_star_rating("Please rate your experience", maxValue=5, defaultValue=0, key="rating")

    # Check if a rating has been given
    if stars > 0:
        if stars > 3:
            st.text(f"Hey {Name}, thanks for your {stars} stars!")
        elif stars < 3:
            st.text(f"Hey {Name}, thanks for your {stars} stars. We'll work on improving our website.")
    





#Main_BUTTON IS VISULAIZE
if __name__ == '__main__':
    if select == "VISUALIZE 📈":
        tab1,tab2,tab3 = st.tabs(['Aggregated View','Map View','Top View'])
        
        with tab1:
            st.write('Displaying','Aggregated', 'View...')
            aggregated_view()

    elif select == "EXPLORE-DATA 🔎":
        explore_func()

    elif select == "ABOUT 📝":
        about()
    
    elif select == "HOME-PAGE 🏠":
        home_page()
        

