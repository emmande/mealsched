import streamlit as st
import sqlite3 as sql
import base64
import os
import pandas as pd






st.set_page_config(
    page_title="Recipe AI agent",
    page_icon=":male-cook:"
)



if os.name == "nt":

    
    import json
    import re
    import psutil
    from langchain_community.document_loaders import SeleniumURLLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.vectorstores import InMemoryVectorStore
    from langchain_ollama import OllamaEmbeddings
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_ollama.llms import OllamaLLM


    if os.path.exists("Z:\\dbase"):
        
        db = "Z:\\dbase\\meals.db" # production db when accessed in windows
    else:
        db="meals.db"  # dev db
else:
    db = "/srv/dev-disk-by-uuid-4622448D224483C1/mum1TB/dbase/meals.db" #prod in raspberry pi (same NAS)



# Update Dish Table
def update_dish(a,b,c,d,e):
    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()
#Main_Ingredients
    try:
        queryInsert=f"INSERT OR REPLACE INTO ulam_reg (ID, Dish,Meal_of_Day,Main_Ingredients,Oil_Level,Health_Rating) \
                       VALUES((SELECT ID From ulam_reg WHERE Dish = \"{a}\"),?,?,?,?,?)        "#VALUES (?,?,?,?,?)", (a,b,c,d,e))

        cursor.execute(queryInsert, (a,b,c,d,e))
        conn.commit()
        # conn.close()
        # st.success("New dish is added to DB!")
        queryExist=   f""" SELECT ID, Dish FROM ulam_reg WHERE Dish = \'{a}\' """

        df_exist = pd.read_sql_query(queryExist, conn)

    except:
        st.warning("some error dish db!")
    else:
        st.success("New dish is added to DB!")
        # conn.commit()
    finally:
        conn.close()

    return int(df_exist['ID'][0])

def update_recipe(id,b,c,d,e,f,g):

    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()
    try:

        queryInsert=f"INSERT OR REPLACE INTO recipe_reg (ID,ulamID, Dish,Expert,Ingredients,Prep,Cook,Settings) \
        VALUES((SELECT ID From recipe_reg WHERE ulamID = {id}),?,?,?,?,?,?,?)        "
        # st.write(queryInsert)
        cursor.execute(queryInsert, (id,b,c,d,e,f,g))
        conn.commit()

    except:
        st.warning("some error!")
    else:
        st.success("Recipe is updated/added!")
        # conn.commit()
    finally:
        conn.close()


def formcreation(dic,url,ulamID):
# st.write("Add Dish")
    with st.form(key="Recipe Management",):

        st.text(ulamID)
        dish = st.text_input("Dish_name: ",dic["dish_name"].title())
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
            UpdateDishInfo(id=ulamID,
                            dish = dish,
                            dishtype = dishtype,
                            Main_Ingredients = mainIngred,
                            Oil_Level = oil,
                            Health_Rating = health_rating)
            
            UpdateRecipeInfo(ulamid=ulamID,
                             Dish=dish,
                             Expert=expert,
                             Ingredients=ingredients,
                             Prep=prep,
                             Cook=cook,
                             Settings=settings)
    

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


def UpdateRecipeInfo(ulamid,Dish,Expert,Ingredients,Prep,Cook,Settings):

    conn = sql.connect(db, check_same_thread=False)
    cursor = conn.cursor()
    try:
        # update dish table
        queryUpdaterecipereg=f"""UPDATE recipe_reg SET Dish = \'{Dish}\',
               Expert = \'{Expert}\',
               Ingredients = \'{Ingredients}\',
               Prep =\'{Prep}\',
               Cook = \'{Cook}\',
               Settings = \'{Settings}\'
               WHERE ulamID = {ulamid}"""

        cursor.execute(queryUpdaterecipereg)

        conn.commit()

    except:
        st.warning("some error in recipe DB update!")
    else:
        st.success("Recipe info is updated!")
        # conn.commit()
    finally:
        conn.close()


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

def  extract_RAM():
    return psutil.virtual_memory()[0]/1000000000



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

st.title("AI Recipe Agent")
st.markdown("Use an offline Deepseek model to understand recipe, retrieve and add relevant info to DB")
with st.form(key="AI Recipe Agent", ):
    # st.title("AI Recipe Agent")
    url = st.text_input("Enter Recipe site URL:")
    submit = st.form_submit_button("Analyze Recipe")


    if submit and extract_RAM() > 15 and len(url)>10:

        documents = load_page(url)
        chunked_documents = split_text(documents)

        index_docs(chunked_documents)
        
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
        
        

        # # note need to take the dictionary from answer
        
        #     if addtoDB and retrieve id:
        ret_id = update_dish(a = dic["dish_name"].title(),
                    b = dic["dishtype"].title(),
                    c = dic["main_ingredient"].title(),
                    d = dic["oil_rating"],
                    e = dic["health_rating"])
        
        update_recipe(  id=ret_id,
                        b = dic["dish_name"].title(),
                        c = "AI agent",
                        d = dic["ingredients"].replace(", ","\n"),
                        e = dic["prep_method"],
                        f = dic["cooking_steps"],
                        g = dic["oven_setting"] +"\n" + dic["extra_note"]+"\n" + f"from {url}")
        # url=""
        st.success(dic["dish_name"]+ " was added")
        url_copy = url
        url=""
        st.subheader("Modify info if needed. Go to dish and recipe tabs",divider="gray")
        # formcreation(dic,url_copy,ret_id)
        

    elif submit and extract_RAM() < 15:
        st.warning("RUN ONLY IF HOSTED IN atleast 16GB RAM COMPUTER!")



