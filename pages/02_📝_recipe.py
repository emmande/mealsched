import streamlit as st
import sqlite3 as sql
import pandas as pd

st.set_page_config(
    page_title="Add/Update Recipe",
    page_icon=":memo:"
)

st.title("Add or Update a recipe")

def list_ulam(meal_type):

    # lastweek = date.today() - timedelta(n_days)


    conn = sql.connect("meals.db", check_same_thread=False)
    cursor = conn.cursor()

   
    cursor.execute(
        f""" SELECT Dish FROM ulam_reg WHERE Meal_of_Day = \'{meal_type}\' 
        """
    ) #datetime(\'now\', \'-8 days\')

    rows = cursor.fetchall()
    conn.close()
# Process the fetched rows
    ulamlist=[]
    for row in rows:
        ulamlist.append(row[0])

    return ulamlist

def Query_Exist_recipe(dish):

    conn = sql.connect("meals.db", check_same_thread=False)
    queryExist=   f""" SELECT * FROM recipe_reg WHERE Dish = \'{dish}\' """

    df_exist = pd.read_sql_query(queryExist, conn)
    conn.close()

# Process the fetched rows

    return  df_exist

ulamtype = st.selectbox("Meal Type", ["Break Fast", "Lunch", "Dinner", "Merienda"])#,on_change=get_new_values_list, key='mealtype')
ulam_fill=list_ulam(ulamtype)
# dish = st.selectbox("Select Ulam from DB: ",ulam_fill)
dish = st.selectbox("Select Ulam from DB: ",ulam_fill)
retrieved_exist=Query_Exist_recipe(dish)

# st.table(retrieved_exist)

def formcreation(ulam_fill,dish,retrieved_exist):
    # st.write("Add Dish")
    with st.form(key="Recipe Management"):

        try:
            expert = st.text_input("Author: ",retrieved_exist['Expert'][0])#,retrieved_exist['Expert'][0])
            ingredients = st.text_area("Enter Ingredients: ",retrieved_exist['Ingredients'][0])
            prep = st.text_area("Prep Steps ",retrieved_exist["Prep"][0])
            cook = st.text_area("Cooking Steps ",retrieved_exist["Cook"][0])
            settings = st.text_area("Cook/Oven settings ",retrieved_exist["Settings"][0])
            submit = st.form_submit_button("Add/Update")
        except:
            expert = st.text_input("Author: ","")
            ingredients = st.text_area("Enter Ingredients: ","")
            prep = st.text_area("Prep Steps ","")
            cook = st.text_area("Cooking Steps ","")
            settings = st.text_area("Cook/Oven settings ","")
            submit = st.form_submit_button("Add/Update")
        

    if submit==True:
        # st.success("Your new ulam is registered!")
        addInfo(dish,expert,ingredients,prep,cook,settings)


def addInfo(a,b,c,d,e,f):
    try:
        cursor.execute(
            """ CREATE TABLE IF NOT EXISTS recipe_reg (ID INTEGER PRIMARY KEY AUTOINCREMENT, Dish TEXT(50),Expert TEXT(10), Ingredients TEXT(300)
                , Prep TEXT(300), Cook TEXT(300), Settings TEXT(100) )
    """
        )
        queryInsert=f"INSERT OR REPLACE INTO recipe_reg (ID, Dish,Expert,Ingredients,Prep,Cook,Settings) \
            VALUES((SELECT ID From recipe_reg WHERE Dish = \'{a}\'),?,?,?,?,?,?)        "
        # st.write(queryInsert)
        cursor.execute(queryInsert, (a,b,c,d,e,f))
        conn.commit()

    except:
        st.warning("some error!")
    else:
        st.success("Recipe is updated/added!")
        # conn.commit()
    finally:
        conn.close()
    


formcreation(ulam_fill,dish,retrieved_exist)