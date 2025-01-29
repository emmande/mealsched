import streamlit as st
import sqlite3 as sql
import base64
import os
import pandas as pd

st.set_page_config(
    page_title="Add Meal",
    page_icon=":stew:"
)

st.header(":blue[Add a new meal to masterlist]")

if os.name == 'nt':
    if os.path.exists("Z:\\dbase"):
        
        db = "Z:\\dbase\\meals.db" # production db when accessed in windows
    else:
        db="meals.db"  # dev db
else:
    db = "/srv/dev-disk-by-uuid-4622448D224483C1/mum1TB/dbase/meals.db" #prod in raspberry pi (same NAS)




dishtype = st.selectbox("Meal Type", ["Break Fast", "Lunch", "Dinner","Brunch", "Merienda"])
st.write("")
def formcreation():
    st.subheader("Add Dish",divider="gray")
    with st.form(key="dish Management", ):
        dish = (st.text_input("Enter Dish Name: ")).title()
        # dishtype = st.selectbox("Meal Type", ["Break Fast", "Lunch", "Dinner","Brunch", "Merienda"]\
        #                         # ,on_change=load_registered(dishtype)
        #                         )
        
        mainIngred = st.selectbox("Main Ingredients", ['Fish','Egg','Pork','Veggie','Dessert',\
                                'Carbs','GroceryFood','Chicken','Beef','ShellFood',"Seafood",'TakeAway','Mutton'])
        #add health data
        oil = int(st.number_input("Oil Level (3=Deep Fried)",0,3))
        health_rating = int(st.number_input("Health Rating (5=Healthiest)",1,5))
        submit = st.form_submit_button("Add dish")
    

    if submit==True and len(dish) > 3:
        st.success("Your new dish is registered!")
        addInfo(dish,dishtype,mainIngred, oil, health_rating)
        load_registered(dishtype)
    
    
    # st.success(df_table)


def addInfo(a,b,c,d,e):
    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """ CREATE TABLE IF NOT EXISTS ulam_reg (Dish TEXT(50), Meal_of_Day TEXT(50), Main_Ingredients TEXT(10),"Oil_Level"	INTEGER,
	"Health_Rating"	INTEGER )
    """
        )
        cursor.execute("INSERT INTO ulam_reg VALUES (?,?,?,?,?)", (a,b,c,d,e))
        conn.commit()
        # conn.close()
        # st.success("New dish is added to DB!")
    except:
        st.warning("DUPLICATE, dish ALREADY EXISTS!")
    else:
        st.success("New dish is added to DB!")
        # conn.commit()
    finally:
        conn.close()

def load_registered(dishtype):
    conn = sql.connect(db, check_same_thread=False)
    try:
        
        query_reg = f"SELECT * From ulam_reg WHERE Meal_of_Day = \'{dishtype}\' \
            order by Dish"
        df_table = pd.read_sql_query(query_reg, conn)
        # st.success(query_reg)
        
    except:
        st.warning("error!")
    # else:
        # st.success("New dish is added to DB!")
        # conn.commit()
    finally:
        conn.close()
    return df_table
    



formcreation()
st.divider()
# st.subheader("",divider="gray")
st.subheader(":blue[Masterlist]",divider="gray")
df_table=load_registered(dishtype)
st.dataframe(df_table,hide_index=True, use_container_width =True)


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

# set_png_as_page_bg("C:/Users/User/Documents/mealschedback/images/test3.png")
