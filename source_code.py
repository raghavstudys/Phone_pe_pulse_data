import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import json
import streamlit as st
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from snowflake.connector import connect,DictCursor

#to make a connection with snowflake
my_connection = snowflake.connector.connect(user="SHANTH",
                 password = "Shashi@007",
                 account = "eqcptkk-vw73578",
                 warehouse = "COMPUTE_WH",
                 database = "PRACTICE",
                 schema = "PUBLIC",
                 role = "ACCOUNTADMIN" )

curr = my_connection.cursor(DictCursor)


#this is a phonepe pulsedata

st.header("PHONE_PE PULSE")

# #agg_transaction_india_state_wise
# #First dataset iteration
# path ="C://Users//Shanth//OneDrive//Desktop//GUVI - Python//Datasets//git//pulse//data//aggregated//transaction//country//india//state//"
# #iterate through path for file names
# city_agg_list = os.listdir(path)

# agg_city_data = {'STATE':[], 'YEAR':[],'QUATER':[],'NAME':[], 'COUNT':[], 'AMOUNT':[]}
# for i in city_agg_list:
#     city_link = path+i+'//'
#     year_agg_list = os.listdir(city_link)
#     for j in year_agg_list:
#         file_year_list = city_link+j+'//'
# #         for k in file_year_list:
#         json_agg_list = os.listdir(file_year_list)
#         for l in json_agg_list:
#             final = file_year_list+l
#             data = open(final,'r')

#             file_opener = json.load(data)

#             for list_ in file_opener['data']['transactionData']:
#                 name_ = list_['name']
#                 count_ = list_['paymentInstruments'][0]['count']
#                 amount_ = list_['paymentInstruments'][0]['amount']
#                 agg_city_data['COUNT'].append(count_)
#                 agg_city_data['AMOUNT'].append(amount_)
#                 agg_city_data['NAME'].append(name_)
#                 agg_city_data['STATE'].append(i)
#                 agg_city_data['YEAR'].append(j)
#                 agg_city_data['QUATER'].append(l.split('.')[0])

# df = pd.DataFrame(agg_city_data)
# st.dataframe(df, use_container_width=True)

# To retrive data

query = '''SELECT
    STATE,
    SUM(AMOUNT) AS TOTAL_TRANSACTION
FROM    
    AGG_TRANSACTION_INDIA
GROUP BY 1
ORDER BY 2 DESC;'''
curr.execute(query)
dff1 = curr.fetchall()
dff = pd.DataFrame(dff1)

st.dataframe(dff)
st.line_chart(data = dff,x = dff['STATE'],y=dff["TOTAL_TRANSACTION"])
