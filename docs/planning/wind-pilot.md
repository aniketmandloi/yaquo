# Wind pilot scope

This records the design interview. Only items under Agreed are accepted; pending decisions are not implementation instructions.

## Brief requirements

Source: [problem.md](../../problem.md).

- React frontend, Python backend, Docker, deployment to Vercel or Heroku.
- Generation data exclusively from Elexon FUELHH (`fuelType: WIND`) and WINDFOR.
- Support inspection of forecasts available for day-ahead procurement and quantitative accuracy evaluation.
- A maximum of 16 hours for the assignment, including delivery work.
- Public repository with an anonymous/random name, startup and directory documentation, hosted URL, and AI assistance disclosure.
- An unlisted YouTube demo, at most five minutes each for the customer and technical lead, at most ten minutes total; required before submission.
- Submission through the specified form and incognito verification of all submitted URLs.

## Agreed

Accepted by the user in the design interview:

1. Two views: day-ahead forecasts and historical forecast accuracy.
2. Accuracy measures: MAE, mean signed error (bias), and RMSE, with plain-language explanations.
3. Decision cutoff: 09:00 Europe/London on the day before delivery, explicitly labeled a pilot assumption rather than a universal auction deadline.
4. January scope: decision dates January 1–31, 2026, for delivery January 2–February 1, 2026. Show decision and delivery dates distinctly.
5. Match actuals and forecasts only at identical target timestamps. Show coverage counts; exclude missing or conflicting records from accuracy scores rather than inventing values.
6. Bundle a reproducible Elexon historical snapshot and record retrieval time. Use the latest actuals retrieved for retrospective evaluation; retain the decision cutoff when selecting forecasts.
7. Label January accuracy measures as retrospective results, not estimates that were available earlier in January.
8. Target one Heroku Basic app serving React and Python from the Docker image. The user accepted the researched $7/month hosting cost. Account access and billing verification still need checking before deployment.

For a target time, a forecast published after the agreed cutoff cannot represent information available at that decision. Retain publication times so the selection is inspectable.

## Pending

- Full-range data feasibility profile, including coverage at the chosen cutoff.
- Acceptance of the proposed testing boundary below.
- Final user confirmation of the resulting scope before implementation.

## Proposed testing boundary

Exercise the Python API with small controlled snapshots to verify the externally visible behavior: selection at the cutoff (including equality), January decision/delivery boundaries, exact target matching, missing/conflicting records, latest retrieved actuals, and the three metric calculations. Do not rely on live Elexon calls for automated test expectations.

Verify frontend integration with static checks and a production build. Verify the packaged app with request-based checks where possible; the user starts servers and performs visual browser checks, per project instructions.

## Delivery focus

The two agreed views provide historical decision support and explain the limits of the data. No additional generation data source is allowed by the brief. Demand, prices, and customer portfolio inputs are unavailable, so the permitted data cannot establish procurement volumes or financial savings.

Before implementation, summarize the agreed scope and testing boundary for final confirmation. Then synthesize a spec and propose small end-to-end tickets, preserving time for deployment, documentation, and the mandatory video.

## Evidence and limits

- [Elexon research](../research/elexon-wind.md): historical samples exist, forecast cadence differs from actuals in the sample, full-range coverage remains unverified.
- [Deployment research](../research/deployment.md): platform options and account prerequisites; no app or paid resource has been provisioned.

The January accuracy analysis must distinguish retrospective realized errors from information available at a historical decision. A risk estimate available at a cutoff would require an evaluation window using only outcomes available by that cutoff.
