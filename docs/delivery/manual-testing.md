# Manual test checklist

Use this to check the app by hand, locally or on the deployed URL. Each check says what to do and what you should see. The automated tests cover the same rules at the API level.

## A. Run it locally

1. **Start the backend.** In a terminal:
   ```sh
   cd backend
   conda activate yaquo
   uvicorn app.server:app --port 8000
   ```
   It should print `Application startup complete`.

2. **Start the frontend.** In a second terminal:
   ```sh
   cd frontend
   npm run dev
   ```
   Open the address it prints (usually http://localhost:5173).

   Alternatively, build with `npm run build` and open http://localhost:8000 with only the backend running.

## B. Check the API directly

Open each link in a browser tab. Expected results are in the right-hand column.

| # | Request | Expected |
| --- | --- | --- |
| 1 | `/api/snapshot` | JSON with `retrievedAt` and two datasets: `WINDFOR` and `FUELHH`, each with a `storedSha256`. |
| 2 | `/api/forecasts?decision_date=2026-01-15` | `deliveryDate` is `2026-01-16`, `cutoff` is `2026-01-15T09:00:00+00:00`, `unit` is `MW`, and there are 24 `targets`. Each has `publishTime` `2026-01-15T07:30:00+00:00`. |
| 3 | `/api/forecasts?decision_date=2026-02-01` | HTTP **422**, with a message that the decision date must be from 2026-01-01 to 2026-01-31. |
| 4 | `/api/accuracy?decision_date=2026-01-15` | `day.metrics`: `matchedPairs` 24, `mae` about 810, `bias` about 349, `rmse` about 970. `period.metrics.matchedPairs` is 744. |
| 5 | `/api/accuracy?decision_date=2026-01-18` | `day.metrics.bias` is about −684 (underforecast). |
| 6 | `/api/accuracy?decision_date=2026-01-27` | `day.metrics.mae` is about 5,329, with a positive bias. |
| 7 | `/api/accuracy` with no date | HTTP **422** (a required parameter is missing). |
| 8 | `/api/nothing-here` | HTTP **404**, not the web page. |
| 9 | `/accuracy` (a page path, refreshed directly) | The web app loads, not an error. This shows the refresh fallback works. |

## C. Check the forecast view (screen)

1. The page title is **Wind Procurement Pilot**, and the top bar has a decision date.
2. The top bar opens on **1 January 2026**. ‹ and › step through dates. ‹ is disabled on 1 January and › is disabled on 31 January.
3. The "Known at the 09:00 cutoff" label is shown above the forecast section.
4. The line chart shows about 24 points. Axes are labelled "Target time (London)" and "MW".
5. Hover over a point. The tooltip shows the time, the MW value, and the publication time and age before the cutoff.
6. The data-quality section reads "24 of 24 hourly targets have a usable forecast" with no missing or conflicting counts.
7. Open "All target values". A table lists each hour, its value, publication time and age.

## D. Check the accuracy view (screen)

1. The section is labelled **Hindsight**, with a dashed border and a tinted background.
2. The **January bias strip** shows 31 columns. Most bars are above the line (orange, overforecast). Hover a column to read its bias.
3. Click 18 January in the strip. The date bar, both views and the strip highlight update to 18 January.
4. The chart has two lines: forecast (teal) and actual (dark, dashed). Hover to see the forecast, actual and signed error for that hour.
5. The metric cards show MAE, bias and RMSE for the day, with January below each. Bias shows "overforecast" or "underforecast" beside its value.
6. The coverage section shows "24 of 24 hourly forecast targets matched" for the day. The half-hour actual timeline shows 48 targets.
7. Click through several dates quickly. The previous results dim while the next one loads, and the page does not jump.

## E. Check errors and edge cases

1. Stop the backend and refresh the page. Each section should show a readable error message, not a blank page.
2. Restart the backend. Reload the page, and the views should load again.

## F. Check the deployed app (incognito window)

Use a private/incognito window so cached data is not used.

1. Open the Heroku URL. The app loads without signing in.
2. Repeat sections B (replace `localhost:8000` with the Heroku host) and C and D.
3. Refresh a deep link such as `/accuracy`. The app should load, not an error page.
4. Check on a phone or a narrow window. The date bar and metric cards should fit, and the strip stays readable (its labels shrink but stay visible).
5. Tab through the page with the keyboard. The focus outline should be visible on the date buttons, the select, and the strip columns.
6. Turn on dark mode in your system settings. Text should stay readable and the bias colours should still be distinguishable.

## Record the results

Note the date and the URL you tested, then mark each section pass or fail. Report any failure with the section number and what you saw.
