# Architecture decision records

Each record states one decision, why it was made, and what follows from it. Records are numbered in the order they were agreed and are not edited once accepted. A later change gets a new record that supersedes the old one.

| Record | Decision | Status |
| --- | --- | --- |
| [0001](0001-bundle-historical-snapshot.md) | Bundle a historical Elexon snapshot instead of fetching live | Accepted |
| [0002](0002-latest-publication-at-cutoff.md) | Select the latest forecast published by the cutoff, with no fallback | Accepted |
| [0003](0003-match-at-identical-target-times.md) | Compare forecasts and actuals only at identical target times | Accepted |
| [0004](0004-pool-errors-for-period-metrics.md) | Pool every matched error for January metrics | Accepted |
| [0005](0005-one-origin-python-serves-frontend.md) | Serve the React build and API from one Python process | Accepted |
| [0006](0006-heroku-basic-container.md) | Deploy to one Heroku Basic dyno | Accepted, deployment pending |
| [0007](0007-scope-wind-only.md) | Use only the two Elexon wind datasets | Accepted |
