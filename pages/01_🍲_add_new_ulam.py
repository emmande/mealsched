import streamlit as st
import sqlite3 as sql

st.set_page_config(
    page_title="Add Meal",
    page_icon=":stew:"
)

st.title("Add a new meal to masterlist")


conn = sql.connect("sharefromhost/meals.db", check_same_thread=False)
cursor = conn.cursor()

def formcreation():
    st.write("Add Dish")
    with st.form(key="Ulam Management"):
        dish = st.text_input("Enter Ulam Name: ")
        ulamtype = st.selectbox("Meal Type", ["Break Fast", "Lunch", "Dinner", "Merienda"])
        submit = st.form_submit_button("Add Ulam")

    if submit==True and len(dish) > 3:
        st.success("Your new ulam is registered!")
        addInfo(dish,ulamtype)


def addInfo(a,b):
    try:
        cursor.execute(
            """ CREATE TABLE IF NOT EXISTS ulam_reg (Dish TEXT(50), Meal_of_Day TEXT(50) )
    """
        )
        cursor.execute("INSERT INTO ulam_reg VALUES (?,?)", (a,b))
        conn.commit()
        # conn.close()
        # st.success("New Ulam is added to DB!")
    except:
        st.warning("DUPLICATE, ULAM ALREADY EXISTS!")
    else:
        st.success("New Ulam is added to DB!")
        # conn.commit()
    finally:
        conn.close()
        

formcreation()