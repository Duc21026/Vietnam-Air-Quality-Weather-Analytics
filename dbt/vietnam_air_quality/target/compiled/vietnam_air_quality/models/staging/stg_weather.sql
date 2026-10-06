with source AS (
    SELECT * FROM "vietnam_air_quality"."raw"."raw_weather"
),

renamed AS (
    SELECT
        id,
        city,
        latitude,
        longitude,
        timestamp,
        temperature,
        relative_humidity,
        precipitation,
        wind_speed,
        wind_direction,
        surface_pressure,
        source,
        ingested_at
    FROM source
)

SELECT * FROM renamed