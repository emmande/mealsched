import streamlit as st
import sqlite3 as sql
import base64

st.set_page_config(
    page_title="Add Meal",
    page_icon=":stew:"
)

st.header(":blue[Add a new meal to masterlist]")


conn = sql.connect("meals.db", check_same_thread=False)
cursor = conn.cursor()

def formcreation():
    st.subheader("Add Dish",divider="gray")
    with st.form(key="Ulam Management", ):
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
