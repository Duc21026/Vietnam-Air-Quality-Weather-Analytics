
  create view "vietnam_air_quality"."analytics_intermediate"."int_hourly_air_quality__dbt_tmp"
    
    
  as (
    WITH air_quality AS (
    SELECT * FROM "vietnam_air_quality"."analytics_staging"."stg_air_quality"
),

pivoted AS (
    SELECT
        timestamp_utc,
        city,
        location_id,
        location_name,
        sensor_id,
        latitude,
        longitude,
        MAX(CASE WHEN parameter = 'pm25' THEN value END) AS pm25,
        MAX(CASE WHEN parameter = 'pm10' THEN value END) AS pm10,
        MAX(CASE WHEN parameter = 'pm25' THEN unit END) AS pm25_unit,
        MAX(CASE WHEN parameter = 'pm10' THEN unit END) AS pm10_unit
    FROM air_quality
    GROUP BY timestamp_utc, city, location_id, location_name, sensor_id, latitude, longitude
)

SELECT * FROM pivoted
  );