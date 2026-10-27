# Video script: exact words and screen actions

Target length: 8 minutes 30 seconds, under the 10-minute limit. Part 1 is for the customer (under 5 minutes). Part 2 is for the technical lead (under 5 minutes).

Before recording:
- Open the live app in an incognito window and wait for it to load. The free instance may need about a minute to wake up.
- Open the README, `docs/adr/`, and a terminal in `backend/` with `pytest` ready to run.
- Set the date bar to 15 January before you start Part 1.

Words in **bold** are what to say. Lines in *italics* are what to do on screen.

---

## Part 1: Customer

### 0:00–0:25 Problem

*Screen: the app's title and header.*

**"This is the Wind Procurement Pilot. It helps a procurement team see the wind forecast they had when they bought power, and how accurate it turned out to be."**

**"A buyer purchases power a day ahead. Wind covers part of demand, so the buyer needs the forecast that existed at decision time. A forecast downloaded later includes updates the buyer never saw, which makes the old forecast look better than it was."**

### 0:25–1:30 Forecast view

*Screen: scroll to the date bar at the top. It should show 15 January 2026.*

**"The date bar at the top controls both views. I'll pick 15 January, the decision date."**

*Screen: scroll down to "Known at the 09:00 cutoff".*

**"This view shows the forecast available at 09:00 London time on 15 January, for the next day, 16 January. The delivery date is shown separately so it's not confused with the decision date."**

**"The 09:00 cutoff is a pilot assumption. It isn't an official auction deadline."**

*Screen: hover over a point on the line.*

**"Each point shows the forecast in megawatts, when it was published, and how old it was at the cutoff. Every value here was published by 09:00 on the decision day."**

*Screen: point to the data-quality summary.*

**"The data-quality summary says 24 of 24 hourly targets have a usable forecast. If a value were missing or conflicting, the app would show a gap, never a zero."**

### 1:30–2:45 Accuracy view

*Screen: scroll down to the section labelled "Hindsight".*

**"This section is labelled hindsight, because it uses the actual wind generation that happened afterwards."**

*Screen: point to the chart with two lines.*

**"The solid line is the forecast. The dashed line is the actual generation. They're compared only at the same hours."**

**"A positive error means the wind was overforecast. A buyer relying on that forecast could end up short."**

*Screen: point to the metric cards.*

**"For 15 January, the average miss is about 810 megawatts. The bias is plus 349, meaning overforecast on average. The RMSE is about 970, which gives more weight to big misses."**

*Screen: scroll to the January strip. Click 18 January.*

**"This strip shows every January decision. Each column is one day's bias. Bars above the line were overforecast, bars below were underforecast."**

**"18 January was the closest day, with an average miss of about 684 megawatts."**

*Screen: click 27 January.*

**"27 January was the furthest off, with an average miss of about 5,300 megawatts. Every hour that day was overforecast."**

### 2:45–3:30 Limits

*Screen: scroll to the "About the data" section.*

**"In January overall, 27 of 31 days were overforecast. Across 744 matched hours, the bias is about plus 1,750 megawatts."**

**"These are hindsight scores. Nobody could have seen them on 1 January. The data covers the GB wind that Elexon meters, not every UK wind farm, and the actuals are the latest retrieved, not final settlement figures."**

**"The app doesn't calculate costs, purchase volumes or savings. The brief only allows these two Elexon datasets."**

---

## Part 2: Technical lead

### 3:30–4:30 Architecture

*Screen: the architecture diagram in the README.*

**"The frontend is React with Vite. The backend is FastAPI in Python, and all the analysis happens in Python. The frontend only displays what the API returns."**

**"One Docker image serves both the frontend and the API, from one origin. There's no separate frontend host to configure."**

**"It runs on Render's free web service. The free instance sleeps after 15 minutes without traffic, so the first request can take about a minute. That's why I opened the app before recording."**

### 4:30–5:15 Core rules

*Screen: open `backend/app/forecasts.py`.*

**"Each forecast target uses the latest forecast published at or before the 09:00 cutoff. The app never falls back to an older one, and never uses a later one."**

*Screen: open `backend/app/accuracy.py`.*

**"Forecasts and actuals are joined only where their timestamps match exactly. Nothing is interpolated, and a missing value is never treated as zero."**

**"The January metrics pool every matched hourly error. They're not an average of the daily figures."**

*Screen: open `docs/adr/` and show the file list.*

**"Each of these rules has a decision record. ADR 0002 covers the cutoff, ADR 0003 the matching, and ADR 0004 the January figures."**

### 5:15–6:15 Tests

*Screen: terminal, in `backend/`.*

**"I'll run the backend tests."**

*Run `pytest`. Wait for the result line, then point to it.*

**"There are 41 tests. They call the API with small hand-built datasets, not the live Elexon feed, so the results are predictable."**

**"They cover the cutoff itself, the first and last January decision dates, conflicting forecasts, missing data versus zero, and the metric calculations, checked against values worked out by hand."**

*Screen: terminal, in `frontend/`.*

**"The frontend has a lint step and a production build. Both pass."**

### 6:15–6:50 Data provenance

*Screen: open `backend/data/snapshot/metadata.json`.*

**"The metadata records the query URLs, the retrieval time, the record counts and SHA-256 hashes for each dataset. The script `fetch_snapshot.py` can retrieve the data again."**

**"The README covers how to run the app locally and in Docker."**

### 6:50–7:30 Trade-offs and next steps

*Screen: the README "Limitations" section.*

**"The data is bundled rather than fetched live. That keeps the demo reliable, but it means the app doesn't update itself."**

**"The next steps would be a configurable cutoff, a scheduled data refresh, and an error estimate that uses only information available before each decision."**

**"AI assistance is disclosed in the README. A human reviewed each plan, decision and change."**

**"Thank you."**

---

## Timing check

| Section | Time |
| --- | --- |
| Problem | 0:25 |
| Forecast view | 1:05 |
| Accuracy view | 1:15 |
| Limits | 0:45 |
| Architecture | 1:00 |
| Core rules | 0:45 |
| Tests | 1:00 |
| Data provenance | 0:35 |
| Trade-offs and close | 0:40 |
| **Total** | **about 8:30** |

If you run over, shorten the trade-offs section first, then the limits section. Keep the forecast and accuracy views, since they show the product.
