# Data Availability

Recorded from real API responses only. No simulated values.

Last checked: 2026-10-06 with `research/check_openaq.py --probe`
(OpenAQ API v3, `X-API-Key` header) and `research/check_weather.py`.

## Station Selection

| City | Location ID | Location Name | Latitude | Longitude | Pollutants |
|---|---:|---|---:|---:|---|
| Hanoi | 4946813 | Số 1 đường Giải Phóng - phường Bạch Mai - ĐHBK | 21.0052 | 105.8418 | pm25, pm10 |
| Hanoi | 6123215 | OceanPark | 20.9933 | 105.9441 | pm25 |
| Ho Chi Minh City | 3276359 | CMT8 | 10.78533 | 106.67029 | pm25 |

## Hanoi

### Station — location 4946813 (primary)

- Location ID: 4946813
- Location name: Số 1 đường Giải Phóng - phường Bạch Mai - ĐHBK
- Coordinates: 21.0052, 105.8418
- Provider: Hanoi Air Quality Monitoring Network
- Coverage: 2025-07-03T15:40:00Z -> 2026-10-06T07:35:00Z (still active)

### PM2.5 (sensor 13502154)

- Available: Yes
- Unit: µg/m³
- Hourly data: Yes — 147/147 non-null hours in the last 7 days
- Historical coverage: 2025-07-03 to present
- Missing periods: small gaps (147 of 168 hours returned in the 7-day probe window)

### PM10 (sensor 13502152)

- Available: Yes
- Unit: µg/m³
- Hourly data: Yes — 165/165 non-null hours in the last 7 days
- Historical coverage: 2025-07-03 to present
- Missing periods: small gaps (165 of 168 hours returned in the 7-day probe window)

### Station — location 6123215 (secondary, PM2.5 only)

- Coordinates: 20.9933, 105.9441
- Coverage: 2025-11-08T06:00:00Z -> 2026-10-06T07:00:00Z (active)
- PM2.5 (sensor 14581375): available, µg/m³, 167/167 non-null hours in last 7 days
- PM10: not available at this location

## Ho Chi Minh City

### Station — location 3276359

- Location ID: 3276359
- Location name: CMT8
- Coordinates: 10.78533, 106.67029
- Coverage: 2024-11-19T11:00:00Z -> 2026-10-06T07:00:00Z (still active)

### PM2.5 (sensor 11357424)

- Available: Yes
- Unit: µg/m³
- Hourly data: Yes — 167/167 non-null hours in the last 7 days
- Historical coverage: 2024-11-19 to present
- Missing periods: none observed in the 7-day probe window

### PM10 (sensor 11357395)

- Available: No (sensor exists but reports no hourly values in the last 30 days)
- Unit: µg/m³ (declared)
- Hourly data: No recent data — excluded from the pipeline for HCMC
- Notes: no other PM10 location within the 25 km API radius limit (max radius
  is 25000 m) reports recent data for HCMC. PM10 is optional in project scope.

## Weather (Open-Meteo)

Checked 2026-10-06 with `research/check_weather.py` (archive API, last 30 days, hourly, timezone Asia/Ho_Chi_Minh).

### Hanoi
- Accessible: Yes (HTTP 200, elevation 19.0 m)
- Hourly data: Yes - 744 records, 2026-09-06T00:00 -> 2026-10-06T23:00
- Variables: all 6 present, 0 nulls each
  - temperature_2m: 21.3 - 34.6 °C
  - relative_humidity_2m: 44 - 100 %
  - precipitation: 0.0 - 8.6 mm
  - surface_pressure: 1002.4 - 1018.7 hPa
  - wind_speed_10m: 0.2 - 20.7 km/h
  - wind_direction_10m: 1 - 360 °
- Time alignment with air quality (location + timestamp): Yes - hourly timestamps + city coordinates align with air-quality hourly data

### Ho Chi Minh City
- Accessible: Yes (HTTP 200, elevation 6.0 m)
- Hourly data: Yes - 744 records, 2026-09-06T00:00 -> 2026-10-06T23:00
- Variables: all 6 present, 0 nulls each
  - temperature_2m: 23.9 - 33.4 °C
  - relative_humidity_2m: 54 - 100 %
  - precipitation: 0.0 - 7.2 mm
  - surface_pressure: 1005.6 - 1014.9 hPa
  - wind_speed_10m: 0.2 - 16.9 km/h
  - wind_direction_10m: 2 - 360 °
- Time alignment with air quality (location + timestamp): Yes

## Time Alignment Check

Joined on UTC hour (OpenAQ hourly period start vs Open-Meteo hourly time),
last 3 days, checked 2026-10-06. Real values only.

| timestamp (UTC) | city | pm25 | temperature | humidity | precipitation | wind_speed |
|---|---|---:|---:|---:|---:|---:|
| 2026-10-06T04:00:00Z | Hanoi | 43.2 | 25.8 | 48 | 0.0 | 15.7 |
| 2026-10-06T05:00:00Z | Hanoi | 42.9 | 26.5 | 46 | 0.0 | 14.6 |
| 2026-10-06T06:00:00Z | Hanoi | 32.9 | 27.0 | 45 | 0.0 | 13.5 |
| 2026-10-06T03:00:00Z | HCMC | 47.9 | 30.4 | 72 | 0.1 | 2.9 |
| 2026-10-06T04:00:00Z | HCMC | 49.4 | 30.7 | 68 | 0.2 | 2.3 |
| 2026-10-06T05:00:00Z | HCMC | 44.3 | 31.0 | 67 | 0.2 | 1.6 |

Join coverage: Hanoi 58/58 air-quality hours matched a weather hour;
HCMC 71/71 matched. Units: PM2.5/PM10 µg/m³, temperature °C,
humidity %, precipitation mm, wind speed km/h.

## Data Availability Decision

- [x] Option A - Data is sufficient, continue to Step 2
- [ ] Option B - Data is insufficient, adjust station/city/pollutant/period

Notes:
- OpenAQ API v3 `GET /locations` and `GET /sensors/{id}/hours` work with
  `X-API-Key`; `radius` max is 25000 m; endpoint paths are relative to
  `https://api.openaq.org/v3`.
- HCMC has no PM10 coverage with recent data within 25 km → PM10 scoped
  to Hanoi only; PM2.5 covers both cities.
- Nearest stations to the city centers (e.g. US Diplomatic Post, Hoàn Kiếm)
  are stale (last data 2016 / 2024) — always check `datetimeLast` and probe
  hourly values before selecting a station.
