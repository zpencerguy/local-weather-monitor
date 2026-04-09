from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from build_report import write_summary
from fetch_metar import fetch_latest_metar
from normalize import normalize_metar


ROOT = Path(__file__).resolve().parent.parent
LATEST_PATH = ROOT / "data/latest/kdvt_metar.json"
HISTORY_ROOT = ROOT / "data/history/observations"
REPORT_PATH = ROOT / "reports/latest_summary.md"


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _history_path(snapshot: dict[str, Any]) -> Path:
    observed_at = snapshot.get("observed_at_utc")
    if observed_at:
        dt = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    else:
        dt = datetime.now(UTC)

    return HISTORY_ROOT / dt.strftime("%Y/%m") / f"{dt.strftime('%Y-%m-%dT%H%MZ')}.json"


def run() -> None:
    previous = _read_json(LATEST_PATH)
    raw_metar = fetch_latest_metar("KDVT")
    snapshot = normalize_metar(raw_metar)

    _write_json(LATEST_PATH, snapshot)
    _write_json(_history_path(snapshot), snapshot)
    write_summary(REPORT_PATH, snapshot, previous)


if __name__ == "__main__":
    run()
