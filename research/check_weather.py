"""Research script: validate Open-Meteo weather data for Hanoi and HCMC.

Usage:
    python research/check_weather.py

No API key required.
"""

from datetime import date, timedelta

import requests

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "surface_pressure",
    "wind_speed_10m",
    "wind_direction_10m",
]
CITIES = [
    {"city": "Hanoi", "lat": 21.0285, "lon": 105.8542},
    {"city": "Ho Chi Minh City", "lat": 10.8231, "lon": 106.6297},
]
LOOKBACK_DAYS = 30


def check_city(city: dict) -> bool:
    print("=" * 70)
    print(f"CITY: {city['city']} ({city['lat']}, {city['lon']})")
    print("=" * 70)

    end = date.today()
    start = end - timedelta(days=LOOKBACK_DAYS)
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "hourly": ",".join(HOURLY_VARIABLES),
        "timezone": "Asia/Ho_Chi_Minh",
    }

    try:
        resp = requests.get(ARCHIVE_URL, params=params, timeout=30)
    except requests.Timeout:
        print("ERROR: timeout")
        return False
    if resp.status_code != 200:
        print(f"ERROR: HTTP {resp.status_code}: {resp.text[:300]}")
        return False

    payload = resp.json()
    hourly = payload.get("hourly", {})
    times = hourly.get("time", [])
    print(f"request: {resp.url}")
    print(f"elevation={payload.get('elevation')} timezone={payload.get('timezone')}")
    print(f"hourly_records={len(times)} "
          f"range={times[0] if times else 'n/a'} -> {times[-1] if times else 'n/a'}")

    ok = True
    for var in HOURLY_VARIABLES:
        values = hourly.get(var)
        if values is None:
            print(f"  {var:<22} MISSING from response")
            ok = False
            continue
        nulls = sum(1 for v in values if v is None)
        pct = 100.0 * nulls / len(values) if values else 0.0
        present = [v for v in values if v is not None]
        sample = f"min={min(present):.1f} max={max(present):.1f}" if present else "no data"
        print(f"  {var:<22} nulls={nulls}/{len(values)} ({pct:.1f}%)  {sample}")

    print("sample rows (first 3):")
    for i in range(min(3, len(times))):
        row = "  ".join(f"{v}={hourly.get(v, [None] * len(times))[i]}"
                        for v in HOURLY_VARIABLES)
        print(f"  {times[i]}  {row}")
    print()
    return ok


def main() -> None:
    all_ok = True
    for city in CITIES:
        all_ok = check_city(city) and all_ok
    print("RESULT:", "OK - weather data usable" if all_ok else "PROBLEMS FOUND")


if __name__ == "__main__":
    main()
