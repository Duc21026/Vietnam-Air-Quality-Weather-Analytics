
  
    

  create  table "vietnam_air_quality"."analytics_analytics"."mart_city_daily__dbt_tmp"
  
  
    as
  
  (
    WITH hourly AS (
    SELECT * FROM "vietnam_air_quality"."analytics_intermediate"."int_air_quality_weather"
),

daily AS (
    SELECT
        city,
        DATE(timestamp_utc) AS date,
        AVG(pm25) AS avg_pm25,
        AVG(pm10) AS avg_pm10,
        MAX(pm25) AS max_pm25,
        MAX(pm10) AS max_pm10,
        AVG(temperature) AS avg_temperature,
        AVG(relative_humidity) AS avg_humidity,
        AVG(wind_speed) AS avg_wind_speed,
        SUM(precipitation) AS total_precipitation,
        COUNT(*) AS record_count
    FROM hourly
    GROUP BY city, DATE(timestamp_utc)
)

SELECT * FROM daily
  );
  