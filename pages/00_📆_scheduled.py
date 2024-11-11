import streamlit as st
import sqlite3 as sql
from datetime import timedelta, date
import pandas as pd
from functools import reduce


st.set_page_config(
    page_title="Last Scheduled",
    page_icon=":calendar:"
)



st.title("Scheduled Meals")




def print_Scheduled(n_days):

    conn = sql.connect("meals.db", check_same_thread=False)
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


st.table(print_Scheduled(get_recent_days()))
# formcreation()