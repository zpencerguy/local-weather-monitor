from __future__ import annotations

import json
from typing import Any

import requests


AVIATION_WEATHER_URL = "https://aviationweather.gov/api/data/metar"


def fetch_latest_metar(station_id: str = "KDVT") -> dict[str, Any]:
    params = {
        "ids": station_id,
        "format": "json",
        "taf": "false",
    }
    response = requests.get(AVIATION_WEATHER_URL, params=params, timeout=30)
    response.raise_for_status()

    payload = response.json()
    if not isinstance(payload, list) or not payload:
        raise RuntimeError(f"No METAR data returned for station {station_id}")

    record = payload[0]
    if not isinstance(record, dict):
        raise RuntimeError("Unexpected METAR payload shape")

    return record


def main() -> None:
    metar = fetch_latest_metar()
    print(json.dumps(metar, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
