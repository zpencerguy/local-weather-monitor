from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _c_to_f(value: float | None) -> float | None:
    if value is None:
        return None
    return (value * 9 / 5) + 32


def _format_temp_line(snapshot: dict[str, Any], previous: dict[str, Any] | None) -> str:
    temp_c = snapshot.get("temperature_c")
    temp_f = _c_to_f(temp_c)
    if temp_f is None:
        return "- Temp: unavailable"

    change_text = "n/a"
    if previous and previous.get("temperature_c") is not None:
        previous_f = _c_to_f(previous["temperature_c"])
        if previous_f is not None:
            delta = temp_f - previous_f
            change_text = f"{delta:+.1f}F"

    return f"- Temp: {temp_f:.1f}F ({temp_c:.1f}C), change since last: {change_text}"


def _format_wind_line(snapshot: dict[str, Any]) -> str:
    speed = snapshot.get("wind_speed_kt")
    direction = snapshot.get("wind_direction_deg")

    if speed is None and direction is None:
        return "- Wind: unavailable"
    if speed is None:
        return f"- Wind: direction {direction}deg"
    if direction is None:
        return f"- Wind: {speed}kt"
    return f"- Wind: {speed}kt from {direction}deg"


def _build_events(snapshot: dict[str, Any], previous: dict[str, Any] | None) -> list[str]:
    events: list[str] = []

    category = snapshot.get("flight_category")
    if category:
        events.append(f"Flight category is {category}.")

    if previous:
        old_direction = previous.get("wind_direction_deg")
        new_direction = snapshot.get("wind_direction_deg")
        if old_direction is not None and new_direction is not None and abs(new_direction - old_direction) >= 45:
            events.append("Wind shift of at least 45 degrees detected.")

    if not events:
        events.append("No notable changes detected.")

    return events


def build_summary(snapshot: dict[str, Any], previous: dict[str, Any] | None = None) -> str:
    observed_at = snapshot.get("observed_at_utc") or "unknown"
    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    lines = [
        "# Latest Weather Summary",
        "",
        f"- Station: {snapshot.get('station', 'KDVT')}",
        f"- Observed at: {observed_at}",
        f"- Generated at: {generated_at}",
        _format_temp_line(snapshot, previous),
        _format_wind_line(snapshot),
        f"- Visibility: {snapshot.get('visibility_mi', 'unavailable')} mi",
        f"- Altimeter: {snapshot.get('altimeter_in_hg', 'unavailable')} inHg",
        "",
        "## Notable Events",
    ]
    lines.extend(f"- {event}" for event in _build_events(snapshot, previous))
    lines.append("")
    return "\n".join(lines)


def write_summary(report_path: Path, snapshot: dict[str, Any], previous: dict[str, Any] | None = None) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_summary(snapshot, previous), encoding="utf-8")
