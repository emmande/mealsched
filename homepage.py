import streamlit as st
import sqlite3 as sql
from datetime import timedelta, date
import os


st.set_page_config(
    page_title="Meal Planner",
    page_icon=":knife_fork_plate:"
)


st.header(":blue[Meal Recommendations]")



if os.name == 'nt':
    db = "Z:\\dbase\\meals.db" # dev in windows
else:
    db = "/srv/dev-disk-by-uuid-4622448D224483C1/mum1TB/dbase/meals.db" #prod in raspberry pi (same NAS)

def suggest_ulam(meal_type,n_days):

    # lastweek = date.today() - timedelta(n_days)

    if meal_type == 'Break Fast':
        filType = '(\'Break Fast\', \'Merienda\')'
    elif meal_type == 'Merienda':
        filType = '(\'Merienda\')'
    else:
        filType = '(\"Lunch\", \"Dinner\")'
    # print(f"SELECT Dish FROM ulam_reg WHERE Meal_of_Day in {filType}")
    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute(
        f""" SELECT Dish FROM ulam_reg WHERE Meal_of_Day in {filType} and Dish not in (SELECT distinct Dish from ulam_sched WHERE meal_date > datetime(\'now\', \'-{n_days} days\'))
        order by Dish"""
    ) #datetime(\'now\', \'-8 days\')
    rows = cursor.fetchall()
    conn.close()
# Process the fetched rows
    ulamlist=[]
    for row in rows:
        ulamlist.append(row[0])

    return ulamlist


# Query Ulam suggestions and list them
ulamtype = st.selectbox("Meal Type", ["Break Fast", "Lunch", "Dinner", "Merienda"])
last_days=st.slider("Don't Suggest from past days: ", 7, 14)
suggested = suggest_ulam(ulamtype,last_days)
selected_suggested = st.pills("Suggested", suggested, selection_mode="multi")
# st.markdown(date.today() - timedelta(last_days))
st.markdown(f"Your selected ulam: {selected_suggested}.")


## Adding value to a dictionary so can be visible in other pages
if 'recent_days' not in st.session_state:
    st.session_state['recent_days'] = last_days


def schedule_this_ulam(selected_suggested):


    # st.write("Add Dish")
    with st.form(key="Schedule this ulam"):
        # Query Ulam suggestions and list them
        meal_date = st.date_input("Date: ")

        submit = st.form_submit_button("Schedule this Meal")

    if submit==True:
        for suggest in selected_suggested:
            add_to_ulam(meal_date,suggest,ulamtype)
        

        suggested = suggest_ulam(ulamtype,last_days)



def add_to_ulam(a,b,c):
    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """ CREATE TABLE IF NOT EXISTS ulam_sched (meal_date, Dish TEXT(50), Meal_of_Day TEXT(50) )
    """
        )
        cursor.execute("INSERT INTO ulam_sched VALUES (?,?,?)", (a,b,c))
        conn.commit()

    except:
        st.warning("ERROR !")
    else:
        st.success("Ulam is scheduled!")

    finally:
        conn.close()
        

# run the form
schedule_this_ulam(selected_suggested)





st.sidebar.success("Navigate page above")