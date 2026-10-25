# Backend

FastAPI service exposing decision-time wind forecasts and their retrospective accuracy from a bundled Elexon snapshot.

## Setup

```sh
conda env create -f environment.yml
conda activate yaquo
```

## Run and test

From this directory:

```sh
uvicorn app.server:app --port 8000
pytest
```

The frontend dev server proxies `/api` to port 8000.

## API

- `GET /api/forecasts?decision_date=2026-01-15`: the delivery day's hourly targets with the forecast selected at the 09:00 Europe/London cutoff, its publication time and age, and data-quality counts. Dates outside 2026-01-01 to 2026-01-31 return 422.
- `GET /api/accuracy?decision_date=2026-01-15`: the same selected forecasts compared with actual generation at identical target times, plus whole-January results. Same date rules as above.
  - Actuals: for each target, the latest publication in the snapshot. Conflicting or invalid latest values are excluded, with no fallback to older publications. Missing values are never treated as zero.
  - Error is forecast minus actual in MW; positive means wind was overforecast. MAE, bias (mean signed error), and RMSE use the matched pairs. They are `null` when there are none.
  - January metrics pool every matched error from all 31 decisions rather than averaging daily scores.
  - `period.days` lists each decision's delivery date and daily metrics, in date order.
  - Coverage counts hourly forecast targets, forecast and actual statuses at those hours, matched pairs, and the half-hour actual timeline separately. Forecasts are hourly and actuals half-hourly, so half the actual timeline is never compared.
- `GET /api/snapshot`: snapshot provenance (`data/snapshot/metadata.json`).

## Snapshot retrieval

`data/snapshot/` holds the data the app reads. To retrieve it again:

```sh
python scripts/fetch_snapshot.py
```

The script queries the public Elexon WINDFOR and FUELHH stream endpoints by publication time (no API key), keeps FUELHH records with `fuelType == "WIND"`, and writes:

- `windfor.json`: WINDFOR records published 2026-01-01T00:00Z to 2026-02-01T00:00Z, unchanged.
- `fuelhh_wind.json`: FUELHH WIND records published 2026-01-02T00:00Z to 2026-02-03T00:00Z, unchanged.
- `metadata.json`: query URLs and bounds, retrieval time, response and stored record counts, SHA-256 hashes of the raw responses and stored files, and the transformation applied.

Check stored files against the metadata with `shasum -a 256 data/snapshot/*.json`. The provider does not guarantee identical responses over time, so a new retrieval can change the hashes. Commit a new snapshot only after reviewing its differences.
