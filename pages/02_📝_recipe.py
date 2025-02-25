import streamlit as st
import sqlite3 as sql
import pandas as pd
import os
import base64

st.set_page_config(
    page_title="Add/Update Recipe",
    page_icon=":memo:"
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

# set_png_as_page_bg("images/recipe.png")

st.header(":blue[Add or Update a recipe]",divider="gray")

if os.name == 'nt':
    if os.path.exists("Z:\\dbase"):
        
        db = "Z:\\dbase\\meals.db" # production db when accessed in windows
    else:
        db="meals.db"  # dev db
else:
    db = "/srv/dev-disk-by-uuid-4622448D224483C1/mum1TB/dbase/meals.db" #prod in raspberry pi (same NAS)


def list_ulam(meal_type):

    # lastweek = date.today() - timedelta(n_days)


    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()
    ulamlist=[]
    try:
        if meal_type=="ALL":
            query_reg = f"SELECT * From ulam_reg \
                order by Meal_of_Day, Dish"

        elif meal_type=="Others":
            query_reg = f"SELECT * From ulam_reg WHERE Meal_of_Day not in (\"Break Fast\", \"Lunch\", \"Dinner\",\"Brunch\", \"Merienda\") \
                order by Meal_of_Day, Dish"
        else:
            query_reg = f"SELECT * From ulam_reg WHERE Meal_of_Day = \'{meal_type}\' \
                order by Dish"
   
        cursor.execute(query_reg) #datetime(\'now\', \'-8 days\')

        rows = cursor.fetchall()
        # Process the fetched rows
        
        for row in rows:
            ulamlist.append(row[0])
    except:
        st.warning("error!")
    # else:
        # st.success("New dish is added to DB!")
        # conn.commit()
    finally:
        conn.close()


    return ulamlist

def Query_Exist_recipe(mealID):
    
    conn = sql.connect(db, check_same_thread=False)
    queryExist=   f""" SELECT * FROM recipe_reg WHERE ulamID = {mealID} """

    df_exist = pd.read_sql_query(queryExist, conn)
    conn.close()
    return  df_exist

def Query_meal(dish):

    conn = sql.connect(db, check_same_thread=False)
    queryExist=   f""" SELECT ID, Dish FROM ulam_reg WHERE Dish = \'{dish}\' """

    df_exist = pd.read_sql_query(queryExist, conn)
    conn.close()

    return  df_exist

ulamtype = st.selectbox("Meal Type", ["Break Fast", "Brunch", "Lunch", "Dinner", "Merienda","Others", "ALL"])#,on_change=get_new_values_list, key='mealtype')
ulam_fill=list_ulam(ulamtype)
# dish = st.selectbox("Select Ulam from DB: ",ulam_fill)
dish = st.selectbox("Select Ulam from DB: ",ulam_fill)




# st.table(retrieved_exist)

def formcreation(ulam_fill,dish,retrieved_exist):
    st.write("Add Dish")
    with st.form(key="Recipe Management"):
        
        ulamID = int(retrieved_ulam['ID'][0])
        # st.warning(ulamID)
        try:
            st.text(ulamID)
            
            # st.warning(ulamID)
            editablename = st.text_input("DishName(Editable): ",retrieved_exist['Dish'][0])#,retrieved_exist['Expert'][0])
            expert = st.text_input("Author: ",retrieved_exist['Expert'][0])#,retrieved_exist['Expert'][0])
            ingredients = st.text_area("Enter Ingredients: ",retrieved_exist['Ingredients'][0])
            prep = st.text_area("Prep Steps ",retrieved_exist["Prep"][0])
            cook = st.text_area("Cooking Steps ",retrieved_exist["Cook"][0])
            settings = st.text_area("Cook/Oven settings ",retrieved_exist["Settings"][0])
            submit = st.form_submit_button("Add/Update")
        except:
            # st.text(ulamID)
            
            editablename = st.text_input("DishName(Editable): ",retrieved_ulam['Dish'][0])#,retrieved_exist['Expert'][0])
            expert = st.text_input("Author: ","")
            ingredients = st.text_area("Enter Ingredients: ","")
            prep = st.text_area("Prep Steps ","")
            cook = st.text_area("Cooking Steps ","")
            settings = st.text_area("Cook/Oven settings ","")
            submit = st.form_submit_button("Add/Update")
        

    if submit==True:
        # st.success("Your new ulam is registered!")
        addInfo(ulamID,editablename,expert,ingredients,prep,cook,settings)


def addInfo(a,b,c,d,e,f,g):

    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """ CREATE TABLE IF NOT EXISTS recipe_reg (ID INTEGER PRIMARY KEY AUTOINCREMENT, ulamID INTEGER, Dish TEXT(50),Expert TEXT(10), Ingredients TEXT(300)
                , Prep TEXT(300), Cook TEXT(300), Settings TEXT(100) )
    """
        )



        queryUpdateName=f"UPDATE ulam_reg SET Dish = \'{b}\' WHERE ID = {a}"
                # st.write(queryInsert)
        cursor.execute(queryUpdateName)

        queryInsert=f"INSERT OR REPLACE INTO recipe_reg (ID,ulamID, Dish,Expert,Ingredients,Prep,Cook,Settings) \
        VALUES((SELECT ID From recipe_reg WHERE ulamID = {a}),?,?,?,?,?,?,?)        "
        # st.write(queryInsert)
        cursor.execute(queryInsert, (a,b,c,d,e,f,g))
        
        conn.commit()

    except:
        st.warning("some error!")
    else:
        st.success("Recipe is updated/added!")
        # conn.commit()
    finally:
        conn.close()
    

retrieved_ulam=Query_meal(dish)
if dish:
    retrieved_exist=Query_Exist_recipe(retrieved_ulam['ID'][0])
    formcreation(ulam_fill,dish,retrieved_exist)

