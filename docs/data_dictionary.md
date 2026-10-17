# Data Dictionary

## `mart_city_pm25_comparison`

Station-balanced daily PM2.5 comparison per city. One row per `city` per `date`.
Source model: `int_hourly_air_quality` (filtered to `pm25 IS NOT NULL`).
Materialized as a table in schema `analytics_analytics`.

| Column | Type | Description |
|---|---|---|
| `city` | text | City label. Standardized to `Hanoi` or `Ho Chi Minh City`. |
| `date` | date | Calendar day (UTC) of the measurements. |
| `avg_pm25` | double precision | Mean of the station-level daily PM2.5 averages (µg/m³). Stations are weighted equally. |
| `station_count` | bigint | Number of monitoring stations reporting that day. |
| `measurement_count` | bigint | Number of hourly PM2.5 readings contributing to the day. |
| `min_station_pm25` | double precision | Lowest station daily average (µg/m³). |
| `max_station_pm25` | double precision | Highest station daily average (µg/m³). |

## Metric definition

**Station-balanced daily average.** Each station's day is averaged first, then the
daily city value is the mean of the available station averages, and the period value
is the mean of the daily city values over the selected dates. This prevents a
frequently-reporting station from dominating a city's average.

### Rules applied
- PM2.5 only (`pm25` parameter); no other pollutants.
- Same start and end date used for both cities.
- Units are `µg/m³` for both cities.
- City labels standardized (verified: only `Hanoi`, `Ho Chi Minh City`).
- `pm25 IS NULL` rows excluded (missing measurements are never treated as zero).
- Duplicate raw rows are collapsed by dbt via `GROUP BY sensor_id, timestamp_utc` in
  `int_hourly_air_quality` (`MAX` aggregation).

### Reference result (period 2026-09-29 → 2026-10-17)
| City | Station-balanced avg PM2.5 | Stations |
|---|---|---|
| Hanoi | 49.21 µg/m³ | 2 |
| Ho Chi Minh City | 34.37 µg/m³ | 1 |

Hanoi has the higher average PM2.5. The conclusion is unchanged under the simpler
measurement-weighted method (Hanoi 50.20 vs HCMC 34.24 µg/m³).

### Limitations
- Coverage is asymmetric: Hanoi has 2 monitoring stations, Ho Chi Minh City only 1.
- Partial days at the edges of the range contain fewer measurements.
- `raw.raw_air_quality` accumulates duplicate rows across loads (loader uses
  `ON CONFLICT DO NOTHING` without a unique constraint); dbt de-duplicates them
  downstream. A unique index on `(sensor_id, parameter, timestamp_utc)` would fix
  this at the source.
