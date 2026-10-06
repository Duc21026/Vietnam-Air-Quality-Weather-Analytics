"""OpenAQ location discovery and metadata."""

from ingestion.openaq.client import _request


def discover_locations(
    api_key: str,
    lat: float,
    lon: float,
    radius_m: int = 25000,
    limit: int = 100,
) -> list[dict]:
    data = _request("/locations", api_key, {
        "coordinates": f"{lat},{lon}",
        "radius": radius_m,
        "limit": limit,
    })
    return data.get("results", [])


def get_location_detail(api_key: str, location_id: int) -> dict:
    data = _request(f"/locations/{location_id}", api_key)
    results = data.get("results", [])
    return results[0] if results else {}


def sensor_parameters(location: dict) -> set[str]:
    return {
        s.get("parameter", {}).get("name", "")
        for s in location.get("sensors", [])
        if s.get("parameter")
    }
