WITH station_daily AS (
    SELECT
        city,
        sensor_id,
        DATE(timestamp_utc) AS date,
        AVG(pm25) AS station_avg_pm25,
        COUNT(*) AS station_measurement_count
    FROM "vietnam_air_quality"."analytics_intermediate"."int_hourly_air_quality"
    WHERE pm25 IS NOT NULL
    GROUP BY city, sensor_id, DATE(timestamp_utc)
),

city_daily AS (
    SELECT
        city,
        date,
        AVG(station_avg_pm25) AS avg_pm25,
        COUNT(*) AS station_count,
        SUM(station_measurement_count) AS measurement_count,
        MIN(station_avg_pm25) AS min_station_pm25,
        MAX(station_avg_pm25) AS max_station_pm25
    FROM station_daily
    GROUP BY city, date
)

SELECT * FROM city_daily