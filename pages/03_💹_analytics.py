import streamlit as st
import sqlite3 as sql
from datetime import timedelta, date
import pandas as pd
from functools import reduce
import base64
import os
import plotly.express as px


st.set_page_config(
    page_title="Analytics",
    page_icon=":chart:"
)

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

# set_png_as_page_bg("images/scheduled.png")



st.header(":blue[Meal Analytics]",divider="gray")


if os.name == 'nt':
    if os.path.exists("Z:\\dbase"):
        
        db = "Z:\\dbase\\meals.db" # production db when accessed in windows
    else:
        db="meals.db"  # dev db
else:
    db = "/srv/dev-disk-by-uuid-4622448D224483C1/mum1TB/dbase/meals.db" #prod in raspberry pi (same NAS)


ulamtype = st.selectbox("Meal Type", ["Break Fast", "Lunch", "Dinner", "Merienda"])
from_date = st.date_input("From: ",value=date.today()-timedelta(days=30))
to_date = st.date_input("To: ")

def meal_frequency(ulamtype,from_date,to_date):

    conn = sql.connect(db, check_same_thread=False)

    query_result= f""" SELECT dish,  count(*) as freq  from ulam_sched WHERE 
    meal_date > \'{from_date}\' and meal_date < \'{to_date}\'
    and Meal_of_Day = \'{ulamtype}\' group by dish
    order by count(*) desc"""

    query_ingred= f""" SELECT Main_Ingredients,  count(a.Dish) as freq  from ulam_sched as a  
    inner join ulam_reg as b on a.Dish=b.Dish
    where
    meal_date > \'{from_date}\' and meal_date < \'{to_date}\'
    and a.Meal_of_Day = \'{ulamtype}\' group by Main_Ingredients
    order by count(a.Dish) desc"""

    from_date2= from_date-timedelta(days=90)
    query_monthly= f""" SELECT dish, strftime("%m-%Y", meal_date) as month,  count(*) as freq  from ulam_sched WHERE 
    meal_date > \'{from_date2}\' 
    and Meal_of_Day = \'{ulamtype}\' 
    group by dish, strftime("%m-%Y", meal_date)
    order by strftime("%m-%Y", meal_date)
    """

    query_monthly_ing= f""" SELECT Main_Ingredients, strftime("%m-%Y", meal_date) as month,  count(a.Dish) as freq  from ulam_sched as a  
    inner join ulam_reg as b on a.Dish=b.Dish
    WHERE 
    meal_date > \'{from_date2}\' 
    and a.Meal_of_Day = \'{ulamtype}\' 
    group by Main_Ingredients, strftime("%m-%Y", meal_date)
    order by strftime("%m-%Y", meal_date)
    """

    query_weekly_oil= f""" SELECT a.Meal_of_Day, strftime("%W", meal_date) as weeks,  sum(b.Oil_Level) as oil_consumption  from ulam_sched as a  
    inner join ulam_reg as b on a.Dish=b.Dish
    WHERE 
    meal_date > \'{from_date2}\' 
    group by a.Meal_of_Day, strftime("%W", meal_date)
    order by strftime("%W", meal_date)
    """
    query_weekly_health= f""" SELECT a.Meal_of_Day, strftime("%W", meal_date) as weeks,  avg(b.Health_Rating) as avg_health  from ulam_sched as a  
    inner join ulam_reg as b on a.Dish=b.Dish
    WHERE 
    meal_date > \'{from_date2}\' 
    group by a.Meal_of_Day, strftime("%W", meal_date)
    order by strftime("%W", meal_date)
    """
    

 

    df_freq = pd.read_sql_query(query_result, conn)
    df_monthly = pd.read_sql_query(query_monthly, conn)
    df_freq_ing = pd.read_sql_query(query_ingred, conn)
    df_monthly_ing = pd.read_sql_query(query_monthly_ing, conn)
    df_weekly_oil = pd.read_sql_query(query_weekly_oil, conn)
    df_weekly_health = pd.read_sql_query(query_weekly_health, conn)

    conn.close()

    return df_freq, df_monthly,df_freq_ing,df_monthly_ing,df_weekly_oil,df_weekly_health

def get_recent_days():
    try:
        return st.session_state['recent_days']
    except:
        return 14


# st.table(print_Scheduled(get_recent_days()))
# st.dataframe(print_Scheduled(get_recent_days()),hide_index=True)

df_freq, df_trend,df_freq_ing,df_monthly_ing,df_weekly_oil,df_weekly_health=meal_frequency(ulamtype,from_date,to_date)

tab1, tab2, tab3,tab4 = st.tabs(["Pie Chart", "Bar Chart","Monthly Freq Trend","Weekly Health Monitor"])

fig = px.pie(df_freq, values='freq', names='Dish', title='Most Frequent Meals')
fig_ing = px.pie(df_freq_ing, values='freq', names='Main_Ingredients', title='Most Frequent Ingredients')
barChart = px.bar(df_freq, y='freq', x='Dish', title='Most Frequent Meals')
barChart_ing = px.bar(df_freq_ing, y='freq', x='Main_Ingredients', title='Most Frequent Ingredients')
trendChart = px.line(df_trend, x="month", y="freq", color='Dish',title='Dish Trend')
trendChart_ing = px.line(df_monthly_ing, x="month", y="freq", color='Main_Ingredients',title='Main Ingredients Trend')
trendChart_oil = px.bar(df_weekly_oil, x="weeks", y="oil_consumption", color='Meal_of_Day', title='Oil Consumption')
trendChart_health = px.bar(df_weekly_health, x="weeks", y="avg_health", color='Meal_of_Day', barmode="group", title='Healthy Eating Rating')




with tab1:
    # Use the Streamlit theme.
    # This is the default. So you can also omit the theme argument.
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    st.plotly_chart(fig_ing, theme="streamlit", use_container_width=True)
with tab2:
    # Use the Streamlit theme.
    st.plotly_chart(barChart, theme="streamlit", use_container_width=True)
    st.plotly_chart(barChart_ing, theme="streamlit", use_container_width=True)
with tab3:
    # Use the native Plotly theme.
    st.plotly_chart(trendChart, theme=None, use_container_width=True)
    st.plotly_chart(trendChart_ing, theme=None, use_container_width=True)
with tab4:
    # Use the native Plotly theme.
    st.plotly_chart(trendChart_oil, theme=None, use_container_width=True)
    st.plotly_chart(trendChart_health, theme=None, use_container_width=True)



# formcreation()