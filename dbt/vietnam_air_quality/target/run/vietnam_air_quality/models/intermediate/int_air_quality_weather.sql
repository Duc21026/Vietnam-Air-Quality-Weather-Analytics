
  create view "vietnam_air_quality"."analytics_intermediate"."int_air_quality_weather__dbt_tmp"
    
    
  as (
    WITH air_quality AS (
    SELECT * FROM "vietnam_air_quality"."analytics_intermediate"."int_hourly_air_quality"
),

weather AS (
    SELECT * FROM "vietnam_air_quality"."analytics_staging"."stg_weather"
),

joined AS (
    SELECT
        aq.timestamp_utc,
        aq.city,
        aq.location_id,
        aq.location_name,
        aq.sensor_id,
        aq.pm25,
        aq.pm10,
        aq.pm25_unit,
        aq.pm10_unit,
        wx.temperature,
        wx.relative_humidity,
        wx.precipitation,
        wx.wind_speed,
        wx.wind_direction,
        wx.surface_pressure
    FROM air_quality aq
    LEFT JOIN weather wx
        ON aq.city = wx.city
        AND aq.timestamp_utc = wx.timestamp
)

SELECT * FROM joined
  );