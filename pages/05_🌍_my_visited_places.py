import streamlit as st
import sqlite3
import pandas as pd
from streamlit_globe import streamlit_globe
import os
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from datetime import datetime

st.set_page_config(page_title="My Global Travels", layout="wide")

# --- DB Configuration ---
if os.name == "nt":
    db = "Z:\\dbase\\meals.db" if os.path.exists("Z:\\dbase") else "meals.db"
else:
    db = "/srv/dev-disk-by-uuid-4622448D224483C1/mum1TB/dbase/meals.db"

# --- Database Functions ---
def init_db():
    conn = sqlite3.connect(db)
    conn.execute('''CREATE TABLE IF NOT EXISTS places 
                   (city TEXT, country TEXT, lat REAL, lon REAL, travel_date TEXT)''')
    conn.close()

def get_data():
    conn = sqlite3.connect(db)
    df = pd.read_sql_query("SELECT * FROM places", conn)
    conn.close()
    if not df.empty:
        df['travel_date'] = pd.to_datetime(df['travel_date'])
    return df

def add_record(city, country, lat, lon, travel_date):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("INSERT INTO places (city, country, lat, lon, travel_date) VALUES (?, ?, ?, ?, ?)", 
              (city, country, lat, lon, travel_date.strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()

def get_coords(city, country):
    geolocator = Nominatim(user_agent="travel_app_v3")
    try:
        location = geolocator.geocode(f"{city}, {country}")
        return (location.latitude, location.longitude) if location else (None, None)
    except: return (None, None)

# --- Dynamic Color Logic ---
def get_color(date, min_year, max_year):
    """Returns Green for newest, Red for oldest."""
    if max_year == min_year: return "blue", "#0000FF"
    year = date.year
    # Normalize year to 0-1
    ratio = (year - min_year) / (max_year - min_year)
    # Folium uses string names; Globe uses Hex
    if ratio > 0.7: return "green", "#00FF00"
    if ratio > 0.3: return "orange", "#FFA500"
    return "red", "#FF0000"

init_db()

# --- Sidebar ---
with st.sidebar:
    st.header("📍 Add Destination")
    with st.form("add_form", clear_on_submit=True):
        new_city = st.text_input("City")
        new_country = st.text_input("Country")
        new_date = st.date_input("Travel Date", value=datetime.now())
        if st.form_submit_button("Add to Map"):
            lat, lon = get_coords(new_city, new_country)
            if lat:
                add_record(new_city, new_country, lat, lon, new_date)
                st.rerun()
            else: st.error("Location not found.")

# --- Logic & Filtering ---
df_raw = get_data()
st.title("🌍 My Travel Journey")

if not df_raw.empty:
    # Filters
    c1, c2 = st.columns(2)
    with c1: selected_year = st.selectbox("Year", ["All"] + sorted(df_raw['travel_date'].dt.year.unique(), reverse=True))
    with c2: selected_month = st.selectbox("Month", ["All"] + list(range(1, 13)))

    df = df_raw.copy()
    if selected_year != "All": df = df[df['travel_date'].dt.year == selected_year]
    if selected_month != "All": df = df[df['travel_date'].dt.month == int(selected_month)]

    min_y, max_y = df_raw['travel_date'].dt.year.min(), df_raw['travel_date'].dt.year.max()

    # --- Globe Data ---
    points, labels = [], []
    for r in df.itertuples():
        f_color, g_hex = get_color(r.travel_date, min_y, max_y)
        points.append({'lat': r.lat, 'lng': r.lon, 'size': 0.01, 'color': g_hex})
        labels.append({'lat': r.lat, 'lng': r.lon, 'text': f"{r.city} ({r.travel_date.year})", 'color': 'white', 'size': 0.3})

    streamlit_globe(pointsData=points, labelsData=labels, width=1000, height=500)

    # --- Folium Zoom & Map ---
    st.subheader("Map Exploration")
    
    # Selection for City Zoom
    target_city = st.selectbox("🎯 Zoom to City:", ["Overview"] + df['city'].tolist())
    
    if 'map_view' not in st.session_state:
        st.session_state.map_view = {'center': [20, 0], 'zoom': 2}

    if target_city != "Overview":
        row = df[df['city'] == target_city].iloc[0]
        st.session_state.map_view = {'center': [row.lat, row.lon], 'zoom': 10}

    m = folium.Map(location=st.session_state.map_view['center'], 
                   zoom_start=st.session_state.map_view['zoom'], 
                   tiles='CartoDB Positron')

    for r in df.itertuples():
        folium_color, _ = get_color(r.travel_date, min_y, max_y)
        folium.Marker(
            location=[r.lat, r.lon],
            popup=f"{r.city} - {r.travel_date.strftime('%Y-%m')}",
            icon=folium.Icon(color=folium_color, icon='cloud')
        ).add_to(m)

    st_folium(m, use_container_width=True, height=500, 
              center=st.session_state.map_view['center'], 
              zoom=st.session_state.map_view['zoom'])

    # --- Data Table ---
    st.dataframe(df[['travel_date', 'city', 'country']].sort_values('travel_date', ascending=False), use_container_width=True)
else:
    st.info("Log a trip to see your globe!")
