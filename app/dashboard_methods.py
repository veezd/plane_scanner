import pandas as pd
import streamlit as st
import sqlite3
from db_manager import DBmanager
import queue
import base64

@st.cache_resource
def get_db():
    s_interval = 15
    return DBmanager(queue.Queue(), s_interval)

@st.cache_data
def fetch_query(query, params=None):
    db = get_db()
    return db.fetch_dataframe(query, params)

@st.cache_data
def fetch_filtered_dataframe(
    category=None,
    area=None,
    velocity=None,
    geo_alt=None,
    baro_alt=None,
    origin_country=None,
    time_period=None,
    icao=None,
    callsign=None,
    latest_only=False
):
    if latest_only:
        query = """--sql
            SELECT 
                a.icao24,
                a.callsign AS "oznaczenie lotu",
                ap.longitude AS "długość geograficzna",
                ap.latitude AS "szerokość geograficzna",
                ap.geo_altitude AS "wysokość geometryczna [m]",
                ap.baro_altitude AS "wysokość barometryczna [m]",
                am.velocity AS "prędkość [m/s]",
                c.name AS "kategoria",
                ct.name AS "kraj pochodzenia",
                ap.time_position AS "czas pozycji",
                am.true_track
            FROM aircraft AS a
            JOIN countries AS ct 
                ON a.country_id = ct.country_id
            JOIN categories AS c 
                ON a.category_id = c.category_id
            JOIN aircraft_position AS ap 
                ON a.aircraft_id = ap.aircraft_id
            JOIN (
                SELECT 
                    aircraft_id, 
                    MAX(time_position) AS latest_position
                FROM aircraft_position
                GROUP BY aircraft_id
            ) AS lp
                ON ap.aircraft_id = lp.aircraft_id AND ap.time_position = lp.latest_position
            LEFT JOIN aircraft_movement AS am 
                ON ap.position_id = am.position_id
            """
    else:
        query = """--sql
            SELECT 
                a.icao24,
                a.callsign AS "oznaczenie lotu",
                ap.longitude AS "długość geograficzna",
                ap.latitude AS "szerokość geograficzna",
                ap.geo_altitude AS "wysokość geometryczna [m]",
                ap.baro_altitude AS "wysokość barometryczna [m]",
                am.velocity AS "prędkość [m/s]",
                c.name AS "kategoria",
                ct.name AS "kraj pochodzenia",
                ap.time_position AS "czas pozycji",
                am.true_track
            FROM aircraft AS a
            JOIN countries AS ct 
                ON a.country_id = ct.country_id
            JOIN categories AS c 
                ON a.category_id = c.category_id
            LEFT JOIN aircraft_position AS ap 
                ON a.aircraft_id = ap.aircraft_id
            LEFT JOIN aircraft_movement AS am 
                ON ap.position_id = am.position_id
            """

    conditions = []
    params = {}

    if category:
        conditions.append("c.name = :category")
        params["category"] = category

    if area:
        if area[0] is not None:
            conditions.append("ap.latitude >= :min_lat")
            params["min_lat"] = area[0]

        if area[1] is not None:
            conditions.append("ap.latitude <= :max_lat")
            params["max_lat"] = area[1]

        if area[2] is not None:
            conditions.append("ap.longitude >= :min_lon")
            params["min_lon"] = area[2]

        if area[3] is not None:
            conditions.append("ap.longitude <= :max_lon")
            params["max_lon"] = area[3]

    if velocity is not None:
        conditions.append("am.velocity >= :velocity")
        params["velocity"] = velocity

    if geo_alt:
        if geo_alt[0] is not None:
            conditions.append("ap.geo_altitude >= :min_geo_alt")
            params["min_geo_alt"] = geo_alt[0]

        if geo_alt[1] is not None:
            conditions.append("ap.geo_altitude <= :max_geo_alt")
            params["max_geo_alt"] = geo_alt[1]

    if baro_alt:
        if baro_alt[0] is not None:
            conditions.append("ap.baro_altitude >= :min_baro_alt")
            params["min_baro_alt"] = baro_alt[0]

        if baro_alt[1] is not None:
            conditions.append("ap.baro_altitude <= :max_baro_alt")
            params["max_baro_alt"] = baro_alt[1]

    if origin_country:
        conditions.append("ct.name = :origin_country")
        params["origin_country"] = origin_country

    if time_period:
        if time_period[0] is not None:
            conditions.append("ap.time_position >= :start_time")
            params["start_time"] = time_period[0]

        if time_period[1] is not None:
            conditions.append("ap.time_position <= :end_time")
            params["end_time"] = time_period[1]

    if icao:
        conditions.append("a.icao24 = :icao")
        params["icao"] = icao

    if callsign:
        conditions.append("a.callsign = :callsign")
        params["callsign"] = callsign

    if conditions:
        query += "\nWHERE " + " AND ".join(conditions)

    if not params:
        params = None

    return fetch_query(query, params), query

@st.cache_data
def image_to_base64(path):
    with open(path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    return f"data:image/png;base64,{encoded}"