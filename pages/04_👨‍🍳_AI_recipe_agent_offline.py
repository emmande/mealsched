import streamlit as st
import sqlite3 as sql
import base64
import os
import pandas as pd
import json
import psutil
import re

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



if os.name == "nt":
    if os.path.exists("Z:\\dbase"):
        
        db = "Z:\\dbase\\meals.db" # production db when accessed in windows
    else:
        db="meals.db"  # dev db
else:
    db = "/srv/dev-disk-by-uuid-4622448D224483C1/mum1TB/dbase/meals.db" #prod in raspberry pi (same NAS)

def update_dish(a,b,c,d,e):
    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()


    # a = dic["dish_name"].title()
    # b = dic["dishtype"].title()
    # c = dic["main_ingredient"].title()
    # d = dic["oil_rating"]
    # e = dic["health_rating"]

#Main_Ingredients
    try:
        queryInsert=f"INSERT OR REPLACE INTO ulam_reg (ID, Dish,Meal_of_Day,Main_Ingredients,Oil_Level,Health_Rating) \
                       VALUES((SELECT ID From ulam_reg WHERE Dish = \"{a}\"),?,?,?,?,?)        "#VALUES (?,?,?,?,?)", (a,b,c,d,e))

        cursor.execute(queryInsert, (a,b,c,d,e))
        conn.commit()
        # conn.close()
        # st.success("New dish is added to DB!")
    except:
        st.warning("some error dish db!")
    else:
        st.success("New dish is added to DB!")
        # conn.commit()
    finally:
        conn.close()

def update_recipe(a,b,c,d,e,f):

    # a = dic["dish_name"].title()
    # b = "AI agent"
    # c = dic["ingredients"].replace(", ","\n")
    # d = dic["prep_method"]
    # e = dic["cooking_steps"]
    # f = dic["oven_setting"] +"\n" + dic["extra_note"]+"\n" + f"from {url}"


    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()
    try:
        queryInsert=f"INSERT OR REPLACE INTO recipe_reg (ID, Dish,Expert,Ingredients,Prep,Cook,Settings) \
            VALUES((SELECT ID From recipe_reg WHERE Dish = \"{a}\"),?,?,?,?,?,?)        "
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


def formcreation(dic,url):
# st.write("Add Dish")
    with st.form(key="Recipe Management"):

        
        dish = st.text_input("Dish name: ",dic["dish_name"].title())
        dishtype = st.text_input("Meal Type: ",dic["dishtype"].title())
        
        mainIngred = st.text_input("Main Ingredient: ",dic["main_ingredient"].title())

        #add health data
        oil = int(st.number_input("Oil Level (3=Deep Fried)",value=dic["oil_rating"]))
        health_rating = int(st.number_input("Health Rating (5=Healthiest)",value=dic["health_rating"]))
        
        # Will go into recipe data
        expert = st.text_input("Author: ","AI agent")#,retrieved_exist['Expert'][0])
        ingredients = st.text_area("Enter Ingredients: ",value=dic["ingredients"].replace(", ","\n"))
        prep = st.text_area("Prep Steps ",value=dic["prep_method"])
        cook = st.text_area("Cooking Steps ",value=dic["cooking_steps"])
        settings = st.text_area("Cook/Oven settings ",value=(dic["oven_setting"] +"\n" + dic["extra_note"]+"\n" + f"from {url}"))
        submit_p = st.form_submit_button("Update")
            

        

        if submit_p==True:
            # st.success("Your new ulam is registered!")
            update_dish(a = dish,
                b = dishtype,
                c = mainIngred,
                d = oil,
                e = health_rating)
    
            update_recipe(  a = dish,
                    b = expert,
                    c = ingredients,
                    d = prep,
                    e = cook,
                    f = settings)



#RAG Portion

template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don"t know the answer, just say that you don"t know. Use three sentences maximum and keep the answer concise.
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
The document contains a recipe. You are to retrieve the name of the dish, ingredients and their amounts, 
method of cooking, breakdown into preparation and cooking. If there is an oven setting, retrieve it and convert to celsius if in fahrenheit. If there is no oven put "NA".

Also you need to infer the following
1. Oil_raiting: You need to rate how much oily is this recipe. Criteria:  Rating is 0 when no oil involved and 3 means it was deep-fried.
2. Health_rating: Rate how healthy is the recipe from 1 to 5 based on the ingredients and method of cooking.
3. Extra_note: Infer extra steps that we should note.
4. dishtype: Assign one, whether this is good for Break fast, brunch, lunch or dinner.
5. main_ingredient: Assign one main ingredient like Chicken, Fish, Beef, Shellfood, Seafood, Pork, Lamb, Rice, Egg, Pasta, Flour

Output the information in a python dictionary format. Avoid nested structure. 

Example:
'''
{
 "dish_name": "brioche", 
 "ingredients": "1 egg, 500 ml water, 2 cups flour",
 "prep_method": "prepare and mix all ingredients",
 "cooking_steps": "put into oven for 30 minutes",
 "oven_setting": "200 Celsius",
 "oil_rating": 1,
 "health_rating": 4,
 "dishtype": "Breakfast",
 "main_ingredient": "Flour",
 "extra_note":"Best to knead using mixer"
  }
'''
 
 """


def  extract_RAM():
    return psutil.virtual_memory()[0]/1000000000



if submit and extract_RAM() > 15 and len(url)>10:
    
    st.chat_message("user").write(question)
    retrieve_documents = retrieve_docs(question)
    context = "\n\n".join([doc.page_content for doc in retrieve_documents])
    answer = answer_question(question, context)
    st.chat_message("assistant").write(answer)

    n= answer.find("{")
    e= answer.find("}")
    ans=answer[n:e+1]
    ans = ans.replace("[","'").replace("]","'")
    # st.success(ans)
    # st.success(ans)
    # st.success(type(ans))
    dic = json.loads(ans)
    
    st.subheader("Added to DB?",divider="gray")
    
    # with st.form(key="Add to DB", ):

    #     addtoDB = st.form_submit_button("Add to DB")


    # # note need to take the dictionary from answer
    
    #     if addtoDB:
    update_dish(a = dic["dish_name"].title(),
                b = dic["dishtype"].title(),
                c = dic["main_ingredient"].title(),
                d = dic["oil_rating"],
                e = dic["health_rating"])
    
    update_recipe(  a = dic["dish_name"].title(),
                    b = "AI agent",
                    c = dic["ingredients"].replace(", ","\n"),
                    d = dic["prep_method"],
                    e = dic["cooking_steps"],
                    f = dic["oven_setting"] +"\n" + dic["extra_note"]+"\n" + f"from {url}")
    # url=""
    st.success(dic["dish_name"]+ " was added to DB")
    url_copy = url
    url=""
    formcreation(dic,url_copy)
    

elif submit and extract_RAM() < 15:
    st.warning("RUN ONLY IF HOSTED IN atleast 16GB RAM COMPUTER!")



