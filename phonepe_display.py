import streamlit as st
# from streamlit_option_menu import option_menu
# from st_btn_select import st_btn_select 
import psycopg2
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
import time
from PIL import Image, ImageDraw, ImageFont
from geopy.geocoders import Nominatim
import concurrent.futures
import plotly.graph_objects as go
# from streamlit_star_rating import st_star_rating


st.set_page_config(
    page_title="PhonePe Pulse",
    page_icon=None,  # You can add an icon here if needed
    layout="wide",  # You can adjust the layout as per your requirement
    initial_sidebar_state="collapsed",  # You can change this based on your sidebar preference
)

# Define the options for the select menu
import streamlit as st

options = ['HOME-PAGE 🏠', "VISUALIZE 📈", "EXPLORE-DATA 🔎", "ABOUT 📝"]

# Add a selectbox to the sidebar
selected_option = st.sidebar.selectbox('Main Menu', options, key='sidebar_select')

# Display the selected option
st.sidebar.write('You selected:', selected_option, unsafe_allow_html=True)




#FUNCTION FOR VISUALIZE
def aggregated_view():
    # ... (existing database connection and query execution code)
    query = """select states,years,sum(transaction_count)as total_transactions from aggregated_user group by  1,2;"""
    query_2 = """select states,years,sum(cast (transaction_amount as bigint)) as total_amount from aggregated_transaction group by 1,2 order by years asc;"""
    my_connection = psycopg2.connect(host='localhost',
                                user = 'postgres',
                                port = "5432",
                                database = 'PhonepePulse',
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
            st.markdown(f'<p style="color:black;">Summary💡:</p> <p style="color:green;"> 👉 In year {selected_year_1} {value_h_1} had highest Transaction </p>', unsafe_allow_html=True)
    st.metric(label="USERS",value=f'{round(max(transaction_amount_year['total_amount'])/10000000,2)} Cr',delta=f'{round(np.mean(transaction_amount_year['total_amount'])/10000000,2)} Cr')
    fig_1 = px.line(transaction_amount_year, x='states', y='total_amount',color='years')
    st.plotly_chart(fig_1, use_container_width=True)
    




import streamlit as st
import pandas as pd
import psycopg2
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
from folium import IFrame

def Map_view():
    # Connect to the database
    my_connection = psycopg2.connect(host='localhost',
                                     user='postgres',
                                     port="5432",
                                     database='PhonepePulse',
                                     password="Shashi@007")
    curr = my_connection.cursor()

    # Execute the query to fetch data
    query = '''SELECT * FROM map_transaction'''
    curr.execute(query)
    data = curr.fetchall()

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(data, columns=[i[0] for i in curr.description])

    # Read the latitude and longitude data from the file
    co = pd.read_csv('/Users/shanthakumark/Downloads/India States-UTs.csv')

    # Replace state names in the 'co' dataset
    co['State/UT'] = co['State/UT'].replace({
        'Andaman and Nicobar Islands': 'Andaman & Nicobar',
        'Andhra Pradesh': 'Andhra Pradesh',
        'Arunachal Pradesh': 'Arunachal Pradesh',
        'Assam': 'Assam',
        'Bihar': 'Bihar',
        'Chhattisgarh': 'Chhattisgarh',
        'Dadra and Nagar Haveli and Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'Delhi': 'Delhi',
        'Goa': 'Goa',
        'Gujarat': 'Gujarat',
        'Haryana': 'Haryana',
        'Himachal Pradesh': 'Himachal Pradesh',
        'Jharkhand': 'Jharkhand',
        'Karnataka': 'Karnataka',
        'Kerala': 'Kerala',
        'Lakshadweep': 'Lakshadweep',
        'Madhya Pradesh': 'Madhya Pradesh',
        'Maharashtra': 'Maharashtra',
        'Manipur': 'Manipur',
        'Meghalaya': 'Meghalaya',
        'Mizoram': 'Mizoram',
        'Nagaland': 'Nagaland',
        'Odisha': 'Odisha',
        'Puducherry': 'Puducherry',
        'Punjab': 'Punjab',
        'Rajasthan': 'Rajasthan',
        'Sikkim': 'Sikkim',
        'Tamil Nadu': 'Tamil Nadu',
        'Telangana': 'Telangana',
        'Tripura': 'Tripura',
        'Chandigarh': 'Chandigarh',
        'Jammu and Kashmir': 'Jammu & Kashmir',
        'Ladakh': 'Ladakh',
        'Uttar Pradesh': 'Uttar Pradesh',
        'Uttarakhand': 'Uttarakhand',
        'West Bengal': 'West Bengal'
    })

    # Merge the 'df' and 'co' datasets to map latitude and longitude
    df_merged = pd.merge(df, co[['State/UT', 'Latitude', 'Longitude']], left_on='states', right_on='State/UT',
                         how='left')

    # Drop unnecessary columns
    df_merged.drop(columns=['State/UT'], inplace=True)

    # Create a Folium map centered around India with custom width and height
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, width='100%', height='500px')

    # Create a MarkerCluster layer to hold the markers
    marker_cluster = MarkerCluster().add_to(m)

    # Get the selected year from the user
    selected_year = st.selectbox('Select Year', df_merged['years'].unique(), key='map_year_selectbox')

    # Filter DataFrame for the selected year
    df_year = df_merged[df_merged['years'] == selected_year]

    # Sum transaction amounts for each state in the selected year
    state_transactions = df_year.groupby('states')['transaction_amount'].sum().reset_index()

    # Add markers for each state
    for index, row in state_transactions.iterrows():
        # Get state name and total transaction amount
        state_name = row['states']
        total_transactions = row['transaction_amount']

        # Retrieve the coordinates of the state
        state_row = df_merged[df_merged['states'] == state_name].iloc[0]
        coordinates = [state_row['Latitude'], state_row['Longitude']]

        # Create a custom icon for the marker
        icon = folium.Icon(color='blue', icon='bar-chart', prefix='fa')

        # Create a Marker with the custom icon
        marker = folium.Marker(location=coordinates, icon=icon, tooltip=f"{state_name}<br>Total Transactions: {round(total_transactions/100000,2)}").add_to(marker_cluster)

        # Add click event to the marker
        marker.add_child(folium.ClickForMarker(popup=get_popup_html(state_name, selected_year)))


    # # Display the map on the left side
    # col1, col2 = st.columns([2, 3])
    # with col1:
    #     st.write("MAP VIEW")
    #     folium_static(m)

    # # Display the DataFrame table on the right side
    # with col2:
    #     f_data_right = df_year[['states','quarter','district','transaction_amount']]
    #     st.write("DATA TABLE")
        # st.write(f_data_right)

    # Display the map and data table side by side
    col1, col2, col3 = st.columns(3)

    # Display the map
    with col1:
        st.subheader("Map Overview",divider='rainbow')
        folium_static(m)

    # Add a divider between the map and the data table
    with col2:
        st.markdown("")

    # Display the data table
    with col3:
        st.subheader("Data Table",divider='rainbow')
        f_data_right = df_year[['states','quarter','district','transaction_amount']]
        st.write(f_data_right)


def get_popup_html(state_name, selected_year):
    # Create a Folium map centered around India
    # Connect to the database
    my_connection = psycopg2.connect(host='localhost',
                                     user='postgres',
                                     port="5432",
                                     database='PhonepePulse',
                                     password="Shashi@007")
    curr = my_connection.cursor()

    # Execute the query to fetch data
    query = '''SELECT * FROM map_insurance'''
    curr.execute(query)
    data = curr.fetchall()

    # Create a DataFrame from the fetched data
    df = pd.DataFrame(data, columns=[i[0] for i in curr.description])

    # Read the latitude and longitude data from the file
    co = pd.read_csv('/Users/shanthakumark/Downloads/India States-UTs.csv')

    # Replace state names in the 'co' dataset
    co['State/UT'] = co['State/UT'].replace({
        'Andaman and Nicobar Islands': 'Andaman & Nicobar',
        'Andhra Pradesh': 'Andhra Pradesh',
        'Arunachal Pradesh': 'Arunachal Pradesh',
        'Assam': 'Assam',
        'Bihar': 'Bihar',
        'Chhattisgarh': 'Chhattisgarh',
        'Dadra and Nagar Haveli and Daman and Diu': 'Dadra and Nagar Haveli and Daman and Diu',
        'Delhi': 'Delhi',
        'Goa': 'Goa',
        'Gujarat': 'Gujarat',
        'Haryana': 'Haryana',
        'Himachal Pradesh': 'Himachal Pradesh',
        'Jharkhand': 'Jharkhand',
        'Karnataka': 'Karnataka',
        'Kerala': 'Kerala',
        'Lakshadweep': 'Lakshadweep',
        'Madhya Pradesh': 'Madhya Pradesh',
        'Maharashtra': 'Maharashtra',
        'Manipur': 'Manipur',
        'Meghalaya': 'Meghalaya',
        'Mizoram': 'Mizoram',
        'Nagaland': 'Nagaland',
        'Odisha': 'Odisha',
        'Puducherry': 'Puducherry',
        'Punjab': 'Punjab',
        'Rajasthan': 'Rajasthan',
        'Sikkim': 'Sikkim',
        'Tamil Nadu': 'Tamil Nadu',
        'Telangana': 'Telangana',
        'Tripura': 'Tripura',
        'Chandigarh': 'Chandigarh',
        'Jammu and Kashmir': 'Jammu & Kashmir',
        'Ladakh': 'Ladakh',
        'Uttar Pradesh': 'Uttar Pradesh',
        'Uttarakhand': 'Uttarakhand',
        'West Bengal': 'West Bengal'
    })

    # Merge the 'df' and 'co' datasets to map latitude and longitude
    df_merged = pd.merge(df, co[['State/UT', 'Latitude', 'Longitude']], left_on='states', right_on='State/UT',
                         how='left')

    # Drop unnecessary columns
    df_merged.drop(columns=['State/UT'], inplace=True)

    # Filter DataFrame to get district-level transactions for the given state
    state_data = df_merged[(df_merged['states'] == state_name) & (df_merged['years'] == selected_year)]
    district_transactions = state_data.groupby('district')[['transaction_count', 'transaction_amount']].sum().reset_index()

    # Create HTML content for the popup
    popup_html = f"<b>{state_name} - {selected_year}</b><br>"
    popup_html += "<table>"
    popup_html += "<tr><th>District</th><th>Transaction Count</th><th>Transaction Amount</th></tr>"
    for index, row in district_transactions.iterrows():
        popup_html += f"<tr><td>{row['district']}</td><td>{row['transaction_count']}</td><td>{row['transaction_amount']}</td></tr>"
    popup_html += "</table>"
    return popup_html

def map_view_2():
    my_connection = psycopg2.connect(host='localhost',
                                     user='postgres',
                                     port="5432",
                                     database='PhonepePulse',
                                     password="Shashi@007")
    curr = my_connection.cursor()

    
    # Execute the query to fetch data
    query = '''with cte as (
    select map_user.states,map_user.years,map_user.quarter,map_user.districts,map_user.registereduser
    ,map_user.appopens,map_insurance.transaction_count,map_insurance.transaction_amount 
    from map_user left join map_insurance 
    on map_user.states = map_insurance.states 
    and map_user.years = map_insurance.years and 
    map_user.quarter = map_insurance.quarter and 
    map_user.districts = map_insurance.district
    where map_insurance.states IS NOT NULL)

    select cte.states,cte.years,cte.quarter,cte.districts,cte.registereduser
    ,cte.appopens,cte.transaction_count,cte.transaction_amount,map_transaction.transaction_count as T_transaction,
    map_transaction.transaction_amount as T_Transaction_amount
    from cte left join map_transaction on cte.states = map_transaction.states 
    and cte.years = map_transaction.years and cte.quarter = map_transaction.quarter 
    and cte.districts = map_transaction.district;

    '''
    curr.execute(query)
    data_insurance_1 = curr.fetchall()
    data_insurance = pd.DataFrame(data_insurance_1, columns=[i[0] for i in curr.description])
    years = data_insurance['years'].unique()
    year_selection = st.selectbox('SELECT_YEAR',years)
    rectified_year_data = data_insurance[data_insurance['years'] == year_selection]
    
    chart_data_t = rectified_year_data.groupby(['states','years','quarter']).agg({'registereduser':'sum','appopens':'sum','t_transaction':'sum','t_transaction_amount':'sum'}).reset_index().sort_values(by = 't_transaction_amount',ascending = False)
    st.bar_chart(chart_data_t,x = 'states',y = ['registereduser'] ,color = 'quarter')




def explore_func():
    sql_code = st.text_area("Write your SQL code here:", value="SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ", height=200)
    st.code(sql_code, language="python", line_numbers=False) 
    query_for_sql = sql_code
    my_connection = psycopg2.connect(host='localhost',
                                user = 'postgres',
                                port = "5432",
                                database = 'PhonepePulse',
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
    
    st.header('About Webpage',divider='violet')
    st.video('https://www.phonepe.com/webstatic/7275/videos/page/safety-herobanner.mp4',format = 'video/mp4',start_time= 0.2)

    col1_2,col2_2 = st.columns([13,13])
    with col1_2:
        st.image('https://www.phonepe.com/webstatic/7275/static/00ce8c2779b8e7913afa54fac6e2ffd4/8b553/1in3-desktop.png',width = 600)
    with col2_2:
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        # st.subheader('That’s why we have an advanced security infrastructure to keep your transactions safe. We do what it takes to earn the trust that you and 53.5+ crore Indians have placed in us.')
        st.markdown('''<h3 style="color:purple; font-weight: normal;">That’s why we have an advanced security infrastructure to keep your transactions safe. 
                    We do what it takes to earn the trust that you and 53.5+ crore Indians have placed in us.</h3>''', unsafe_allow_html=True)

    # Apply CSS to adjust the aspect ratio
    st.markdown(
        """
        <style>
        video {
            width: 100% !important;
            height: 10 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("""
    ## Project
    In conclusion, our project harnesses the power of Streamlit and various Python libraries to develop an interactive data exploration and visualization tool. By seamlessly integrating database interaction, data manipulation, visualization, image processing, and geocoding functionalities, we provide users with a comprehensive platform for analyzing and understanding complex datasets. Whether it's querying databases, generating interactive visualizations, annotating images, or performing spatial analysis, our application offers a myriad of features to cater to diverse data exploration needs. With its user-friendly interface and robust functionality, our project exemplifies the potential of Streamlit and Python libraries in democratizing data science and empowering users to derive actionable insights from data effortlessly..

    ## Developer
    This app is developed by Shanth.

    """) 

    st.image('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1MTciIGhlaWdodD0iNTE3Ij48ZGVmcz48bGluZWFyR3JhZGllbnQgaWQ9ImIiIHgxPSItMzcuOTE3JSIgeDI9IjEwMCUiIHkxPSIyMS4xNTElIiB5Mj0iMTE4Ljk3JSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzlCRkZGRiIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzZFQThDOSIvPjwvbGluZWFyR3JhZGllbnQ+PGxpbmVhckdyYWRpZW50IGlkPSJjIiB4MT0iLTM3LjkxNyUiIHgyPSIxMDAlIiB5MT0iMjIuNTIyJSIgeTI9IjExNS42OTElIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjOUJGRkZGIi8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjNkVBOEM5Ii8+PC9saW5lYXJHcmFkaWVudD48bGluZWFyR3JhZGllbnQgaWQ9ImQiIHgxPSItLjExJSIgeDI9Ijc4LjQ5OCUiIHkxPSI1LjE1NCUiIHkyPSIxNTcuMjE0JSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzlCRkZGRiIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzZFQThDOSIvPjwvbGluZWFyR3JhZGllbnQ+PGxpbmVhckdyYWRpZW50IGlkPSJlIiB4MT0iLTYuOTkxJSIgeDI9IjgyLjQxMiUiIHkxPSI1LjE1NCUiIHkyPSIxNTcuMjE0JSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzlCRkZGRiIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzZFQThDOSIvPjwvbGluZWFyR3JhZGllbnQ+PGxpbmVhckdyYWRpZW50IGlkPSJmIiB4MT0iLTguNzc0JSIgeDI9IjgzLjQyNiUiIHkxPSI1LjE1NCUiIHkyPSIxNTcuMjE0JSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzlCRkZGRiIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzZFQThDOSIvPjwvbGluZWFyR3JhZGllbnQ+PGxpbmVhckdyYWRpZW50IGlkPSJnIiB4MT0iLTE0LjY0NCUiIHgyPSI4Ni43NjQlIiB5MT0iNS4xNTQlIiB5Mj0iMTU3LjIxNCUiPjxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiM5QkZGRkYiLz48c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiM2RUE4QzkiLz48L2xpbmVhckdyYWRpZW50PjxsaW5lYXJHcmFkaWVudCBpZD0iaCIgeDE9Ii0zNy45MTclIiB4Mj0iMTAwJSIgeTE9IjIzLjY0OSUiIHkyPSIxMTIuOTk2JSI+PHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzlCRkZGRiIvPjxzdG9wIG9mZnNldD0iMTAwJSIgc3RvcC1jb2xvcj0iIzZFQThDOSIvPjwvbGluZWFyR3JhZGllbnQ+PGxpbmVhckdyYWRpZW50IGlkPSJpIiB4MT0iLTM3LjkxNyUiIHgyPSIxMDAlIiB5MT0iMTkuOTkxJSIgeTI9IjEyMS43NDMlIj48c3RvcCBvZmZzZXQ9IjAlIiBzdG9wLWNvbG9yPSIjOUJGRkZGIi8+PHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjNkVBOEM5Ii8+PC9saW5lYXJHcmFkaWVudD48ZmlsdGVyIGlkPSJhIj48ZmVDb2xvck1hdHJpeCBpbj0iU291cmNlR3JhcGhpYyIgdmFsdWVzPSIwIDAgMCAwIDAuNzA1MjUwIDAgMCAwIDAgMC41OTA0MTAgMCAwIDAgMCAwLjk0NzY5MCAwIDAgMCAxLjAwMDAwMCAwIi8+PC9maWx0ZXI+PC9kZWZzPjxnIGZpbHRlcj0idXJsKCNhKSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTkyMiAtNTE0NSkiIGZpbGw9Im5vbmUiIGZpbGwtcnVsZT0iZXZlbm9kZCIgb3BhY2l0eT0iLjQ5NSI+PGcgc3Ryb2tlLXdpZHRoPSI0Ij48cGF0aCBzdHJva2U9InVybCgjYikiIGQ9Ik0yMjAuNTgzIDE1NC40MTZTMjY2LjUwOCA0OS4wMyAzNzMgMTM5LjYyNmMwIDAtMzcuOTM0IDEyNi4zNS0xMzUuMjc2IDcxLjgzNiIgdHJhbnNmb3JtPSJyb3RhdGUoLTMwIDEwNDE4Ljg0NCA5MzkuNjY1KSIvPjxwYXRoIHN0cm9rZT0idXJsKCNjKSIgZD0iTTI0MS44MjMgMTkyLjExNXMxMTQuNzQyLTQ1LjgxOSAxMzAuODggOTUuMjA4YzAgMC0xMTguMjkgNjUuMDctMTUyLjQxOC01OS40OCIgdHJhbnNmb3JtPSJyb3RhdGUoLTMwIDEwNDE4Ljg0NCA5MzkuNjY1KSIvPjxwYXRoIHN0cm9rZT0idXJsKCNkKSIgZD0iTTE1My4yOSAxNjAuMTg2UzYwLjA2MyA5NS40MTQgMTQ4LjYyNiAwYzAgMCAxMjcuMjI2IDU1LjA5NCA2Ni4xNjUgMTQ5LjgwMyIgdHJhbnNmb3JtPSJyb3RhdGUoLTMwIDEwNDE4Ljg0NCA5MzkuNjY1KSIvPjxwYXRoIHN0cm9rZT0idXJsKCNlKSIgZD0iTTE5OC42NjEgMTQyLjE2OFMxNTQuNzQ4IDM2LjMzIDI5NS43MzYgMjEuNDVjMCAwIDY0LjE5MyAxMTYuNDktNjAuNDU0IDE0OS4xMzEiIHRyYW5zZm9ybT0icm90YXRlKC0zMCAxMDQxOC44NDQgOTM5LjY2NSkiLz48cGF0aCBzdHJva2U9InVybCgjZikiIGQ9Ik0yMzEuNjggMjE5LjI4OHMxMDYuMDcyIDQ4LjU4NSAxNi44MzUgMTUzLjYyOGMwIDAtMTMzLjE3MS0zMC45MzUtNzUuMzI5LTEzNS41NjIiIHRyYW5zZm9ybT0icm90YXRlKC0zMCAxMDQxOC44NDQgOTM5LjY2NSkiLz48cGF0aCBzdHJva2U9InVybCgjZykiIGQ9Ik0yMTAuNTM1IDIzMy40NDRzNDAuMjcyIDEwOC44NDEtOTYuOTgzIDEyMS43OGMwIDAtNzEuMDUzLTExNC42NTggMzQuOTIzLTE0Ni43MTMiIHRyYW5zZm9ybT0icm90YXRlKC0zMCAxMDQxOC44NDQgOTM5LjY2NSkiLz48cGF0aCBzdHJva2U9InVybCgjaCkiIGQ9Ik0xNTUuNjQzIDIyMS4wNzhTMTA4LjQ0OSAzMzYuNjgxIDAgMjQ2LjM0OGMwIDAgMzYuMzQyLTEzMi4wNjkgMTQ1Ljc3LTY2LjU3OCIgdHJhbnNmb3JtPSJyb3RhdGUoLTMwIDEwNDE4Ljg0NCA5MzkuNjY1KSIvPjxwYXRoIHN0cm9rZT0idXJsKCNpKSIgZD0iTTE0NC4zMjcgMTk1LjYxM1MzNC4zNTQgMjQzLjM2NyAyMi40NTMgMTA0LjgzYzAgMCAxMTUuMDg2LTc0LjA2NiAxNDkuMTkgNDEuODg0IiB0cmFuc2Zvcm09InJvdGF0ZSgtMzAgMTA0MTguODQ0IDkzOS42NjUpIi8+PC9nPjxwYXRoIHN0cm9rZT0iIzhCRTNFMyIgc3Ryb2tlLXdpZHRoPSI2IiBkPSJNMTIzNC45OCA1NDAzLjQ2Yy41NzMgMjYuMjI0LTIwLjIyIDQ3Ljk0Ny00Ni40NDMgNDguNTE5LTI2LjIyMS41NzMtNDcuOTQ0LTIwLjIxOS00OC41MTctNDYuNDQtLjU3My0yNi4yMjMgMjAuMjE4LTQ3Ljk0NiA0Ni40NDItNDguNTE5IDI2LjIyMi0uNTc0IDQ3Ljk0MyAyMC4yMTggNDguNTE3IDQ2LjQ0eiIvPjwvZz48L3N2Zz4=',width = 200)
    st.subheader('SCAN THIS FOR OUR MAIN WEBSITE')
    st.image('/Users/shanthakumark/Downloads/qrcode_www.phonepe.com.png')
# For beautiful typing
    

import streamlit as st

def home_page():

    # Header and content
    col1,col2 = st.columns([13,2])
    with col1:
        st.header("PhonePe Pulse",divider='violet')
    with col2:
        st.image('data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJMYXllcl8yIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHg9IjAiIHk9IjAiIHZpZXdCb3g9IjAgMCAxMzIgNDgiIHhtbDpzcGFjZT0icHJlc2VydmUiPjxzdHlsZT4uc3Qwe2ZpbGw6IzVmMjU5Zn08L3N0eWxlPjxjaXJjbGUgdHJhbnNmb3JtPSJyb3RhdGUoLTc2LjcxNCAxNy44NyAyNC4wMDEpIiBjbGFzcz0ic3QwIiBjeD0iMTcuOSIgY3k9IjI0IiByPSIxNy45Ii8+PHBhdGggY2xhc3M9InN0MCIgZD0iTTkwLjUgMzQuMnYtNi41YzAtMS42LS42LTIuNC0yLjEtMi40LS42IDAtMS4zLjEtMS43LjJWMzVjMCAuMy0uMy42LS42LjZoLTIuM2MtLjMgMC0uNi0uMy0uNi0uNlYyMy45YzAtLjQuMy0uNy42LS44IDEuNS0uNSAzLS44IDQuNi0uOCAzLjYgMCA1LjYgMS45IDUuNiA1LjR2Ny40YzAgLjMtLjMuNi0uNi42SDkyYy0uOSAwLTEuNS0uNy0xLjUtMS41em05LTMuOWwtLjEuOWMwIDEuMi44IDEuOSAyLjEgMS45IDEgMCAxLjktLjMgMi45LS44LjEgMCAuMi0uMS4zLS4xLjIgMCAuMy4xLjQuMi4xLjEuMy40LjMuNC4yLjMuNC43LjQgMSAwIC41LS4zIDEtLjcgMS4yLTEuMS42LTIuNC45LTMuOC45LTEuNiAwLTIuOS0uNC0zLjktMS4yLTEtLjktMS42LTIuMS0xLjYtMy42di0zLjljMC0zLjEgMi01IDUuNC01IDMuMyAwIDUuMiAxLjggNS4yIDV2Mi40YzAgLjMtLjMuNi0uNi42aC02LjN6bS0uMS0yLjJIMTAzLjJ2LTFjMC0xLjItLjctMi0xLjktMnMtMS45LjctMS45IDJ2MXptMjUuNSAyLjJsLS4xLjljMCAxLjIuOCAxLjkgMi4xIDEuOSAxIDAgMS45LS4zIDIuOS0uOC4xIDAgLjItLjEuMy0uMS4yIDAgLjMuMS40LjIuMS4xLjMuNC4zLjQuMi4zLjQuNy40IDEgMCAuNS0uMyAxLS43IDEuMi0xLjEuNi0yLjQuOS0zLjguOS0xLjYgMC0yLjktLjQtMy45LTEuMi0xLS45LTEuNi0yLjEtMS42LTMuNnYtMy45YzAtMy4xIDItNSA1LjQtNSAzLjMgMCA1LjIgMS44IDUuMiA1djIuNGMwIC4zLS4zLjYtLjYuNmgtNi4zem0tLjEtMi4ySDEyOC42di0xYzAtMS4yLS43LTItMS45LTJzLTEuOS43LTEuOSAydjF6TTY2IDM1LjdoMS40Yy4zIDAgLjYtLjMuNi0uNnYtNy40YzAtMy40LTEuOC01LjQtNC44LTUuNC0uOSAwLTEuOS4yLTIuNS40VjE5YzAtLjgtLjctMS41LTEuNS0xLjVoLTEuNGMtLjMgMC0uNi4zLS42LjZ2MTdjMCAuMy4zLjYuNi42aDIuM2MuMyAwIC42LS4zLjYtLjZ2LTkuNGMuNS0uMiAxLjItLjMgMS43LS4zIDEuNSAwIDIuMS43IDIuMSAyLjR2Ni41Yy4xLjcuNyAxLjQgMS41IDEuNHptMTUuMS04LjRWMzFjMCAzLjEtMi4xIDUtNS42IDUtMy40IDAtNS42LTEuOS01LjYtNXYtMy43YzAtMy4xIDIuMS01IDUuNi01IDMuNSAwIDUuNiAxLjkgNS42IDV6bS0zLjUgMGMwLTEuMi0uNy0yLTItMnMtMiAuNy0yIDJWMzFjMCAxLjIuNyAxLjkgMiAxLjlzMi0uNyAyLTEuOXYtMy43em0tMjIuMy0xLjdjMCAzLjItMi40IDUuNC01LjYgNS40LS44IDAtMS41LS4xLTIuMi0uNHY0LjVjMCAuMy0uMy42LS42LjZoLTIuM2MtLjMgMC0uNi0uMy0uNi0uNlYxOS4yYzAtLjQuMy0uNy42LS44IDEuNS0uNSAzLS44IDQuNi0uOCAzLjYgMCA2LjEgMi4yIDYuMSA1LjZ2Mi40ek01MS43IDIzYzAtMS42LTEuMS0yLjQtMi42LTIuNC0uOSAwLTEuNS4zLTEuNS4zdjYuNmMuNi4zLjkuNCAxLjYuNCAxLjUgMCAyLjYtLjkgMi42LTIuNFYyM3ptNjguMiAyLjZjMCAzLjItMi40IDUuNC01LjYgNS40LS44IDAtMS41LS4xLTIuMi0uNHY0LjVjMCAuMy0uMy42LS42LjZoLTIuM2MtLjMgMC0uNi0uMy0uNi0uNlYxOS4yYzAtLjQuMy0uNy42LS44IDEuNS0uNSAzLS44IDQuNi0uOCAzLjYgMCA2LjEgMi4yIDYuMSA1LjZ2Mi40em0tMy42LTIuNmMwLTEuNi0xLjEtMi40LTIuNi0yLjQtLjkgMC0xLjUuMy0xLjUuM3Y2LjZjLjYuMy45LjQgMS42LjQgMS41IDAgMi42LS45IDIuNi0yLjRWMjN6Ii8+PHBhdGggZD0iTTI2IDE5LjNjMC0uNy0uNi0xLjMtMS4zLTEuM2gtMi40bC01LjUtNi4zYy0uNS0uNi0xLjMtLjgtMi4xLS42bC0xLjkuNmMtLjMuMS0uNC41LS4yLjdsNiA1LjdIOS41Yy0uMyAwLS41LjItLjUuNXYxYzAgLjcuNiAxLjMgMS4zIDEuM2gxLjR2NC44YzAgMy42IDEuOSA1LjcgNS4xIDUuNyAxIDAgMS44LS4xIDIuOC0uNXYzLjJjMCAuOS43IDEuNiAxLjYgMS42aDEuNGMuMyAwIC42LS4zLjYtLjZWMjAuOGgyLjNjLjMgMCAuNS0uMi41LS41di0xem0tNi40IDguNmMtLjYuMy0xLjQuNC0yIC40LTEuNiAwLTIuNC0uOC0yLjQtMi42di00LjhoNC40djd6IiBmaWxsPSIjZmZmIi8+PC9zdmc+',width = 200,clamp=True,channels="RGB")
    
    st.write('')
    st.write('')
    st.write('')
    col1_1,col3_3 = st.columns([13,7.5])
    with col1_1:
        st.image('https://www.phonepe.com/webstatic/7275/static/e6134a314b2623b1b056da813213e72e/a384c/advert-hero-web-2x.png',width = 505)
        st.write('')
    with col3_3:
        st.image('https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWF1MnR0NzdkeWtkcmxtZXE2dmZ5bzNydWY0ZGU1Nm0xbHRjMHRocyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/KCsydOvAAnvmB4uIYM/giphy.webp',width = 315)
        # Apply CSS to adjust the aspect ratio
        st.markdown(
            """
            <style>
            video {
                width: 100% !important;
                height: 10 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    # Typing animation and disclaimer
    st.write(' ')
    st.write(' ')
    st.write(' ')
    st.write(' ')

    colq1,colq2 = st.columns([12,7])
    with colq1:
        st.image('data:image/png;base64,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',width = 100)
        st.write('''Every transaction on PhonePe needs your fingerprint/face ID''')
        st.write ('''UPI PIN and password for authentication.''')
    
    with colq2:
        st.image('data:image/png;base64,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',width =100 )
        st.write('''Only you and the person you are transacting with ''')
        st.write('''will be able to see the details of your payment.''')
    st.write(' ') 
    st.write(' ')   
    st.write(' ')     
    st.text("This website uses data of PhonePe. Accuracy may vary.")

    # Rating section
    Name = st.text_input("Enter Your Name:", key="name_input")  # Unique key for text input
    stars = st.slider("Rate your experience", min_value=0, max_value=5, step=1, format='%.0f')

    # Show a message based on the rating
    if stars > 0:
        st.text(f"Hey {Name}, you rated your experience as {stars} stars.")

    
def top_view():

    st.header('TOP - INSURANCE,USER AND TRANSACTION DEEP DIVE',divider='rainbow')

    query_top = '''with cte1 as 
    (select top_transaction.states,top_transaction.years,
    top_transaction.quarter,top_transaction.pincodes,top_transaction.transaction_count,top_transaction.transaction_amount,
    top_user.registereduser
    from top_transaction left join top_user
    on top_transaction.states = top_user.states and top_transaction.years = top_user.years
    and top_transaction.quarter = top_user.quarter and top_transaction.pincodes = top_user.pincodes),
    cte2 as
    (select cte1.states,cte1.years,cte1.quarter,
    cte1.pincodes,cte1.transaction_count,
    cte1.transaction_amount,
    cte1.registereduser,
    top_insurance.transaction_count as T_insurance_count,
    top_insurance.transaction_amount as T_insurance_amount
    from cte1 left join top_insurance on
    cte1.states = top_insurance.states and
    cte1.years = top_insurance.years and
    cte1.quarter = top_insurance.quarter and
    cte1.pincodes = top_insurance.pincodes
    where cte1.registereduser IS NOT NULL)

    select * from cte2 where t_insurance_count IS NOT NULL'''

    my_connection = psycopg2.connect(host='localhost',
                                    user = 'postgres',
                                    port = "5432",
                                    database = 'PhonepePulse',
                                    password = "Shashi@007")

    curr = my_connection.cursor()
    curr.execute(query_top)
    ans = curr.fetchall()
    dataframe_top = pd.DataFrame(ans,columns = [i[0] for i in curr.description])
    
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    
    col1,col2 = st.columns([1.5,2.5])
    with col1:
        st.dataframe(dataframe_top)

    with col2:
        fig = px.bar(dataframe_top, x='states', y='transaction_count', title='Transaction Counts by State',color='years')
        st.plotly_chart(fig)

    st.subheader('OVERALL DATA VIEW',divider='grey')

    colq1,colq2 = st.columns([10,16])
    with colq1:
        
        fig_2 = px.scatter(dataframe_top, x='transaction_count', y='t_insurance_count', hover_data=['states', 'years', 'quarter', 'pincodes'],
                         title='Insurance Transaction Count vs User Transaction Count',color='years')
        fig_2.update_layout(xaxis_title='User Transaction Count',
                          yaxis_title='Insurance Transaction Count')
        st.plotly_chart(fig_2)

    with colq2:
        fig_3 = px.sunburst(dataframe_top, path=['states', 'years', 'quarter', 'pincodes'],
                      values='t_insurance_count',
                      title='Insurance Transaction Count Sunburst Chart',
                      color='registereduser',
                      color_continuous_scale='RdBu',
                      hover_data=['t_insurance_count', 'transaction_count', 'transaction_amount'])
        fig_3.update_layout(template='plotly_dark')
        st.plotly_chart(fig_3, use_container_width=True)
        
#Main_BUTTON IS VISULAIZE
if __name__ == '__main__':
    if selected_option == "VISUALIZE 📈":
        tab1,tab2,tab3 = st.tabs(['Aggregated View','Map View','Top View'])

        
        with tab1:
            st.subheader('Displaying Aggregated View...',divider = 'rainbow')
            aggregated_view()

        with tab2:
            st.subheader('Displaying Map View...',divider='violet')
            Map_view()
            st.divider()
            st.subheader('MAP INSURANCE AND MAP USER OVERVIEW',divider='rainbow')
            map_view_2()
        
        with tab3:
            top_view()

    elif selected_option == "EXPLORE-DATA 🔎":
        explore_func()

    elif selected_option == "ABOUT 📝":
        about()
    
    elif selected_option == "HOME-PAGE 🏠":
        home_page()
        

