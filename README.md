# Wind Procurement Pilot

A web app for a UK utility's day-ahead procurement team. For each January 2026 purchase decision it shows the Elexon wind generation forecast that was available at the decision time, and how accurate that forecast turned out to be against actual generation.

- **Hosted app:** not deployed yet.
- **Video walkthrough:** not recorded yet.

## What it shows

1. **Day-ahead forecast (as of the decision).** Pick a decision date from January 1 to 31, 2026. The app shows the next day's hourly wind forecast as it stood at 09:00 Europe/London on the decision date, with each value's publication time and age at the cutoff.
2. **Retrospective accuracy.** The same selected forecasts compared with actual generation at identical target times, with MAE, mean signed error (bias) and RMSE in MW for the chosen day and for the whole of January.

## Directories

| Path | Contents |
| --- | --- |
| `backend/app/` | FastAPI service. `forecasts.py` selects forecasts at the decision cutoff, `accuracy.py` matches them with actuals and computes metrics, `snapshot.py` loads the bundled data, `main.py` defines the API and serves the built frontend, `server.py` is the entry point. |
| `backend/data/snapshot/` | Bundled Elexon WINDFOR and FUELHH WIND records, plus `metadata.json` with their provenance. The app reads only these files. |
| `backend/scripts/fetch_snapshot.py` | Retrieves the snapshot again from the public Elexon API. |
| `backend/tests/` | API tests against small controlled snapshots. |
| `frontend/src/` | React app. `ForecastView.tsx` and `AccuracyView.tsx` are the two views, `SnapshotProvenance.tsx` shows the data source, `api.ts` is the typed API client. |
| `docs/` | Planning, research notes, and the video walkthrough scripts. |
| `GLOSSARY.md` | Domain terms used across code and docs. |
| `Dockerfile`, `heroku.yml` | One image serving the frontend and API; Heroku builds it from `heroku.yml`. |

## Running locally

Requirements: Python 3.12 (a conda environment is provided) and Node.js 20.19+ or 22.12+.

Backend, from `backend/`:

```sh
conda env create -f environment.yml
conda activate yaquo
uvicorn app.server:app --port 8000
```

Frontend dev server, from `frontend/` in a second terminal:

```sh
npm ci
npm run dev
```

Open the address Vite prints. It proxies `/api` to the backend on port 8000.

To serve everything from the backend instead, run `npm run build` in `frontend/` and restart the backend; it serves `frontend/dist` at http://localhost:8000 when that folder exists.

### Checks

```sh
cd backend && pytest
cd frontend && npm run lint && npm run build
```

## Docker

From the repository root:

```sh
docker build -t wind-pilot .
docker run --rm -p 8000:8000 wind-pilot
```

Then open http://localhost:8000. The container listens on `$PORT` (default 8000), so `docker run --rm -e PORT=5000 -p 5000:5000 wind-pilot` also works.

## Deploying to Heroku

The app runs on one Heroku Basic dyno using the container stack. Heroku builds the image from `heroku.yml`:

```sh
heroku create <app-name>
heroku stack:set container --app <app-name>
git push heroku main
heroku ps:type web=basic --app <app-name>
```

## Data and methodology

**Source.** Only two Elexon datasets are used: WINDFOR (wind forecasts) and FUELHH records with `fuelType` `WIND` (actual generation). Values are Elexon-reported GB wind generation in MW. Elexon covers wind farms visible to the system operator through operational metering, not every UK wind generator.

**Snapshot.** The app reads a bundled snapshot instead of calling Elexon on each request, so the demo does not depend on the live API. `backend/data/snapshot/metadata.json` records the query URLs and publication-time bounds, the retrieval time, record counts, SHA-256 hashes, and the one transformation applied (keeping only WIND rows from FUELHH). Run `python scripts/fetch_snapshot.py` from `backend/` to retrieve it again; see [backend/README.md](backend/README.md) for details.

**Decision cutoff.** Each decision date's cutoff is 09:00 Europe/London. This is a pilot assumption, not an official auction deadline. The delivery day is the following calendar day. For each hourly target in the delivery day, the app takes the latest forecast published at or before the cutoff. A later forecast is never used, even if it would score better.

**Actuals.** For each half-hour target, the latest actual publication in the snapshot is used.

**Matching.** Forecasts and actuals are compared only at identical target times. Forecasts are hourly and actuals half-hourly, so 24 of the 48 actuals on each delivery day are compared and the other 24 are not. Nothing is interpolated or averaged, and missing values are never treated as zero.

**Metrics.** Forecast error is forecast minus actual, in MW. A positive error means wind was overforecast, which can leave a buyer short if that wind was counted as supply.

- MAE: the average size of the errors.
- Bias (mean signed error): the average error, showing a tendency to over- or underforecast.
- RMSE: the square root of the average squared error, so large misses count more.

The January figures pool every matched error from all 31 decisions rather than averaging the daily figures. When a day has no valid pairs, metrics are reported as unavailable, not zero.

## Limitations

- Accuracy figures are retrospective. They were not known at earlier January decisions and are not a forward risk estimate.
- Actuals are the latest within the retrieval window (publications up to 2026-02-03). Later corrections and final settlement values were not checked.
- The snapshot showed 24 hourly forecasts and 48 half-hour actuals per delivery day, all 744 hourly targets matched. This is what the retrieved data contained, not a guarantee from Elexon.
- Forecast publication time is used as the time a forecast became available.
- The pilot does not include demand, prices, portfolios, purchase volumes, or financial savings, as the brief allows only the two wind datasets.

## AI assistance

This project was built with AI assistance. Claude Code (Anthropic) was used for domain and deployment research, planning, writing code, tests, and documentation. I reviewed the plans, decisions, and changes.
