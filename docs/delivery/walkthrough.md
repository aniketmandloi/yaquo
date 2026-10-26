# Video walkthrough script (8 minutes)

Unlisted YouTube video, two parts. Customer part first (about 3.5 minutes), then technical part (about 4 minutes), leaving slack under the 10-minute limit. Each part is capped at 5 minutes.

Figures come from the bundled snapshot. Check them on screen while recording.

## Part 1: Customer (procurement team), 0:00–3:30

**0:00–0:25 The problem.** A buyer purchases power a day ahead. Wind covers part of demand, so the buyer needs to know what wind forecast existed at decision time, and how far off forecasts usually are. Looking back at a forecast from a later download makes it look more accurate than it was. This app avoids that.

**0:25–1:30 Forecast view.** *Screen: the decision date bar at the top, then "Day-ahead forecast available at the decision cutoff". Pick 15 January.*

- The date bar drives both views. Delivery date is 16 January, shown separately.
- The cutoff is 09:00 London time. It is a pilot assumption, not an official auction deadline.
- Hover over the line: the MW value, when it was published, and its age at the cutoff.
- The data-quality summary says 24 of 24 hourly targets have a usable forecast. A gap would show as a gap, never as zero.

**1:30–2:45 Accuracy view.** *Screen: "Retrospective accuracy against retrieved actuals", same date.*

- Forecast and actual on one chart. Hover to see the error for an hour.
- Explain the sign: positive means more wind was forecast than arrived, which can leave a buyer short.
- 15 January: MAE 810 MW, bias +349 MW, RMSE 970 MW.
- *Click the January strip.* Most days sit above the line. Click 18 January (closest: MAE 684 MW), then 27 January (furthest: MAE 5,329 MW, overforecast).
- January overall: 744 matched hourly pairs, MAE about 2,022 MW, bias about +1,746 MW. 27 of 31 days were overforecast.

**2:45–3:30 Limits.** These are hindsight scores. Nobody knew them on 1 January. The data is Elexon-metered GB wind, and actuals are the latest retrieved, not final settlement. The app does not show volumes or savings, because the brief allows only these two datasets.

## Part 2: Technical lead, 3:30–7:30

**3:30–4:30 Architecture.** *Screen: the README architecture diagram.*

- React and Vite frontend, FastAPI backend. All analysis runs in Python.
- One process and one Docker image serve both `/api` and the built frontend ([ADR 0005](../adr/0005-one-origin-python-serves-frontend.md)).
- Heroku builds the image from `heroku.yml` onto one Basic dyno ([ADR 0006](../adr/0006-heroku-basic-container.md)).

**4:30–5:15 Core rules.** *Screen: `backend/app/forecasts.py`, then `accuracy.py`.*

- Pick the latest forecast published at or before the cutoff, for each target separately. Never fall back to an older one ([ADR 0002](../adr/0002-latest-publication-at-cutoff.md)).
- Join only on identical timestamps. No interpolation ([ADR 0003](../adr/0003-match-at-identical-target-times.md)).
- January metrics pool every matched error ([ADR 0004](../adr/0004-pool-errors-for-period-metrics.md)).

**5:15–6:15 Tests.** *Screen: terminal, run `(cd backend && pytest)`.*

- 41 tests through the HTTP API, with small hand-built snapshots, not the live Elexon feed.
- They cover cutoff equality, the January boundaries, conflicts, missing data versus zero, and metrics checked against hand-worked values.
- Frontend: `npm run lint` and `npm run build`.

**6:15–6:50 Data and delivery.** *Screen: `backend/data/snapshot/metadata.json`.*

- The snapshot records the query URLs, retrieval time, record counts and SHA-256 hashes. `fetch_snapshot.py` retrieves it again.
- Local run and Docker run are in the README.

**6:50–7:30 Trade-offs and next steps.** The snapshot is bundled rather than fetched live, which keeps the demo reliable within the time limit. Next steps: a configurable cutoff, scheduled data refresh, and an error estimate that uses only information available before each decision. AI assistance is disclosed in the README.
