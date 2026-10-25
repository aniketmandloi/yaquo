# Video walkthrough scripts

Two parts for the unlisted YouTube video: about 4.5 minutes for the customer and 4.5 for the technical lead, leaving slack under the 5-minute and 10-minute limits. Timings are targets. Figures were taken from the bundled snapshot through the API; check them against the screen while recording.

## Part 1: Customer (procurement team), about 4.5 minutes

**0:00–0:30 The problem.** You buy power a day ahead, and wind covers part of demand. To know how much to buy, you need the wind forecast that existed when you made the decision, and an idea of how wrong it tends to be. A forecast downloaded today includes later updates you didn't have, so comparing that with actuals makes past forecasts look better than they were.

**0:30–2:00 Forecast view.** *Screen: "Day-ahead forecast available at the decision cutoff", select 15 January.*

- Decision date 15 January, delivery date 16 January, shown separately.
- The cutoff is 09:00 London time. Say it is a pilot assumption that can be changed, not an official auction deadline.
- Hover over a point on the line: the forecast in MW, when it was published, and how old it was at the cutoff. All January decisions use the 07:30 publication.
- Data quality: 24 hourly targets, none missing or conflicting. Missing data would be flagged, never shown as zero.

**2:00–3:45 Accuracy view.** *Screen: "Retrospective accuracy against retrieved actuals".*

- Same date: forecast and actual on one chart. Hover to show a signed error.
- Explain the sign: positive means more wind was forecast than arrived, so a buyer relying on it could end up short.
- 15 January: MAE 810 MW, bias +349 MW, RMSE 970 MW.
- Contrast: 18 January was the closest day (MAE 684 MW, underforecast). 27 January was the furthest off (MAE 5,329 MW, all overforecast).
- January as a whole: MAE about 2,022 MW, bias about +1,746 MW, RMSE about 2,497 MW across 744 hourly pairs. 27 of 31 days had positive bias. The takeaway: in January 2026 the day-ahead forecast mostly overestimated wind.
- Coverage: all 744 hourly forecasts matched. Actuals are half-hourly, so half the actual timeline has no forecast to compare against. That's how often each dataset reports, not missing data.

**3:45–4:30 Limits and next steps.** These are scores in hindsight, not something known on 1 January. The data covers Elexon-metered GB wind only, and the actuals are the latest retrieved, not final settlement figures. Possible next steps: a different cutoff, live data, or a rolling error estimate that uses only data available before each decision.

## Part 2: Technical lead, about 4.5 minutes

**0:00–0:45 Architecture.** *Screen: README directory table.* A React and Vite frontend, plus a FastAPI backend that does all the analysis. One Docker image: Node builds the frontend, then the Python image serves both `/api` and the built files. Heroku builds it from `heroku.yml` onto one Basic dyno, which does not sleep. The app reads a bundled snapshot, so the demo doesn't depend on Elexon being up.

**0:45–1:30 Data and provenance.** *Screen: `backend/scripts/fetch_snapshot.py`, `metadata.json`.* The data was pulled from the Elexon stream endpoints by publication time and stored unchanged, apart from keeping only WIND rows from FUELHH. The metadata records the query URLs, bounds, retrieval time, record counts and SHA-256 hashes.

**1:30–2:45 Core logic.** *Screen: `backend/app/forecasts.py`, `accuracy.py`.*

- Times are parsed as timezone-aware values. The cutoff is 09:00 Europe/London, and the delivery day is the next London calendar day.
- One shared function picks the latest publication per target: forecasts at or before the cutoff, actuals with no time limit. If the latest value conflicts with another, the target is excluded rather than falling back to an older value. Exact duplicates count once.
- Forecasts and actuals are joined only on identical target times, with no interpolation. Error is forecast minus actual. January metrics pool all errors instead of averaging the daily figures. When there are no pairs, metrics are `null`, not 0.

**2:45–3:45 Testing and practices.** *Screen: `backend/tests/`.*

- Tests go through the HTTP API with small hand-built snapshots. They cover the cutoff (including a forecast published exactly at it), both January boundaries, invalid dates, exact matching, zero generation versus missing data, conflicts, actual revisions, hand-calculated metrics, and days with different numbers of pairs.
- Static file serving is tested too, including the refresh fallback and a blocked `..` path.
- Process: research notes, then an agreed spec (GitHub issue #1), split into three tickets and done test-first in small commits. Each ticket was a pull request. AI assistance is disclosed in the README.

**3:45–4:30 Trade-offs and limits.** The snapshot is bundled rather than fetched live, for reliability and to keep within 16 hours. The cutoff is fixed and the error figures are retrospective. Archive completeness and final settlement of the actuals are unverified. With more time: a configurable cutoff, scheduled data refresh, and an error estimate available before each decision.
