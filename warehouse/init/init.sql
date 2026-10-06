-- Raw warehouse tables for Vietnam Air Quality & Weather Analytics

CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.raw_air_quality (
    id              SERIAL PRIMARY KEY,
    location_id     INTEGER NOT NULL,
    location_name   TEXT,
    city            TEXT NOT NULL,
    sensor_id       INTEGER NOT NULL,
    parameter       TEXT NOT NULL,
    value           DOUBLE PRECISION,
    unit            TEXT,
    timestamp_utc   TIMESTAMPTZ NOT NULL,
    latitude        DOUBLE PRECISION,
    longitude       DOUBLE PRECISION,
    source          TEXT DEFAULT 'openaq',
    ingested_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw.raw_weather (
    id                  SERIAL PRIMARY KEY,
    city                TEXT NOT NULL,
    latitude            DOUBLE PRECISION,
    longitude           DOUBLE PRECISION,
    timestamp           TIMESTAMPTZ NOT NULL,
    temperature         DOUBLE PRECISION,
    relative_humidity   DOUBLE PRECISION,
    precipitation       DOUBLE PRECISION,
    wind_speed          DOUBLE PRECISION,
    wind_direction      DOUBLE PRECISION,
    surface_pressure    DOUBLE PRECISION,
    source              TEXT DEFAULT 'open_meteo',
    ingested_at         TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_aq_ts ON raw.raw_air_quality (timestamp_utc);
CREATE INDEX IF NOT EXISTS idx_aq_city ON raw.raw_air_quality (city);
CREATE INDEX IF NOT EXISTS idx_aq_sensor ON raw.raw_air_quality (sensor_id);
CREATE INDEX IF NOT EXISTS idx_weather_ts ON raw.raw_weather (timestamp);
CREATE INDEX IF NOT EXISTS idx_weather_city ON raw.raw_weather (city);
