WITH joined AS (
    SELECT * FROM {{ ref('int_air_quality_weather') }}
),

classified AS (
    SELECT
        *,
        CASE
            WHEN pm25 <= 12 THEN 'Good'
            WHEN pm25 <= 35.4 THEN 'Moderate'
            WHEN pm25 <= 55.4 THEN 'Unhealthy for Sensitive Groups'
            WHEN pm25 <= 150.4 THEN 'Unhealthy'
            WHEN pm25 <= 250.4 THEN 'Very Unhealthy'
            ELSE 'Hazardous'
        END AS pollution_level
    FROM joined
)

SELECT * FROM classified
