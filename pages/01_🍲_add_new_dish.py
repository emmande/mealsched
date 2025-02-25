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




dishtype = st.selectbox("Meal Type", ["Break Fast", "Lunch", "Dinner","Brunch", "Merienda","Others", "ALL"])

st.write("")


def formcreation():


    
    with st.form(key="dishadd"):

        st.subheader("Add Dish",divider="gray")
        dish = (st.text_input("Enter Dish Name: ")).title()

        
        mainIngred = st.selectbox("Main Ingredients", ['Fish','Egg','Pork','Veggie','Dessert',\
                                'Carbs','GroceryFood','Chicken','Beef','ShellFood',"Seafood",'TakeAway','Mutton'])
        #add health data
        oil = int(st.number_input("Oil Level (3=Deep Fried)",0,3))
        health_rating = int(st.number_input("Health Rating (5=Healthiest)",1,5))
        submit = st.form_submit_button("Add dish")
    

    if submit==True and len(dish) > 3 and len(find_similar(dish))==0:
        addInfo(dish,dishtype,mainIngred, oil, health_rating)
        st.success("Your new dish is registered!")
        df_table=load_registered(dishtype)

    elif submit==True and  len(find_similar(dish))>0:

        st.success("There are similar Dish names already registered")
        df_table=find_similar(dish)
    else:
        df_table = load_registered(dishtype)

    return df_table



    
    
    # st.success(df_table)


def addInfo(a,b,c,d,e):
    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """ CREATE TABLE IF NOT EXISTS ulam_reg (ID INTEGER PRIMARY KEY AUTOINCREMENT, Dish TEXT(50), Meal_of_Day TEXT(50), Main_Ingredients TEXT(10),"Oil_Level"	INTEGER,
	"Health_Rating"	INTEGER )
    """
        )
        queryInsert=f"INSERT OR REPLACE INTO ulam_reg (ID, Dish,Meal_of_Day,Main_Ingredients,Oil_Level,Health_Rating) \
                       VALUES((SELECT ID From ulam_reg WHERE Dish = \"{a}\"),?,?,?,?,?)        "#VALUES (?,?,?,?,?)", (a,b,c,d,e))

        cursor.execute(queryInsert, (a,b,c,d,e))
        conn.commit()
    except:
        st.warning("some error!")
    else:
        st.success("New dish is added to DB!")
        # conn.commit()
    finally:
        conn.close()

def load_registered(dishtype):
    conn = sql.connect(db, check_same_thread=False)
    try:
        if dishtype=="ALL":
            query_reg = f"SELECT * From ulam_reg \
                order by Meal_of_Day, Dish"

        elif dishtype=="Others":
            query_reg = f"SELECT * From ulam_reg WHERE Meal_of_Day not in (\"Break Fast\", \"Lunch\", \"Dinner\",\"Brunch\", \"Merienda\") \
                order by Meal_of_Day, Dish"
        else:
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


def find_similar(text_dish):
    conn = sql.connect(db, check_same_thread=False)
    try:
        if len(text_dish) > 3:
            query_reg = f"SELECT * From ulam_reg WHERE Dish like \'{text_dish}\' \
                    order by Dish"
            df_table = pd.read_sql_query(query_reg, conn)
        # st.success(query_reg)
        
    except:
        # st.warning("error!")
        df_table = None
    # else:
        # st.success("New dish is added to DB!")
        # conn.commit()
    finally:
        conn.close()
    return df_table
    

def UpdateDishInfo(id, dish,dishtype,Main_Ingredients,Oil_Level,Health_Rating):

    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()
    try:
        # update dish table
        queryUpdatedishreg=f""" UPDATE ulam_reg SET Dish = \'{dish}\',
               Meal_of_Day = \'{dishtype}\',
               Main_Ingredients = \'{Main_Ingredients}\',
               Oil_Level = {Oil_Level},
               Health_Rating = {Health_Rating}
               WHERE ID = {id}"""

        cursor.execute(queryUpdatedishreg)

        conn.commit()

    except:
        st.warning("some error in dish DB update!")
    else:
        st.success("Dish info is updated!")
        # conn.commit()
    finally:
        conn.close()



# st.divider()
# st.subheader("",divider="gray")
df_table=formcreation()


st.subheader(":blue[Masterlist]",divider="gray")
st.markdown("Tick an item to edit and update")





def update_from_editor(edited_df):
    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()

    id =edited_df['ID'].iloc[0]
    dish=edited_df['Dish'].iloc[0]
    dishtype = edited_df['Meal_of_Day'].iloc[0]
    Main_Ingredients=edited_df['Main_Ingredients'].iloc[0]
    Oil_Level=edited_df['Oil_Level'].iloc[0]
    Health_Rating=edited_df['Health_Rating'].iloc[0]
    try:
        # update dish table
        queryUpdatedishreg=f""" UPDATE ulam_reg SET Dish = \'{dish}\',
                Meal_of_Day = \'{dishtype}\',
                Main_Ingredients = \'{Main_Ingredients}\',
                Oil_Level = {Oil_Level},
                Health_Rating = {Health_Rating}
                WHERE ID = {id}"""
        # st.warning(queryUpdatedishreg)
        cursor.execute(queryUpdatedishreg)

        conn.commit()

    except:
        st.warning("some error in dish DB update!")
    else:
        # st.success("Dish info is updated!")
        st.success(f"{dish} is updated!")
        # conn.commit()
    finally:
        conn.close()


def delete_from_editor(edited_df):
    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()

    id =edited_df['ID'].iloc[0]

    try:
        # update dish table
        queryUpdatedishreg=f""" DELETE FROM ulam_reg
                WHERE ID = {id}"""
        # st.warning(queryUpdatedishreg)
        cursor.execute(queryUpdatedishreg)

        conn.commit()

    except:
        st.warning("some error in dish DB update!")
    else:
        # st.success("Dish info is updated!")
        st.success(f"removed!")
        # conn.commit()
    finally:
        conn.close()

        
# df_table=load_registered(dishtype)

event=st.dataframe(df_table,hide_index=True, use_container_width =True,on_select='rerun',
    selection_mode="single-row")

dishselected = event.selection.rows


st.markdown("Selected record to edit or delete:")
filtered_df = df_table.iloc[dishselected]


edited_df = st.data_editor(
    filtered_df,
    column_config={
        "Dish": "Dish",
        "Meal_of_Day": "Meal_of_Day",
        "Main_Ingredients": "Main_Ingredients",
        "Oil_Level": st.column_config.NumberColumn(
            "Oil level",
            help="How much oil this have (0-3)?",
            min_value=0,
            max_value=3,
            step=1,
            # format="%d ⭐",
        ), 
        "Health_Rating": st.column_config.NumberColumn(
        "Health rating",
        help="How healthy is this dish (1-5)?",
        min_value=1,
        max_value=5,
        step=1,
        # format="%d ⭐",
        ), 
    },
    hide_index=True
    )

with st.form(key="dishupdate"):

    subUpdate = st.form_submit_button("Update dish")
    subDelete = st.form_submit_button("Remove dish")

if subUpdate==True :
    update_from_editor(edited_df)
        # st.success(f"{edited_df['Dish'].iloc[0]} is updated!")
elif subDelete==True :
    delete_from_editor(edited_df)



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
