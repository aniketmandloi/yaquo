# Elexon wind procurement pilot

## Problem Statement

A UK utility's day-ahead procurement team needs to inspect wind generation forecasts available before a purchase decision and quantify how those forecasts performed. A forecast retrieved after delivery may contain later publications that were unavailable to the buyer. Comparing such a forecast with actuals would misrepresent decision-time performance.

The assignment limits generation data to Elexon WINDFOR and FUELHH WIND and limits the work to 16 hours, including deployment and delivery materials.

## Solution

Provide a React application with two views backed by Python: a day-ahead forecast view and a retrospective accuracy view. For each January 2026 decision date, show the forecast available by 09:00 Europe/London for the following delivery day. Show MAE, mean signed error, and RMSE against retrieved actuals, with exact target matching, coverage counts, and plain-language explanations.

Bundle a reproducible historical Elexon snapshot so the deployed demonstration does not depend on live API availability. Serve the frontend and backend from one Docker image on Heroku Basic, using the hosting budget accepted by the user.

## User Stories

1. As a procurement analyst, I want to select a January decision date, so that I can inspect the information available for that purchase decision.
2. As a procurement analyst, I want the corresponding delivery date shown separately, so that I do not confuse decision and delivery dates.
3. As a procurement analyst, I want the 09:00 London pilot cutoff shown, so that I understand the forecast selection assumption.
4. As a procurement analyst, I want the latest eligible forecast for each next-day target, so that later publications cannot affect the historical decision view.
5. As a procurement analyst, I want a daily wind forecast chart with values in MW, so that I can inspect the expected generation profile.
6. As a procurement analyst, I want publication times and forecast age at the cutoff, so that I can assess freshness.
7. As a procurement analyst, I want missing or conflicting forecasts identified, so that I do not mistake unavailable information for zero generation.
8. As a procurement analyst, I want to compare eligible forecasts with actual generation, so that I can inspect realized misses.
9. As a procurement analyst, I want MAE in MW, so that I can quantify the average magnitude of misses.
10. As a procurement analyst, I want mean signed error in MW, so that I can see whether wind was generally overforecast or underforecast.
11. As a procurement analyst, I want RMSE in MW, so that larger misses receive greater weight.
12. As a procurement analyst, I want explanations of each metric and the error sign, so that I can interpret the figures correctly.
13. As a procurement analyst, I want daily and whole-January accuracy summaries, so that I can compare an individual decision with the complete pilot period.
14. As a procurement analyst, I want matched counts and the differing forecast/actual cadences explained, so that I understand which observations the scores represent.
15. As a procurement analyst, I want absent data distinguished from valid zero error, so that I can assess incomplete results honestly.
16. As a procurement analyst, I want retrospective scores clearly labeled, so that I do not treat later January outcomes as information available earlier in the month.
17. As a procurement analyst, I want dataset coverage and retrieval bounds explained, so that I do not mistake reported GB wind for all UK generation or final settlement data.
18. As an evaluator, I want the public app to work without credentials, so that I can review the pilot directly.
19. As a technical lead, I want to reproduce the snapshot and inspect its provenance, so that I can audit the analysis.
20. As a technical lead, I want automated tests at the Python API boundary, so that I can trust forecast selection, alignment, and calculations.
21. As a technical lead, I want documented local and Docker startup commands, so that I can reproduce the application.
22. As a technical lead, I want a concise architecture explanation and explicit limitations, so that I can assess implementation choices within the time limit.
23. As an evaluator, I want the README to describe directories, startup, AI assistance, and the hosted app, so that I can navigate the submission.
24. As an evaluator, I want the required customer and technical video sections, so that I can assess the product and its implementation within ten minutes.
25. As an applicant, I want all submission links checked in incognito and submitted through the required form, so that the evaluator can access every deliverable.

## Implementation Decisions

### Time and forecast eligibility

- Decision dates are January 1–31, 2026 inclusive; delivery dates are January 2–February 1 inclusive. Reject unsupported decision dates explicitly rather than returning misleading empty results.
- Define each cutoff as 09:00 Europe/London on its decision date. This is an agreed pilot assumption, not a universal auction deadline.
- Parse provider timestamps as timezone-aware instants. Use exact instants for joins and show the timezone in user-facing dates and times.
- Restrict targets to the following calendar delivery day. For each target independently, select the greatest publication time less than or equal to the cutoff.
- Retain selected publication time and age relative to the cutoff. Never select a later publication because it produces a better retrospective score.
- Select the latest eligible key before checking conflicts. Exclude a conflicting selected key; do not silently fall back to an older forecast.

### Snapshot and data quality

- Generation observations come exclusively from WINDFOR and FUELHH records with fuel type WIND. Do not add demand, prices, or other generation sources.
- Include a reproducible retrieval procedure and snapshot metadata recording source URLs/query bounds, retrieval time, content hashes, and transformations needed to obtain the analysis data.
- Preserve target times, publication times, and generation values needed to audit the as-of selection. The running app reads the bundled snapshot rather than fetching Elexon for each page request.
- For actuals, select the greatest publication time retrieved for each target. Describe these as latest actuals within the documented retrieval window, without claiming final reconciliation or absence of later corrections.
- Deduplicate identical observations. Exclude conflicting selected observations and invalid generation values, and expose their counts. Missing observations remain missing and are never replaced with zero.
- Join forecasts and actuals only at identical target instants. Do not interpolate, forward-fill, or average half-hour actuals into an hourly comparator.
- Research found 24 hourly forecast targets and 48 half-hour actual targets per delivery day. All 744 hourly targets matched across the agreed range. Treat these as verified snapshot observations, not a permanent provider guarantee.
- Show matched/eligible forecast counts and the half-hour actual timeline count separately. The 744 unmatched half-hour targets reflect forecast cadence, not 744 unexpected provider failures.
- Label data as Elexon reported GB wind generation, with the source's operational-metering coverage limitation.

### Accuracy

- Define signed error as forecast minus actual, in MW. Positive error means wind overforecast; treating that wind as available supply can leave a purchaser short.
- Calculate MAE as mean absolute error, bias as mean signed error, and RMSE as square root of mean squared error, using the same valid matched pairs.
- Daily scores and the January aggregate use the agreed per-day cutoffs. Aggregate the underlying matched errors across the period; do not average daily metric values.
- Return unavailable metrics when there are no valid pairs, with explanatory counts. A valid zero score must remain distinguishable from no data.
- Label scores as retrospective realized performance. Do not present them as a prior-only risk estimate available at an earlier January cutoff or convert them into financial savings or procurement volumes.

### Application interfaces

- The forecast API accepts a decision date and exposes its delivery day, cutoff, eligible target values, publication metadata, and data-quality counts.
- The accuracy API exposes daily and whole-period matched observations, metric summaries, and coverage information using the same selection rules as the forecast view.
- Keep analysis behind the Python API. The React views display returned results and handle loading, unavailable data, and request errors clearly.
- The forecast view is a historical as-of view. Actuals belong in the retrospective accuracy comparison, with clear view labels to prevent hindsight confusion.
- Use readable chart labels, units, and metric explanations. Chart interaction must expose individual target values and selected publication information.

### Packaging and delivery

- Build React and serve its production assets with the Python backend from one Docker image. Support the hosting-assigned port and frontend navigation on refresh.
- Target one Heroku Basic app. Account/billing access and actual deployment compatibility must be verified; the user accepted the researched $7/month cost.
- Use a public repository with an anonymous/random name, as required by the assignment. Verify whether the existing repository satisfies this before creating or renaming anything.
- The README must explain directories, local/Docker startup, dataset provenance and limitations, the hosted URL, and AI assistance.
- Prepare a customer demonstration and technical walkthrough, each at most five minutes and at most ten minutes total. The unlisted YouTube video is a submission prerequisite.
- Verify repository, app, and video access in incognito and complete the required submission form. Do not claim delivery complete while recording/upload, access checks, or form submission remain outstanding.
- The user starts development servers and performs visual browser checks, per project instructions. Provide exact visual checks after automated verification.
- Preserve unrelated work and commit each verified logical change separately.

## Testing Decisions

- The user accepted testing through the Python API using small controlled snapshots. Test observable results rather than internal implementation details.
- Cover cutoff equality, a newer publication after cutoff, independent selection per target, both January boundaries, and invalid decision dates.
- Cover exact timestamp matching, absent records, legitimate zero generation, invalid values, identical duplicates, conflicting latest keys without fallback, and latest retrieved actual selection.
- Verify MAE, bias, and RMSE against manually calculated examples, including zero pairs, valid zero error, and unequal sample counts between days.
- Ensure the forecast and accuracy interfaces use the same eligible forecast records and expose consistent coverage counts.
- Separate snapshot provenance/coverage validation from deterministic tests. Automated test expectations must not depend on a live provider response.
- Run applicable formatting/static checks, frontend production build, targeted tests during development, and the full suite at completion. Check Docker packaging where the available runtime permits it.
- There is no existing application or test suite in this repository; establish only the minimal tooling needed for these behaviors. Adding dependencies requires approval under the project instructions.
- User visual checks cover date selection, forecast and accuracy views, chart inspection, explanations, errors, responsive readability, and public access.

## Out of Scope

- Additional generation sources, customer portfolios, demand forecasts, prices, trade execution, purchase-volume calculations, or financial savings claims.
- Live forecasting beyond the agreed historical period, scheduled refresh infrastructure, and prediction models.
- Interpolation between hourly forecasts, alternative forecast/actual aggregation assumptions, and exchange-specific auction certification.
- Uncertainty bands or risk estimates represented as available before their underlying actual outcomes.
- Authentication or account-management workflows for this public evaluation pilot.

## Further Notes

The user confirmed the full product scope and API testing boundary before this spec was synthesized. Full-range research supports the agreed dates with 744 matched pairs, but archive completeness, final actual reconciliation, and forecast interval semantics beyond target timestamps remain unverified.

Reserve meaningful time within the 16-hour limit for deployment, README, the mandatory video, and submission. Do not spend the entire budget on application code.

Supporting project documents: the agreed pilot scope, the domain glossary, and the Elexon and deployment research notes. Issue tickets should be self-contained and declare their blocking relationships. Publish tickets only after the user approves their proposed breakdown.
