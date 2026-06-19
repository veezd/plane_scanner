import streamlit as st
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
    latest_only = st.checkbox("Tylko najnowsze dane samolotu", value=True)
    origin_country = st.selectbox("Kraj pochodzenia", countries)
    category = st.selectbox("Kategoria", categories)

    with st.container(border=True) as area_container:
        cords_or_city = st.segmented_control('Lokalizacja', ['miasto', 'koordynaty'],
                                             selection_mode="single",
                                             default='miasto',
                                             required=True)
        
        if cords_or_city == "koordynaty":
            st.text('Zakres długości geograficznej')
            lo_col1, lo_col2 = st.columns(2)
            lomin = lo_col1.number_input('Dolny', value=None, key='lomin')
            lomax = lo_col2.number_input('Górny', value=None, key='lomax')

            st.text('Zakres szerekości geograficznej')
            la_col1, la_col2 = st.columns(2)
            lamin = la_col1.number_input('Dolny', value=None, key='lamin')
            lamax = la_col2.number_input('Górny', value=None, key='lamax')
            area = [st.session_state['lamin'], st.session_state['lomin'], st.session_state['lamax'], st.session_state['lomax']]
        else:
            area = st.selectbox("Miasto", areas)

    velocity = st.slider("Minimalna prędkość [m/s]", min_value=0, max_value=350)

    with st.container(border=True) as c:
        geo_or_baro = st.segmented_control("Wysokość [m]", ["geometryczna", "barometryczna"],
                                        selection_mode="single",
                                        default="geometryczna",
                                        required=True)
        col1, col2 = st.columns(2)
        if geo_or_baro == "geometryczna":
            min_geo_alt = col1.number_input('Minimalna', value=None, step=10)
            max_geo_alt = col2.number_input('Maksymalna', value=None, step=10)
            min_baro_alt = None
            max_baro_alt = None
        else:
            min_baro_alt = col1.number_input('Minimalna', value=None)
            max_baro_alt = col2.number_input('Maksymalna', value=None)
            min_geo_alt = None
            max_geo_alt = None

    icao = st.text_input("icao24", max_chars=6, placeholder="Wpisz...")
    callsign = st.text_input("Oznaczenie lotu", max_chars=6, placeholder="Wpisz...")

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

#pobranie danych z bazy (do wyświetlanej tabeli)
df, query= dashboard_methods.fetch_filtered_dataframe(
    category=category,
    area=area,
    velocity=velocity,
    geo_alt=[min_geo_alt,max_geo_alt],
    baro_alt=[min_baro_alt,max_baro_alt],
    origin_country=origin_country,
    time_period=[start_time,end_time],
    icao=icao,
    callsign=callsign,
    latest_only=latest_only)


#tworzenie mapy

#pobranie danych do mapy (zawsze tylko najnowsze i nie starsze niż 15 minut)

if start_time is None:
    now = datetime.datetime.now()
    t = datetime.timedelta(minutes=15)
    start_time = now - t

df_map, query= dashboard_methods.fetch_filtered_dataframe(
    category=category,
    area=area,
    velocity=velocity,
    geo_alt=[min_geo_alt,max_geo_alt],
    baro_alt=[min_baro_alt,max_baro_alt],
    origin_country=origin_country,
    time_period=[start_time,end_time],
    icao=icao,
    callsign=callsign,
    latest_only=True)
st.subheader("Mapa samolotów")

df_map = df_map.rename(columns={
    "długość geograficzna": "longitude",
    "szerokość geograficzna": "latitude"
})
icon_url = dashboard_methods.image_to_base64("docs/plane_icon.png")
df_map["icon_data"] = [{
    "url": icon_url,
    "width": 128,
    "height": 128,
    "anchorY": 128
}] * len(df_map)

layer = pdk.Layer(
    "IconLayer",
    data=df_map,
    get_icon="icon_data",
    get_size=3,
    size_scale=10,
    get_position="[longitude, latitude]",
    get_angle="true_track",
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=52.0,
    longitude=19.0,
    zoom=5
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "text": "icao24: {icao24}\nLot: {oznaczenie lotu}"
    },
    map_style=None
)

st.pydeck_chart(deck)


#wyświetlanie tabeli
df = df.drop(columns=["true_track"])
st.write(df)

#do debugowania
if visible_query:
    st.write(query)
