"""Research script: validate OpenAQ coverage for Hanoi and Ho Chi Minh City.

Usage:
    python research/check_openaq.py            # list locations + sensors
    python research/check_openaq.py --probe    # also probe recent hourly data

Requires OPENAQ_API_KEY in .env (get one at https://explore.openaq.org).
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

BASE_URL = "https://api.openaq.org/v3"
RADIUS_M = 25000
CITIES = [
    {"city": "Hanoi", "lat": 21.0285, "lon": 105.8542},
    {"city": "Ho Chi Minh City", "lat": 10.8231, "lon": 106.6297},
]
TARGET_PARAMETERS = ("pm25", "pm10")
MAX_CANDIDATES_PER_CITY = 3
PROBE_DAYS = 7
PROBE_LIMIT = 24 * 7


def load_api_key() -> str:
    load_dotenv()
    key = os.getenv("OPENAQ_API_KEY", "").strip()
    if not key:
        sys.exit("ERROR: OPENAQ_API_KEY not set. Add it to .env first.")
    return key


def api_get(path: str, api_key: str, params: dict | None = None) -> dict:
    try:
        resp = requests.get(
            f"{BASE_URL}{path}",
            headers={"X-API-Key": api_key, "Accept": "application/json"},
            params=params,
            timeout=30,
        )
    except requests.Timeout:
        sys.exit(f"ERROR: timeout calling {path}")
    if resp.status_code == 401:
        sys.exit("ERROR: 401 Unauthorized - invalid OpenAQ API key.")
    if resp.status_code == 429:
        sys.exit("ERROR: 429 rate limited - wait and rerun.")
    if resp.status_code != 200:
        sys.exit(f"ERROR: {resp.status_code} from {path}: {resp.text[:300]}")
    return resp.json()


def sensor_parameters(location: dict) -> set[str]:
    return {
        s.get("parameter", {}).get("name", "")
        for s in location.get("sensors", [])
        if s.get("parameter")
    }


def print_location(loc: dict) -> None:
    coords = loc.get("coordinates") or {}
    first = (loc.get("datetimeFirst") or {}).get("utc", "n/a")
    last = (loc.get("datetimeLast") or {}).get("utc", "n/a")
    print(f"  location_id={loc.get('id')}  name={loc.get('name')!r}")
    print(f"    coordinates: {coords.get('latitude')}, {coords.get('longitude')}")
    print(f"    distance_m:  {loc.get('distance')}")
    print(f"    first/last:  {first} -> {last}")
    for s in loc.get("sensors", []):
        p = s.get("parameter") or {}
        print(
            f"    sensor_id={s.get('id'):<8} {p.get('name', '?'):<8} "
            f"unit={p.get('units', '?'):<10} ({s.get('name')})"
        )


def probe_hourly(sensor_id: int, api_key: str) -> None:
    datetime_to = datetime.now(timezone.utc)
    datetime_from = datetime_to - timedelta(days=PROBE_DAYS)
    data = api_get(
        f"/sensors/{sensor_id}/hours",
        api_key,
        {
            "datetime_from": datetime_from.isoformat(),
            "datetime_to": datetime_to.isoformat(),
            "limit": PROBE_LIMIT,
        },
    )
    results = data.get("results", [])
    found = (data.get("meta") or {}).get("found")
    observed = [r for r in results if r.get("value") is not None]
    units = {((r.get("parameter") or {}).get("units")) for r in results} - {None}
    print(f"    probe sensor_id={sensor_id}: hours_found={found} "
          f"non_null={len(observed)} units={sorted(units)}")
    if observed:
        periods = [r.get("period") or {} for r in observed]
        first_utc = (periods[0].get("datetimeFrom") or {}).get("utc")
        last_utc = (periods[-1].get("datetimeTo") or {}).get("utc")
        print(f"      window: {first_utc} -> {last_utc}")
        sample = observed[:3]
        for r in sample:
            p = (r.get("period") or {}).get("datetimeFrom") or {}
            print(f"      {p.get('utc')}  value={r.get('value')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate OpenAQ data sources.")
    parser.add_argument("--probe", action="store_true",
                        help="also probe recent hourly measurements")
    args = parser.parse_args()

    api_key = load_api_key()

    for city in CITIES:
        print("=" * 70)
        print(f"CITY: {city['city']} ({city['lat']}, {city['lon']})")
        print("=" * 70)
        data = api_get(
            "/locations",
            api_key,
            {
                "coordinates": f"{city['lat']},{city['lon']}",
                "radius": RADIUS_M,
                "limit": 100,
            },
        )
        results = data.get("results", [])
        found = (data.get("meta") or {}).get("found")
        print(f"locations_found={found} (radius={RADIUS_M} m)")

        candidates = [loc for loc in results
                      if TARGET_PARAMETERS[0] in sensor_parameters(loc)]
        print(f"locations_with_pm25={len(candidates)}")

        for loc in results:
            params = sorted(sensor_parameters(loc))
            marker = " <== PM2.5 candidate" if TARGET_PARAMETERS[0] in params else ""
            print(f"  [{loc.get('id')}] {loc.get('name')!r} params={params}{marker}")

        print(f"\nDetails of up to {MAX_CANDIDATES_PER_CITY} PM2.5 candidate(s):")
        for loc in candidates[:MAX_CANDIDATES_PER_CITY]:
            print_location(loc)
            if args.probe:
                for s in loc.get("sensors", []):
                    p = (s.get("parameter") or {}).get("name")
                    if p in TARGET_PARAMETERS:
                        probe_hourly(s.get("id"), api_key)
            print()
        print()


if __name__ == "__main__":
    main()
