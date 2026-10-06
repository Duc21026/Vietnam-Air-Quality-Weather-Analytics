"""OpenAQ API v3 client."""

import time
from datetime import datetime, timedelta, timezone

import requests

BASE_URL = "https://api.openaq.org/v3"
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2


class OpenAQError(Exception):
    pass


def _request(path: str, api_key: str, params: dict | None = None) -> dict:
    url = f"{BASE_URL}{path}"
    headers = {"X-API-Key": api_key, "Accept": "application/json"}
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=DEFAULT_TIMEOUT)
        except requests.Timeout:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise OpenAQError(f"timeout calling {path}")
        if resp.status_code == 429:
            wait = RETRY_DELAY * (attempt + 1) * 2
            time.sleep(wait)
            continue
        if resp.status_code == 401:
            raise OpenAQError("401 Unauthorized - invalid OpenAQ API key")
        if resp.status_code == 404:
            raise OpenAQError(f"404 Not Found: {path}")
        if resp.status_code != 200:
            raise OpenAQError(f"{resp.status_code} from {path}: {resp.text[:300]}")
        return resp.json()
    raise OpenAQError(f"max retries exceeded for {path}")


def fetch_sensor_hours(
    sensor_id: int,
    api_key: str,
    datetime_from: datetime,
    datetime_to: datetime,
    limit: int = 1000,
) -> list[dict]:
    results = []
    offset = 0
    while True:
        params = {
            "datetime_from": datetime_from.isoformat(),
            "datetime_to": datetime_to.isoformat(),
            "limit": min(limit, 1000),
            "offset": offset,
        }
        data = _request(f"/sensors/{sensor_id}/hours", api_key, params)
        batch = data.get("results", [])
        results.extend(batch)
        found = (data.get("meta") or {}).get("found", 0)
        if len(results) >= found or len(batch) < params["limit"]:
            break
        offset += len(batch)
    return results


def fetch_location_hours(
    location_id: int,
    api_key: str,
    datetime_from: datetime,
    datetime_to: datetime,
) -> list[dict]:
    results = []
    offset = 0
    while True:
        params = {
            "datetime_from": datetime_from.isoformat(),
            "datetime_to": datetime_to.isoformat(),
            "limit": 1000,
            "offset": offset,
        }
        data = _request(f"/locations/{location_id}/hours", api_key, params)
        batch = data.get("results", [])
        results.extend(batch)
        found = (data.get("meta") or {}).get("found", 0)
        if len(results) >= found or len(batch) < params["limit"]:
            break
        offset += len(batch)
    return results
