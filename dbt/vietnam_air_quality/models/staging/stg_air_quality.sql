WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_air_quality') }}
),

renamed AS (
    SELECT
        id,
        location_id,
        location_name,
        city,
        sensor_id,
        parameter,
        value,
        unit,
        timestamp_utc,
        latitude,
        longitude,
        source,
        ingested_at
    FROM source
)

SELECT * FROM renamed
