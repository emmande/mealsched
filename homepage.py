import streamlit as st
import sqlite3 as sql
from datetime import timedelta, date
import os
# import random

st.set_page_config(
    page_title="Meal Planner",
    page_icon=":knife_fork_plate:"
)

st.header(":blue[Meal Recommendations]")

if os.name == 'nt':
    db = "Z:\\dbase\\meals.db" # dev in windows
else:
    db = "/srv/dev-disk-by-uuid-4622448D224483C1/mum1TB/dbase/meals.db" #prod in raspberry pi (same NAS)

def suggest_ulam(meal_type,n_days,meal_date):

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
    querystring=f""" SELECT Dish, Main_Ingredients FROM ulam_reg WHERE Meal_of_Day in {filType} and Dish not in (SELECT distinct Dish from ulam_sched WHERE meal_date > datetime(\'{meal_date}\', \'-{n_days} days\')
        and meal_date < datetime(\'{meal_date}\'))

        """
    # order by RANDOM()
    cursor.execute(querystring) 
    #datetime(\'now\', \'-8 days\')
    # st.success(querystring)
    rows = cursor.fetchall()
    conn.close()
# Process the fetched rows
    ulamlist=[]
    mainIngred=[]
    # st.success(rows)
    for row in rows:
        ulamlist.append(row[0])
        mainIngred.append(row[1])

    return ulamlist,mainIngred


# Query Ulam suggestions and list them
ulamtype = st.selectbox("Meal Type", ["Break Fast", "Lunch", "Dinner", "Merienda"])
meal_date = st.date_input("Date: ")
last_days=st.slider("Don't Suggest from past days: ", 7, 14)
suggested, sugIngred = suggest_ulam(ulamtype,last_days,meal_date)

#add random selection here to be displayed in pills

def randomize_selection(suggested, sugIngred,nth):
    # Divide Food suggestions into meat, gulay, sides/dessert
    mains = []
    vegs=[]
    sides=[]
    # others=[]
    for ul, ing in zip(suggested, sugIngred):
        if ing in ('Fish','Egg','Pork','ShellFood','TakeAway','Mutton','Chicken','Beef'):
            mains.append(ul)
        elif ing =='Veggie':
            vegs.append(ul)
        else:
            sides.append(ul)

    ## remove ... apply only when random is executed only on a single button

    # if len(mains) > 0 and len(vegs)>0 and len(sides)>0:
    #     randomlist = [random.choice(mains),random.choice(vegs),random.choice(sides)]
    # elif len(mains) < 1 and len(vegs)>0 and len(sides)>0:
    #     randomlist = [random.choice(vegs),random.choice(sides)]
    # elif len(mains) > 0 and len(vegs)<1 and len(sides)>0:
    #     randomlist = [random.choice(mains),random.choice(sides)]
    # elif len(mains) > 0 and len(vegs)>0 and len(sides)<1:
    #     randomlist = [random.choice(mains),random.choice(vegs)]
    # elif len(mains) < 1 and len(vegs)<1 and len(sides)>0:
    #     randomlist = [random.choice(sides)]
  

    # return randomlist
    if len(mains) > nth:
        mnth=nth-1
    else:
        mnth=len(mains)-1
    if len(vegs) > nth:
        vnth=nth-1 
    else:
        vnth=len(vegs)-1
    if len(sides) > nth:
        snth=nth-1 
    else:
        snth=len(sides)-1

    if len(mains) > 0 and len(vegs)>0 and len(sides)>0:
        randomlist = [mains[mnth], vegs[vnth], sides[snth]]
    elif len(mains) < 1 and len(vegs)>0 and len(sides)>0:
        randomlist = [ vegs[vnth], sides[snth]]
    elif len(mains) > 0 and len(vegs)<1 and len(sides)>0:
        randomlist = [mains[mnth],  sides[snth]]
    elif len(mains) > 0 and len(vegs)>0 and len(sides)<1:
        randomlist = [mains[mnth], vegs[vnth]]
    elif len(mains) < 1 and len(vegs)<1 and len(sides)>0:
        randomlist = [ sides[snth]]

    # st.text(mnth,vnth,snth)
    return randomlist



## Adding value to a dictionary so can be visible in other pages
if 'recent_days' not in st.session_state:
    st.session_state['recent_days'] = last_days

# with st.form(key="Randomize"):
number = int(st.number_input("Suggest next/previous",1,len(suggested)))

# with st.form(key="r"):
#     if st.form_submit_button("Suggest another"):
#         suggested, sugIngred = suggest_ulam(ulamtype,last_days,meal_date)

randomlist=randomize_selection(suggested, sugIngred,number)

selected_suggested = st.pills("Suggested", randomlist, selection_mode="multi")
# st.markdown(randomlist)
# selectested = st.pills("Suggested", [1,2,3], selection_mode="multi")
st.text(f"Your selected ulam: {selected_suggested}.")

def schedule_this_ulam(meal_date,selected_suggested):
    
    with st.form(key="Schedule this ulam"):

        submit = st.form_submit_button("Schedule this Meal")
        if submit==True:
            for suggest in selected_suggested:
                add_to_ulam(meal_date,suggest,ulamtype)



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
schedule_this_ulam(meal_date,selected_suggested)





st.sidebar.success("Navigate page above")