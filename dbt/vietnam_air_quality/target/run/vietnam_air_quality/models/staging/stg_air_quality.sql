
  create view "vietnam_air_quality"."analytics_staging"."stg_air_quality__dbt_tmp"
    
    
  as (
    WITH source AS (
    SELECT * FROM "vietnam_air_quality"."raw"."raw_air_quality"
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
  );