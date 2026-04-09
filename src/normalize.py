from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def _to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, str) and value.endswith("+"):
        value = value[:-1]
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _to_iso_utc(value: Any) -> str | None:
    if value in (None, ""):
        return None

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    if isinstance(value, str) and value.endswith("Z"):
        return value

    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None

    return parsed.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _altimeter_to_inhg(value: Any) -> float | None:
    numeric = _to_float(value)
    if numeric is None:
        return None
    if numeric > 100:
        return round(numeric * 0.0295299830714, 2)
    return numeric


def normalize_metar(raw: dict[str, Any], fetched_at: datetime | None = None) -> dict[str, Any]:
    fetched_at = fetched_at or datetime.now(UTC).replace(microsecond=0)

    normalized = {
        "schema_version": 1,
        "source": "aviationweather.gov/api/data/metar",
        "station": raw.get("icaoId") or raw.get("station") or "KDVT",
        "fetched_at_utc": fetched_at.isoformat().replace("+00:00", "Z"),
        "observed_at_utc": _to_iso_utc(raw.get("obsTime") or raw.get("observationTime") or raw.get("reportTime")),
        "temperature_c": _to_float(raw.get("temp")),
        "dewpoint_c": _to_float(raw.get("dewp")),
        "wind_speed_kt": _to_int(raw.get("wspd")),
        "wind_direction_deg": _to_int(raw.get("wdir")),
        "visibility_mi": _to_float(raw.get("visib")),
        "altimeter_in_hg": _altimeter_to_inhg(raw.get("altim")),
        "flight_category": raw.get("fltCat"),
        "raw_metar": raw.get("rawOb") or raw.get("raw_text"),
    }
    return normalized
