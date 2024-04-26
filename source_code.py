import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import json
import streamlit as st
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from snowflake.connector import connect,DictCursor

# #to make a connection with snowflake
# my_connection = snowflake.connector.connect(user="SHANTH",
#                  password = "Shashi@007",
#                  account = "eqcptkk-vw73578",
#                  warehouse = "COMPUTE_WH",
#                  database = "PRACTICE",
#                  schema = "PUBLIC",
#                  role = "ACCOUNTADMIN" )

# curr = my_connection.cursor(DictCursor)

# #this is a phonepe pulsedata

# st.header("PHONE_PE PULSE")



#agg_transaction_india_state_wise
#First dataset iteration
path ="C://Users//Shanth//OneDrive//Desktop//GUVI - Python//Datasets//git//pulse//data//aggregated//transaction//country//india//state//"
#iterate through path for file names
city_agg_list = os.listdir(path)

agg_city_data = {'STATE':[], 'YEAR':[],'QUATER':[],'NAME':[], 'COUNT':[], 'AMOUNT':[]}
for i in city_agg_list:
    city_link = path+i+'//'
    year_agg_list = os.listdir(city_link)
    for j in year_agg_list:
        file_year_list = city_link+j+'//'
#         for k in file_year_list:
        json_agg_list = os.listdir(file_year_list)
        for l in json_agg_list:
            final = file_year_list+l
            data = open(final,'r')

            file_opener = json.load(data)

            for list_ in file_opener['data']['transactionData']:
                name_ = list_['name']
                count_ = list_['paymentInstruments'][0]['count']
                amount_ = list_['paymentInstruments'][0]['amount']
                agg_city_data['COUNT'].append(count_)
                agg_city_data['AMOUNT'].append(amount_)
                agg_city_data['NAME'].append(name_)
                agg_city_data['STATE'].append(i)
                agg_city_data['YEAR'].append(j)
                agg_city_data['QUATER'].append(l.split('.')[0])

TRANSACTION_AGG_CITY_DATA = pd.DataFrame(agg_city_data)

# write_pandas(my_connection,TRANSACTION_AGG_CITY_DATA,table_name = 'TRANSACTION_AGG_CITY_DATA')

#Extracting users_agg_statewise 
users_agg_statewise = {'STATE':[], 'YEAR':[],'QUATER':[],'REGISTEREDUSERS':[],'APPOPENS':[],'BRAND':[],'COUNT':[],'PERCENTAGE':[]}

path = '''C://Users//Shanth//OneDrive//Desktop//GUVI - Python//Datasets//git//pulse//data//aggregated//user//country//india//state//'''
state_list_1 = os.listdir(path)
for state_link in state_list_1:
    state_wise_link = path+state_link+'//'
    
    
    year_list_agg_users = os.listdir(state_wise_link)
    
    for years in year_list_agg_users:
        year_wise_link = state_wise_link+years+'//'
        files_list = os.listdir(year_wise_link)
        
        for files in files_list:
            final_link = year_wise_link+files
            
            DATA_users = open(final_link,'r')
            
            final_files = json.load(DATA_users)
            
            for files_ in final_files['data']:
                
                
                if final_files['data']['usersByDevice'] == None:
                    users_ = final_files['data']['aggregated']['registeredUsers']
                    app_opens = final_files['data']['aggregated']['appOpens']
                    brand_ = "-"
                    count_ = "-"
                    percentage_ = "-"
                else:
                    users_by_device = final_files['data']['usersByDevice']
                    for users_data in users_by_device:
                        users_ = final_files['data']['aggregated']['registeredUsers']
                        app_opens = final_files['data']['aggregated']['appOpens']
                        brand_ = users_data['brand']
                        count_ = users_data['count']
                        percentage_ = users_data['percentage']
                        

                        users_agg_statewise['REGISTEREDUSERS'].append(users_)
                        users_agg_statewise['APPOPENS'].append(app_opens)
                        users_agg_statewise['BRAND'].append(brand_)
                        users_agg_statewise['COUNT'].append(count_)
                        users_agg_statewise['PERCENTAGE'].append(percentage_)
                        users_agg_statewise['STATE'].append(state_link)
                        users_agg_statewise['YEAR'].append(years)
                        users_agg_statewise['QUATER'].append(files.split('.json')[0])


USERS_AGG_STATE_WISE = pd.DataFrame(users_agg_statewise)

# write_pandas(my_connection,USERS_AGG_STATE_WISE,table_name = 'USERS_AGG_STATE_WISE')

path = "C://Users//Shanth//OneDrive//Desktop//GUVI - Python//Datasets//git//pulse//data//map//transaction//hover//country//india//state//"

map_transaction_list = {'STATE':[],'YEAR':[],"QUATER":[],"DIST_NAME":[],"TYPE":[],"COUNT":[],"AMOUNT":[]}

state_list = os.listdir(path)
for states in state_list:
    W_states_path = path+states+"//"
    
    years_list = os.listdir(W_states_path)
    for years in years_list:
        W_year_path = W_states_path+years+"//"
        
        files_list = os.listdir(W_year_path)
        for files in files_list:
            final_path_1 = W_year_path+files
            
            DATA_3 = open(final_path_1,'r')
            final_files_3 = json.load(DATA_3)
            
            for file_items in final_files_3['data']['hoverDataList']:
                s_names = file_items['name']
                types = file_items['metric'][0]['type']
                count = file_items['metric'][0]['count']
                amount = file_items['metric'][0]['amount']
                states = states
                years_ = years
                quaters = files.split('.json')[0]
                
                map_transaction_list['STATE'].append(states)
                map_transaction_list['YEAR'].append(years_)
                map_transaction_list['QUATER'].append(quaters)
                map_transaction_list['DIST_NAME'].append(s_names)
                map_transaction_list['TYPE'].append(types)
                map_transaction_list['COUNT'].append(count)
                map_transaction_list['AMOUNT'].append(amount)
            
            
        

MAP_TRANSACTION_LIST = pd.DataFrame(map_transaction_list)


#map_users

MAP_USERS_DATA = {'STATE':[],'YEAR':[],'QUATER':[],'DISTRICT':[],'REGISTERED_USERS':[],'APP_OPENS':[]}

path = "C://Users//Shanth//OneDrive//Desktop//GUVI - Python//Datasets//git//pulse//data//map//user//hover//country//india//state//"

state_list = os.listdir(path)

for states in state_list:
    w_state_path = path+states+"//"
    year_list = os.listdir(w_state_path)
    
    for years in year_list:
        w_year_path = w_state_path+years+"//"
        
        files_list = os.listdir(w_year_path)
        
        for files in files_list:
            w_files_path = w_year_path+files
            
            data = open(w_files_path,'r')
            
            final_files = json.load(data)
            
            for district in final_files['data']['hoverData']:
                districts = district
                registered_users = final_files['data']['hoverData'][district]['registeredUsers']
                app_opens = final_files['data']['hoverData'][district]['appOpens']

                MAP_USERS_DATA['STATE'].append(states)
                MAP_USERS_DATA['YEAR'].append(years)
                MAP_USERS_DATA['QUATER'].append(files.split('.json')[0])
                MAP_USERS_DATA['DISTRICT'].append(districts)
                MAP_USERS_DATA['REGISTERED_USERS'].append(registered_users)
                MAP_USERS_DATA['APP_OPENS'].append(app_opens)

MAP_USERS_DATA = pd.DataFrame(MAP_USERS_DATA)

#top file _items

TOP_TRANSACTION_LIST = {'STATE':[],'YEAR_':[],'QUATERS':[],'DISTRICT':[],'TYPE':[],'COUNT_':[],'AMOUNT':[]}

path = "C://Users//Shanth//OneDrive//Desktop//GUVI - Python//Datasets//git//pulse//data//top//transaction//country//india//state//"
state_list = os.listdir(path)

for states in state_list:
    w_state_path = path+states+"//"
    
    year_list = os.listdir(w_state_path)
    
    for years in year_list:
        w_year_path = w_state_path+years+"//"
        
        files_list = os.listdir(w_year_path)
        
        for files in files_list:
            w_files_path = w_year_path+files
            
            data = open(w_files_path,'r')
            
            final_data = json.load(data)
            
            state = states
            year_ = years
            quaters = files.split('.json')[0]
            district_name = final_data['data']['districts'][0]['entityName']
            type_ = final_data['data']['districts'][0]['metric']['type']
            count_ = final_data['data']['districts'][0]['metric']['count']
            amount = final_data['data']['districts'][0]['metric']['amount']
            
            TOP_TRANSACTION_LIST['STATE'].append(state)
            TOP_TRANSACTION_LIST['YEAR_'].append(year_)
            TOP_TRANSACTION_LIST['QUATERS'].append(quaters)
            TOP_TRANSACTION_LIST['DISTRICT'].append(district_name)
            TOP_TRANSACTION_LIST['TYPE'].append(type_)
            TOP_TRANSACTION_LIST['COUNT_'].append(count_)
            TOP_TRANSACTION_LIST['AMOUNT'].append(amount)

TOP_TRANSACTION_LIST = pd.DataFrame(TOP_TRANSACTION_LIST)

#top users list

TOP_USERS_LIST = {'STATE':[],'YEAR_':[],'QUATERS_':[],'DISTRICT':[],'REGISTERED_USERS':[]}
path = 'C://Users//Shanth//OneDrive//Desktop//GUVI - Python//Datasets//git//pulse//data//top//user//country//india//state//'
states = os.listdir(path)

for state in states:
    w_state_path = path+state+"//"
    
    year_list = os.listdir(w_state_path)
    
    for years in year_list:
        w_year_path = w_state_path+years+"//"
        
        files_list = os.listdir(w_year_path)
        
        for files in files_list:
            final_path = w_year_path+files
            
            DATA = open(final_path,'r')
            
            final_items  = json.load(DATA)
            
            names = final_items['data']['districts'][0]['name']
            registered_users = final_items['data']['districts'][0]['registeredUsers']
            states = state 
            years_ = years
            quaters  = files.split('.json')[0]
            
            TOP_USERS_LIST['STATE'].append(states)
            TOP_USERS_LIST['YEAR_'].append(years_)
            TOP_USERS_LIST['QUATERS_'].append(quaters)
            TOP_USERS_LIST['DISTRICT'].append(names)
            TOP_USERS_LIST['REGISTERED_USERS'].append(registered_users)

TOP_USERS_LIST = pd.DataFrame(TOP_USERS_LIST)
