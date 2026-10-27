# Wind Procurement Pilot

A pilot for a UK utility's day-ahead procurement team. For each January 2026 purchase decision, it shows the Elexon wind generation forecast that was available at 09:00 London time on the decision day, and how accurate that forecast turned out to be against actual generation.

| | |
| --- | --- |
| **Live app** | _Not deployed yet. Add the Render URL here once it is live._ |
| **Video** | _Not recorded yet. Add the unlisted YouTube link here._ |
| **Specification** | [Issue #1](https://github.com/aniketmandloi/yaquo/issues/1) and [`docs/planning/wind-pilot-spec.md`](docs/planning/wind-pilot-spec.md) |
| **Tickets** | [#2 forecast view](https://github.com/aniketmandloi/yaquo/issues/2), [#3 accuracy view](https://github.com/aniketmandloi/yaquo/issues/3), [#4 delivery](https://github.com/aniketmandloi/yaquo/issues/4) |
| **Decisions** | [`docs/adr/`](docs/adr/) |

## What the app answers

1. **What did we know when we decided?** Pick a decision date (1–31 January 2026). The forecast view shows the next day's hourly wind forecast as published by 09:00 London time that day. Each value shows when its forecast was published and how old it was at the cutoff. Later publications are never used, even if they would have scored better.
2. **How wrong was it?** The accuracy view compares those same forecasts with the actual generation for the delivery day, and for all of January. It reports MAE, bias and RMSE in MW, along with coverage counts so you can see exactly which hours were compared.

## Quick start

Requirements: Python 3.12 (a conda environment file is provided) and Node.js 20.19+ or 22.12+.

**Backend**, from `backend/`:

```sh
conda env create -f environment.yml
conda activate yaquo
uvicorn app.server:app --port 8000
```

**Frontend**, from `frontend/` in a second terminal:

```sh
npm ci
npm run dev
```

Open the address Vite prints (usually http://localhost:5173). Requests to `/api` are proxied to port 8000.

To serve the whole app from the backend instead, build the frontend with `npm run build` and open http://localhost:8000. The backend serves `frontend/dist` whenever that folder exists.

**Checks**

```sh
(cd backend && pytest)
(cd frontend && npm run lint && npm run build)
```

**Docker** (from the repository root):

```sh
docker build -t wind-pilot .
docker run --rm -p 8000:8000 wind-pilot
```

The container listens on `$PORT` (default 8000). Open http://localhost:8000.

**Render** deploys the same image from the repository's `Dockerfile`. See [`docs/adr/0008-render-free-web-service.md`](docs/adr/0008-render-free-web-service.md) for why.

The free instance sleeps after 15 minutes without traffic. The first request after that can take about a minute while it restarts. Open the app shortly before reviewing it.

## Architecture

```text
Browser (React + Vite + Recharts)
  │  GET /api/forecasts?decision_date=…
  │  GET /api/accuracy?decision_date=…
  │  GET /api/snapshot
  ▼
FastAPI (Python)                       one process, one Docker image, one origin
  ├─ forecasts.py   cutoff selection    the same rules feed both views
  ├─ accuracy.py    matching + metrics  pairs only at identical target times
  ├─ snapshot.py    loads the bundle
  └─ main.py        API routes + serves frontend/dist (refresh-safe fallback)
  │
  ▼
backend/data/snapshot/                 bundled Elexon WINDFOR + FUELHH WIND
  ├─ windfor.json, fuelhh_wind.json    unchanged provider responses
  └─ metadata.json                     URLs, bounds, retrieval time, SHA-256
```

The analysis runs only in Python. React displays what the API returns, including loading, error and "insufficient data" states. The decision rules are recorded in [`docs/adr/`](docs/adr/).

## Directories

| Path | What it holds |
| --- | --- |
| `backend/app/` | API and analysis: cutoff selection (`forecasts.py`), matching and metrics (`accuracy.py`), snapshot loading (`snapshot.py`), routes and static serving (`main.py`), entry point (`server.py`). |
| `backend/data/snapshot/` | The bundled Elexon data and its provenance. The app reads only these files. |
| `backend/scripts/fetch_snapshot.py` | Retrieves the snapshot again from the public Elexon API. |
| `backend/tests/` | API tests against small hand-built snapshots. |
| `frontend/src/` | React views: `ForecastView.tsx`, `AccuracyView.tsx`, `JanuaryStrip.tsx`, `DecisionPicker.tsx`, `SnapshotProvenance.tsx`; typed client in `api.ts`. |
| `docs/planning/` | The agreed scope, the specification, and the ticket breakdown. |
| `docs/research/` | Elexon data findings and the hosting research. |
| `docs/adr/` | Architecture decision records. |
| `docs/delivery/` | Video walkthrough script and the manual test checklist. |
| `GLOSSARY.md` | The domain terms used in code, UI and docs. |
| `Dockerfile`, `.dockerignore` | Container build, used by Docker and Render. |

## Data and method

**Sources.** Only two Elexon datasets are used: WINDFOR (wind forecasts) and FUELHH rows with `fuelType` `WIND` (actual generation). Values are Elexon-reported GB wind generation in MW. Elexon covers wind farms visible to the system operator through operational metering, not every UK wind generator or any customer portfolio.

**Snapshot.** The app reads a bundled snapshot rather than calling Elexon on each request. [`backend/data/snapshot/metadata.json`](backend/data/snapshot/metadata.json) records the query URLs and publication-time bounds, the retrieval time, record counts, SHA-256 hashes, and the one transformation applied (keeping only WIND rows from FUELHH). To retrieve it again: `python scripts/fetch_snapshot.py` from `backend/`. The provider may return different data over time, so review differences before committing a new snapshot.

**Cutoff.** Each decision's cutoff is 09:00 Europe/London on the decision date. This is a pilot assumption, not an official auction deadline. For each hourly target on the next calendar day, the app takes the latest forecast published at or before the cutoff. If that latest forecast is conflicting or invalid, the target is excluded. The app never falls back to an older forecast. See [ADR 0002](docs/adr/0002-latest-publication-at-cutoff.md).

**Actuals.** For each half-hour target, the latest actual publication in the snapshot is used.

**Matching.** Forecasts and actuals are compared only at identical target times. Forecasts are hourly and actuals are half-hourly, so 24 of the 48 actuals on each delivery day are compared and the others are not. Nothing is interpolated or averaged, and a missing value is never treated as zero. See [ADR 0003](docs/adr/0003-match-at-identical-target-times.md).

**Metrics.** Error is forecast minus actual, in MW. A positive error means wind was overforecast, which can leave a buyer short if it was counted as supply.

- **MAE:** the average size of the error, ignoring direction.
- **Bias (mean signed error):** the average error. Positive means overforecast, negative means underforecast.
- **RMSE:** like MAE, but larger misses count more heavily.

The January figures pool every matched error across all 31 decisions. They are not an average of the daily figures. See [ADR 0004](docs/adr/0004-pool-errors-for-period-metrics.md). When there are no valid pairs, a metric is reported as insufficient data, never as zero.

## Results at a glance

These figures come from the bundled snapshot. The app shows the full breakdown.

- **January 2026, all 31 decisions:** 744 matched hourly pairs. MAE about 2,022 MW, bias about +1,746 MW, RMSE about 2,497 MW.
- **27 of 31 decisions** had positive bias, meaning the forecast overestimated wind.
- **Closest day:** 18 January (MAE 684 MW, bias −684 MW).
- **Furthest day:** 27 January (MAE 5,329 MW, bias +5,329 MW).

## Limitations

- **Hindsight, not foresight.** The accuracy figures use outcomes that were not known at the decision time. They describe past performance and are not a forward risk estimate.
- **Latest, not final, actuals.** Actuals are the latest values in the retrieval window (publications up to 3 February 2026). Later corrections and final settlement data were not checked.
- **Cutoff is an assumption.** 09:00 London time is a pilot assumption, not an official auction deadline.
- **Archive completeness is observed, not guaranteed.** All 744 hourly targets matched in this snapshot. That reflects what Elexon returned for these queries, not a provider guarantee.
- **Scope is deliberately narrow.** The brief allows only the two wind datasets. The app does not cover demand, prices, customer portfolios, purchase volumes or financial savings.
- **No live data.** The app serves the bundled January snapshot and does not refresh itself.

## Testing

- **Automated:** `pytest` in `backend/` runs 41 tests against the API and static serving. They cover cutoff equality, January boundaries, exact matching, missing and conflicting records, latest-actual selection, the three metrics against hand-worked values, pooled period metrics, and static serving.
- **Frontend:** `npm run lint` and `npm run build` (which includes the TypeScript check).
- **Manual:** the step-by-step checklist is in [`docs/delivery/manual-testing.md`](docs/delivery/manual-testing.md).

## Decisions and history

- **Specification:** [`docs/planning/wind-pilot-spec.md`](docs/planning/wind-pilot-spec.md), also published as [issue #1](https://github.com/aniketmandloi/yaquo/issues/1).
- **Agreed scope and interview:** [`docs/planning/wind-pilot.md`](docs/planning/wind-pilot.md).
- **Tickets:** [`docs/planning/wind-pilot-tickets.md`](docs/planning/wind-pilot-tickets.md). Delivered in [PR #5](https://github.com/aniketmandloi/yaquo/pull/5) (forecast view), [PR #6](https://github.com/aniketmandloi/yaquo/pull/6) (accuracy view), [PR #7](https://github.com/aniketmandloi/yaquo/pull/7) (packaging and delivery) and [PR #8](https://github.com/aniketmandloi/yaquo/pull/8) (UI polish).
- **Data research:** [`docs/research/elexon-wind.md`](docs/research/elexon-wind.md).
- **Hosting research:** [`docs/research/deployment.md`](docs/research/deployment.md).
- **Architecture decisions:** [`docs/adr/`](docs/adr/).
- **Domain terms:** [`GLOSSARY.md`](GLOSSARY.md).

## AI assistance

This project was built with AI assistance. Claude Code (Anthropic) helped with research, planning, writing code, tests and documentation. A human reviewed each plan, decision and change, and made the final calls on scope and delivery.
