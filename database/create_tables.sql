-- to query jest zvibe kodowane, nie jestem jakos fanem SQL, Jafar mozesz to sprawdzic pozniej jak bedziesz
-- grzebal przy bazie danych

CREATE TABLE IF NOT EXISTS countries (
    country_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY, 
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS monitored_areas (
    area_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    lamin REAL NOT NULL,
    lomin REAL NOT NULL,
    lamax REAL NOT NULL,
    lomax REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS import_logs (
    import_id INTEGER PRIMARY KEY AUTOINCREMENT,
    imported_at DATETIME NOT NULL,
    api_name TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    records_received INTEGER NOT NULL,
    records_saved INTEGER NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT
);


CREATE TABLE IF NOT EXISTS aircraft (
    aircraft_id INTEGER PRIMARY KEY AUTOINCREMENT,
    icao24 TEXT UNIQUE NOT NULL, 
    callsign TEXT,
    country_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS aircraft_position (
    position_id INTEGER PRIMARY KEY AUTOINCREMENT,
    aircraft_id INTEGER NOT NULL,
    import_id INTEGER NOT NULL,
    area_id INTEGER NOT NULL,
    time_position DATETIME,
    longitude REAL NOT NULL,
    latitude REAL NOT NULL,
    geo_altitude REAL,
    baro_altitude REAL,
    FOREIGN KEY (aircraft_id) REFERENCES aircraft(aircraft_id),
    FOREIGN KEY (import_id) REFERENCES import_logs(import_id),
    FOREIGN KEY (area_id) REFERENCES monitored_areas(area_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_aircraft_position_unique 
ON aircraft_position (aircraft_id, import_id);


CREATE TABLE IF NOT EXISTS aircraft_movement (
    position_id INTEGER PRIMARY KEY,
    velocity REAL,
    true_track REAL,
    FOREIGN KEY (position_id) REFERENCES aircraft_position(position_id)
);