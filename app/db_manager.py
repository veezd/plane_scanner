import sqlite3
import os
import threading
import queue
import datetime
import pandas as pd

class DBmanager:
    def __init__(self,queue,s_interval):
        current_file_path = os.path.abspath(__file__)
        app_dir = os.path.dirname(current_file_path)
        self.db_dir = os.path.join(os.path.dirname(app_dir), "database")
        self.db_path = os.path.join(self.db_dir, "data.db")

        self.connection, self.cursor = self.create_db_connection()
        
        self.send_query("create_tables.sql")
        self.send_query("add_monitored_areas.sql") # mamy kilka domyslnych, potrzebne pozniej do filtracji
        self.send_query("add_obj_categories.sql") # inicjalizacja kategorii obiektow latajacych


        self.work_queue = queue;
        self._stop_event = threading.Event()
        self._thread = None
        self.save_interval = s_interval

    def create_db_connection(self):
        con, cur = None, None 

        try:
            con = sqlite3.connect(self.db_path,check_same_thread=False)
            # ogolnie to jest niebezpieczne gdy zapisuje sie z wielu watkow ale u nas tylko jeden sluzy do zapisu wiec mozna to wylaczyc dla uproszczenia
            cur = con.cursor()
            # Odrazu przy polaczeniu inicjalizuje uzywane przez nas tablice
            print("[DBmanager] Connection successfully created")

        except sqlite3.Error as e:
            print(f"[DBmanager] A database error occurred: {e}")
        except Exception as e:
            print(f"[DBmanager] An unexpected error occurred: {e}")
            
        return (con, cur)
    
    # send_query jest dosc ogolnikowa metoda ktora mozna testowac rozne rzeczy
    # raczej w faktycznej obsludze appki beda bardziej wyspecjalizowane metody

    def send_query(self, query_or_file):
        # jako argumenty podac jedno zapytanie str, albo caly skrypt .sql (musi byc w folderze database)
        try:
            if isinstance(query_or_file, str) and query_or_file.strip().endswith('.sql'):
                
                if not os.path.isabs(query_or_file) and not os.path.exists(query_or_file):
                    file_path = os.path.join(self.db_dir, query_or_file)
                else:
                    file_path = query_or_file
                
                print(f"[DBmanager] Executing script: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as file:
                    sql_content = file.read()
                
                self.cursor.executescript(sql_content)
                
            else:
                self.cursor.execute(query_or_file)
            
            self.connection.commit()
            
        except FileNotFoundError:
            print(f"[DBmanager] No SQL script: {query_or_file} found")
            return None
        except sqlite3.Error as e:
            print(f"[DBmanager] Database error: {e}")
            if self.connection:
                self.connection.rollback() 
            return None
        
    
    # kopia metod watkowych z ApiReadera z lekka modyfikacja.
    def _save_loop(self):
        while not self._stop_event.is_set():
            try:
                lst = self.work_queue.get(timeout=self.save_interval) # timeout zawsze musi byc wiekszy niz download_interval z API
                self._save_state_vector(lst) 
                self.work_queue.task_done()
            except queue.Empty:
                print(f"[DBmanager] No data received from API in the last {self.save_interval} seconds.")
            except Exception as e:
                print(f"[DBmanager] Data saving error : {e}")

    def begin_saving(self):
        if self._thread is not None and self._thread.is_alive():
            print("[DBmanager] Called 'begin_saving' while data saving is already in progress")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target = self._save_loop,
            daemon = True
        )

        self._thread.start()
        print(f"[DBmanager] Started data saving with interval {self.save_interval}s")


    def end_saving(self):
        if self._thread is None or not self._thread.is_alive():
            print("[DBmanager] Called 'stop_saving' while data saving is offline")
            return
        
        print("[DBmanager] Stopping data saving thread")
        self._stop_event.set()
        self._thread.join()
        print("[DBmanager] Thread eliminated succesfully")
        return None

    def _save_state_vector(self, state_vector):
        try:
            if hasattr(state_vector, 'states'):
                states = state_vector.states
            else:
                states = state_vector.get("states", [])

            imported_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            records_received = len(states) if states is not None else 0
            records_saved = 0
            
            self.cursor.execute("""
                INSERT INTO import_logs (imported_at, api_name, endpoint, records_received, records_saved, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (imported_at, 'OpenSky API', 'get_states', records_received, 0, 'In Progress', None))
            
            import_id = self.cursor.lastrowid
            
            if states is None or len(states) == 0:
                self.cursor.execute("UPDATE import_logs SET status = 'Success' WHERE import_id = ?", (import_id,))
                self.connection.commit()
                return

            for state in states:
                is_dict = isinstance(state, dict)
                
                lat = state.get("latitude") if is_dict else state.latitude
                lon = state.get("longitude") if is_dict else state.longitude
                
                if lat is None or lon is None:
                    continue
                
                self.cursor.execute("""
                    SELECT area_id FROM monitored_areas 
                    WHERE ? BETWEEN lamin AND lamax AND ? BETWEEN lomin AND lomax
                """, (lat, lon))
                area_row = self.cursor.fetchone()
                
                if not area_row:
                    continue # Samolot leci poza monitorowanymi strefami, pomijamy go
                    
                area_id = area_row[0]
                
                icao24 = state.get("icao24") if is_dict else state.icao24
                callsign = state.get("callsign") if is_dict else state.callsign
                callsign = callsign.strip() if callsign else None
                
                origin_country = state.get("origin_country") if is_dict else state.origin_country
                if not origin_country:
                    origin_country = "Unknown"
                
                category = state.get("category") if is_dict else state.category
                category_id = category if category is not None else 0
                
                time_pos = state.get("time_position") if is_dict else state.time_position
                time_position_str = datetime.datetime.fromtimestamp(time_pos).strftime("%Y-%m-%d %H:%M:%S") if time_pos else None

                self.cursor.execute("INSERT OR IGNORE INTO countries (name) VALUES (?)", (origin_country,))
                self.cursor.execute("SELECT country_id FROM countries WHERE name = ?", (origin_country,))
                country_row = self.cursor.fetchone()
                country_id = country_row[0] if country_row else 1 
                
                self.cursor.execute("""
                    INSERT INTO aircraft (icao24, callsign, country_id, category_id)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(icao24) DO UPDATE SET 
                        callsign = excluded.callsign, 
                        category_id = excluded.category_id
                """, (icao24, callsign, country_id, category_id))
                
                self.cursor.execute("SELECT aircraft_id FROM aircraft WHERE icao24 = ?", (icao24,))
                aircraft_id = self.cursor.fetchone()[0]
                
                geo_alt = state.get("geo_altitude") if is_dict else state.geo_altitude
                baro_alt = state.get("baro_altitude") if is_dict else state.baro_altitude
                
                try:
                    self.cursor.execute("""
                        INSERT INTO aircraft_position 
                        (aircraft_id, import_id, area_id, time_position, longitude, latitude, geo_altitude, baro_altitude)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (aircraft_id, import_id, area_id, time_position_str, lon, lat, geo_alt, baro_alt))
                    
                    position_id = self.cursor.lastrowid
                    
                    velocity = state.get("velocity") if is_dict else state.velocity
                    true_track = state.get("true_track") if is_dict else state.true_track
                    
                    self.cursor.execute("""
                        INSERT INTO aircraft_movement (position_id, velocity, true_track)
                        VALUES (?, ?, ?)
                    """, (position_id, velocity, true_track))
                    
                    records_saved += 1
                except sqlite3.IntegrityError:
                    # Wyłapanie naruszenia UNIQUE indexu (aircraft_id, import_id) w tabeli aircraft_position
                    # Jeżeli taki wystąpi, po prostu go ignorujemy by program biegł dalej
                    pass

            self.cursor.execute("""
                UPDATE import_logs 
                SET records_saved = ?, status = 'Success' 
                WHERE import_id = ?
            """, (records_saved, import_id))
            
            self.connection.commit()
            print(f"[DBmanager] Succesfully saved {records_saved}/{records_received} tracking records to DB.")

        except Exception as e:
            if self.connection:
                self.connection.rollback()
            print(f"[DBmanager] Fatal error while saving state vector: {e}")
            
            if 'import_id' in locals():
                try:
                    self.cursor.execute("""
                        UPDATE import_logs 
                        SET status = 'Failed', error_message = ? 
                        WHERE import_id = ?
                    """, (str(e), import_id))
                    self.connection.commit()
                except Exception as inner_e:
                    print(f"[DBmanager] Could not log fatal error to import_logs: {inner_e}")

    def fetch_dataframe(self, query):
        try:
            return pd.read_sql_query(query, self.connection)

        except (sqlite3.Error, pd.errors.DatabaseError) as e:
            print(f"[DBmanager] Database error: {e}")
            return None