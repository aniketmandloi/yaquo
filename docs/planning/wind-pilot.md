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

For a target time, a forecast published after the agreed cutoff cannot represent information available at that decision. Retain publication times so the selection is inspectable.

## Pending

- Exact timestamp matching and treatment of gaps, duplicates, and conflicting records.
- Reproducible historical snapshot versus runtime Elexon requests; actual-revision policy and retrospective scoring interpretation.
- Hosting platform and cost acceptance.
- Final user confirmation of the resulting scope before implementation.

## Evidence and limits

- [Elexon research](../research/elexon-wind.md): historical samples exist, forecast cadence differs from actuals in the sample, full-range coverage remains unverified.
- [Deployment research](../research/deployment.md): platform options and account prerequisites; no app or paid resource has been provisioned.

The January accuracy analysis must distinguish retrospective realized errors from information available at a historical decision. A risk estimate available at a cutoff would require an evaluation window using only outcomes available by that cutoff.
