import streamlit as st
import sqlite3 as sql
import base64
import os
import pandas as pd
import json

from langchain_community.document_loaders import SeleniumURLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


st.set_page_config(
    page_title="Recipe AI agent",
    page_icon=":male-cook:"
)



if os.name == 'nt':
    if os.path.exists("Z:\\dbase"):
        
        db = "Z:\\dbase\\meals.db" # production db when accessed in windows
    else:
        db="meals.db"  # dev db
else:
    db = "/srv/dev-disk-by-uuid-4622448D224483C1/mum1TB/dbase/meals.db" #prod in raspberry pi (same NAS)

def add_dish(dic):
    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()


    a = dic['dish_name']
    b = dic['dishtype']
    c = dic['main_ingredient']
    d = dic['oil_rating']
    e = dic['health_rating']


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

def add_recipe(dic):

    a = dic['dish_name']
    b = 'AI agent'
    c = dic['ingredients'].replace(", ","\n")
    d = dic['prep_method']
    e = dic['cooking_steps']
    f = dic['oven_setting'] +'\n' + dic['extra_note']


    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()
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


#RAG Portion

template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:


"""

embeddings = OllamaEmbeddings(model="deepseek-r1:8b")
# embeddings = OllamaEmbeddings(model="deepseek-r1:14b")
vector_store = InMemoryVectorStore(embeddings)

model = OllamaLLM(model="deepseek-r1:8b")
# model = OllamaLLM(model="deepseek-r1:14b")

def load_page(url):
    loader = SeleniumURLLoader(
        urls=[url]
    )
    documents = loader.load()

    return documents

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    data = text_splitter.split_documents(documents)

    return data

def index_docs(documents):
    vector_store.add_documents(documents)

def retrieve_docs(query):
    return vector_store.similarity_search(query)

def answer_question(question, context):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    return chain.invoke({"question": question, "context": context})

st.title("AI Recipe Agent")
with st.form(key="AI Recipe Agent", ):
    # st.title("AI Recipe Agent")
    url = st.text_input("Enter Recipe site URL:")
    submit = st.form_submit_button("Analyze Recipe")

documents = load_page(url)
chunked_documents = split_text(documents)

index_docs(chunked_documents)

# question = st.chat_input()
question = """
The document contains a recipe. You are to retrieve the name of the dish, ingredients, 
method of cooking, breakdown into preparation and cooking. If there is an oven setting, retrieve it and convert to celsius if in fahrenheit.

Also you need to infer the following
1. Oil_raiting: You need to rate how much oily is this recipe. Criteria:  Rating is 0 when no oil involved and 3 means it was deep-fried.
2. Health_rating: Rate how healthy is the recipe from 1 to 5 based on the ingredients and method of cooking.
3. Extra_note: Infer extra steps that we should note.
4. dishtype: Infer whether this is good for Breakfast, brunch, lunch or dinner. Assign only one designation
5. main_ingredient: Assign one main ingredient like Chicken, Fish, Beef, Shellfood, Seafood, Pork, Lamb, Rice, Egg, Pasta, Flour

Output the information in a python dictionary format. 

Example:
{'dish_name': 'brioche', 
 'ingredients': "1 egg, 500 ml water, 2 cups flour",
 'prep_method': "prepare and mix all ingredients",
 'cooking_steps': "put into oven for 30 minutes",
 'oven_setting': "200 Celsius',
 'oil_rating': 1,
 'health_rating': 4,
 'dishtype': 'Breakfast',
 'main_ingredient': 'Flour',
 'extra_note':'Best to knead using mixer'
 
 }



"""

# def  extract_dic(answer):
#     pass

if submit:
    st.chat_message("user").write(question)
    retrieve_documents = retrieve_docs(question)
    context = "\n\n".join([doc.page_content for doc in retrieve_documents])
    answer = answer_question(question, context)
    st.chat_message("assistant").write(answer)
    # st.success(answer)
    # st.success(type(answer))
    # st.success(answer["dish_name"])

    st.subheader("Do you want to add this to DB?",divider="gray")
    with st.form(key="Add to DB", ):
        addtoDB = st.form_submit_button("Add to DB")


    # note need to take the dictionary from answer
    dic = json.loads(answer)
    if addtoDB:
        add_dish(dic)
        add_recipe(dic)

