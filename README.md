# Local Weather Monitor

Track hyperlocal weather for Deer Valley Airport (`KDVT`) using a lightweight git-scraping workflow.

This repository is designed to act as:
- Scheduler via GitHub Actions
- Scraper via Python scripts
- Time-series store via git history
- Audit trail via commits and diffs
- Reporting layer via generated Markdown

## Phase 1 Scope

The initial scaffold focuses on hourly METAR observations for `KDVT`:
- Fetch the latest observation
- Normalize it into deterministic JSON
- Save a timestamped snapshot
- Update `data/latest/kdvt_metar.json`
- Generate `reports/latest_summary.md`
- Commit and push only when data changes

## Repository Layout

```text
.
├── .github/workflows/scrape.yml
├── data/
│   ├── history/
│   │   ├── daily/
│   │   └── observations/
│   └── latest/
├── reports/
├── src/
│   ├── build_report.py
│   ├── fetch_metar.py
│   ├── normalize.py
│   └── run_pipeline.py
└── requirements.txt
```

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/run_pipeline.py
```

Generated files:
- `data/latest/kdvt_metar.json`
- `data/history/observations/YYYY/MM/<timestamp>.json`
- `reports/latest_summary.md`

## Data Model

The normalized METAR snapshot includes:
- `schema_version`
- `source`
- `station`
- `fetched_at_utc`
- `observed_at_utc`
- `temperature_c`
- `dewpoint_c`
- `wind_speed_kt`
- `wind_direction_deg`
- `visibility_mi`
- `altimeter_in_hg`
- `flight_category`
- `raw_metar`

Values not present in the source are stored as `null`.

## GitHub Actions Notes

The included workflow:
- Runs hourly
- Supports manual dispatch
- Writes weather artifacts into the repo
- Commits only when tracked files change

For pushes to succeed, the repository needs workflow write access to contents. The workflow sets `contents: write` for that purpose.
