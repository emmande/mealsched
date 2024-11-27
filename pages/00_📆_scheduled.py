import streamlit as st
import sqlite3 as sql
from datetime import timedelta, date
import pandas as pd
from functools import reduce
import base64
import os



st.set_page_config(
    page_title="Last Scheduled",
    page_icon=":calendar:"
)




st.header(":blue[Scheduled Meals]",divider="gray")


if os.name == 'nt':
    db = "Z:\\dbase\\meals.db" # dev in windows
else:
    db = "/srv/dev-disk-by-uuid-4622448D224483C1/mum1TB/dbase/meals.db" #prod in raspberry pi (same NAS)


def print_Scheduled(n_days):

    conn = sql.connect(db, check_same_thread=False)
    # cursor = conn.cursor()

    query_lunch = f""" SELECT meal_date, dish as Lunch  from ulam_sched WHERE meal_date > datetime(\'now\', \'-{n_days} days\') 
      and  Meal_of_Day = \'Lunch\' """
    
    query_merienda = f""" SELECT meal_date,dish as Merienda  from ulam_sched WHERE meal_date > datetime(\'now\', \'-{n_days} days\') 
      and  Meal_of_Day = \'Merienda\' """
    
    query_dinner = f""" SELECT meal_date, dish as Dinner  from ulam_sched WHERE meal_date > datetime(\'now\', \'-{n_days} days\') 
      and  Meal_of_Day = \'Dinner\' """
  
    query_bf = f""" SELECT meal_date, dish as BreakFast  from ulam_sched WHERE meal_date > datetime(\'now\', \'-{n_days} days\') 
      and  Meal_of_Day = \'Break Fast\' 
      """
    
    # query_single = f""" SELECT meal_date, (case when Meal_of_Day = \'Break Fast\' then dish end) as BreakFast  
    # , (case when Meal_of_Day = \'Lunch\' then dish end) as Lunch 
    # , (case when Meal_of_Day = \'Merienda\' then dish end) as Merienda 
    # , (case when Meal_of_Day = \'Dinner\' then dish end) as Dinner 
    # from ulam_sched WHERE meal_date > datetime(\'now\', \'-{n_days} days\') 
      
    #   """
 

    df_bf = pd.read_sql_query(query_bf, conn)
    df_ln = pd.read_sql_query(query_lunch, conn)
    df_mr= pd.read_sql_query(query_merienda, conn)
    df_dn= pd.read_sql_query(query_dinner, conn)
    
    # Implode the DataFrame based on the 'group' column
    df_bf = df_bf.groupby('meal_date')['BreakFast'].agg(lambda x: ', '.join(x)).reset_index()
    df_ln = df_ln.groupby('meal_date')['Lunch'].agg(lambda x: ', '.join(x)).reset_index()
    df_mr = df_mr.groupby('meal_date')['Merienda'].agg(lambda x: ', '.join(x)).reset_index()
    df_dn = df_dn.groupby('meal_date')['Dinner'].agg(lambda x: ', '.join(x)).reset_index()

    data_frames=[df_bf,df_ln,df_mr,df_dn]

    df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['meal_date'],how='outer'), data_frames)
    




    conn.close()

    return df_merged

def get_recent_days():
    try:
        return st.session_state['recent_days']
    except:
        return 7


# st.table(print_Scheduled(get_recent_days()))
st.dataframe(print_Scheduled(get_recent_days()))





def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

set_png_as_page_bg("images/scheduled.png")


# formcreation()