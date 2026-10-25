# Wind pilot tickets

The user approved this three-ticket breakdown and its blocking edges. The tickets are published with the `ready-for-agent` label as sub-issues of the specification, with native GitHub blocking dependencies.

Parent specification: [GitHub issue #1](https://github.com/aniketmandloi/yaquo/issues/1).

| Slice | Published ticket | Blocked by |
| --- | --- | --- |
| Forecast view | [#2](https://github.com/aniketmandloi/yaquo/issues/2) | None |
| Accuracy view | [#3](https://github.com/aniketmandloi/yaquo/issues/3) | #2 |
| Public delivery | [#4](https://github.com/aniketmandloi/yaquo/issues/4) | #3 |

## Budget

Keep the whole assignment within 16 hours, including research, planning, verification, deployment, and submission preparation. Suggested allocation: up to 2 hours for research/planning already performed, 4 hours for ticket 1, 4 hours for ticket 2, 4 hours for ticket 3 (including at least 2 hours for video and submission), and 2 hours of contingency. These are caps to guide scope, not claims about elapsed time; deduct actual time already spent before implementation. Prefer the simplest complete version of the agreed scope if time becomes tight.

## 1. Inspect the forecasts available for each January procurement decision

**Blocked by:** None.

**What it delivers:** A buyer selects any January 1–31 decision date and sees the next delivery day's wind forecast as available at 09:00 London time, with the publication times and data provenance needed to trust the view. This is the first complete React-to-Python-to-data path.

### Acceptance criteria

- [ ] Bundle a reproducible snapshot sourced exclusively from Elexon WINDFOR and FUELHH WIND, with query bounds, retrieval time, and integrity information; provide a documented retrieval procedure.
- [ ] Support all January decision dates, including January 1 for January 2 delivery and January 31 for February 1 delivery; show decision date, delivery date, cutoff, timezone, and MW units clearly.
- [ ] Select the latest forecast publication no later than the cutoff independently for each target timestamp; include equality and never use later publications.
- [ ] Display the selected next-day forecasts in a usable chart with inspectable values, publication time, and forecast age; identify the fixed cutoff as a pilot assumption.
- [ ] Surface missing or conflicting selected records without inventing values or silently substituting an older forecast. Handle unavailable or invalid dates with clear responses and UI states.
- [ ] Explain that the data represents Elexon reported GB wind coverage and that hourly forecast targets differ from half-hourly actuals.
- [ ] Verify date boundaries, cutoff selection, and missing/conflicting forecast behavior through the Python API with controlled snapshots; run frontend static checks and production build.

## 2. Evaluate the selected forecasts against actual generation

**Blocked by:** Ticket 1, which establishes the snapshot and decision-cutoff selection behavior reused by scoring.

**What it delivers:** A buyer opens the historical accuracy view, compares forecast and actual generation for a selected day, and inspects daily and whole-period MAE, bias, and RMSE with honest coverage counts.

### Acceptance criteria

- [ ] Reuse the same cutoff-selected forecasts as the forecast view; compare only identical target timestamps against the latest actuals retrieved within the documented snapshot bounds.
- [ ] Show forecast and actual generation together for a selected delivery day, with values and signed errors available for inspection.
- [ ] Present MAE, mean signed error, and RMSE in MW for a selected day and all January decisions, with concise explanations; positive bias means wind was overforecast.
- [ ] Calculate period metrics from every matched error, rather than averaging daily metrics; include an unequal-daily-count test case.
- [ ] Show eligible hourly forecast targets, matched pairs, missing records, and conflicting selected records. Distinguish matching the available hourly forecasts from coverage of the half-hour actual timeline.
- [ ] Deduplicate identical records; exclude invalid or conflicting selected records from scores without treating missing generation as zero, interpolating, or falling back to older conflicting publications.
- [ ] Represent no valid matches as insufficient data rather than a zero score.
- [ ] Label scores as retrospective evaluation against the retrieved actuals, without implying final settlement truth, early-January knowledge, procurement volumes, financial savings, or a forward risk model.
- [ ] Verify exact matching, actual revision selection, conflicts, metric calculations, and insufficient-data behavior through the Python API; run frontend static checks and production build.

## 3. Deliver the pilot as a public, reviewable submission

**Blocked by:** Ticket 2, so the packaged and presented application includes both required customer capabilities.

**What it delivers:** The evaluator can open the complete deployed pilot, inspect its public source and startup instructions, and watch the required customer and technical walkthrough before assessing the submission.

### Acceptance criteria

- [ ] Build one Docker image serving the React frontend and Python API, including the reproducible snapshot, and configure deployment to the agreed Heroku Basic app.
- [ ] Verify production build, automated checks, packaged HTTP behavior where possible, and review the implementation against the spec and repository standards. The user starts servers and performs the visual checks required by project instructions.
- [ ] Deploy the complete application using verified account access and billing setup; record the working public URL and any remaining operational limitations. Do not claim deployment succeeded before checking it.
- [ ] Provide a public GitHub repository with an anonymous/random name, preserving the existing working repository unless explicitly instructed otherwise.
- [ ] Provide README coverage of directories, startup and Docker commands, data retrieval/provenance, cutoff and metric methodology, limitations, deployed URL, and explicit AI assistance disclosure.
- [ ] Prepare a customer walkthrough and technical walkthrough that together cover the product outcome, analysis, architecture, code, and development practices.
- [ ] Complete an unlisted YouTube video with customer and technical sections each at most five minutes and total duration at most ten minutes; capture the working video URL before submission.
- [ ] Have the user verify the application, repository, and video URLs in incognito mode, including core chart navigation and readable values.
- [ ] Submit the required details through the “Full Stack SWE challenge submission v4” form only after the mandatory video and working URLs exist; record confirmation rather than assuming submission.

The last delivery steps may require the user's authenticated accounts, recording, browser checks, or form access. Prepare all supporting material agents can produce, then request only the human actions that remain. Keep this ticket open until its actual completion gates are satisfied.

## Approval

The user approved the three-ticket granularity and dependency order and instructed the agent to publish them. Ticket #2 is the first unblocked implementation task. Ticket #4 remains incomplete until deployment, video, access checks, and submission are actually complete.
