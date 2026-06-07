import pandas as pd
import streamlit as st
import sqlite3
from db_manager import DBmanager
import dashboard_methods
import datetime
import pydeck as pdk

db = dashboard_methods.get_db()
countries = dashboard_methods.fetch_query("""SELECT name 
                                   FROM countries
                                   ORDER BY name""")
countries = ["Wszystkie"] + countries["name"].tolist()

categories = dashboard_methods.fetch_query("""SELECT name 
                                   FROM categories
                                   ORDER BY category_id""")
categories = ["Wszystkie"] + categories["name"].tolist()

areas = dashboard_methods.fetch_query("""SELECT name 
                                   FROM monitored_areas
                                   ORDER BY name""")
areas = ["Wszystkie"] + areas["name"].tolist()

st.set_page_config(page_title="Plane scanner", layout="wide", page_icon="✈️")

with st.sidebar:
    st.header('Filtry')
    origin_country = st.selectbox("Kraj pochodzenia", countries)
    category = st.selectbox("Kategoria", categories)
    area = st.selectbox("Miasto", areas)
    velocity = st.slider("Minimalna prędkość [m/s]")
    with st.container(border=True) as c:
        geo_or_baro = st.segmented_control("Wysokość [m]", ["geometryczna", "barometryczna"],
                                        selection_mode="single",
                                        default="geometryczna",
                                        required=True)
        col1, col2 = st.columns(2)
        if geo_or_baro == "geometryczna":
            min_geo_alt = col1.number_input('Minimalna', value=None)
            max_geo_alt = col2.number_input('Maksymalna', value=None)
            min_baro_alt = None
            max_baro_alt = None
        else:
            min_baro_alt = col1.number_input('Minimalna', value=None)
            max_baro_alt = col2.number_input('Maksymalna', value=None)
            min_geo_alt = None
            max_geo_alt = None
    icao = st.text_input("icao24", max_chars=6, placeholder="Wpisz...")
    callsign = st.text_input("Oznaczenie lotu", max_chars=6, placeholder="Wpisz...")
    if "now" not in st.session_state:
        st.session_state.now = datetime.datetime.now()
        st.session_state.t = datetime.timedelta(hours=1)
    start_time = st.datetime_input('Czas początkowy', value = None)
    end_time = st.datetime_input('Czas końcowy', value = None)
    visible_query = st.checkbox('Pokaż zapytanie SQL', value=False)

if origin_country == "Wszystkie":
    origin_country = None

if category == "Wszystkie":
    category = None

if area == "Wszystkie":
    area = None

if velocity == 0:
    velocity = None

df, query= dashboard_methods.fetch_filtered_dataframe(
    category=category,
    area=area,
    velocity=velocity,
    geo_alt=[min_geo_alt,max_geo_alt],
    baro_alt=[min_baro_alt,max_baro_alt],
    origin_country=origin_country,
    time_period=[start_time,end_time],
    icao=icao,
    callsign=callsign)

#do debugowania
if visible_query:
    st.write(query)
st.write(df)
