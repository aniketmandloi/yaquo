# 0003: Compare forecasts and actuals only at identical target times

Status: Accepted

## Context

WINDFOR forecasts are hourly and FUELHH actuals are half-hourly. Matching them needs an assumption about what an hourly forecast means, and the research found no documented answer.

## Decision

- Join a forecast and an actual only when their `startTime` values are exactly equal.
- Do not interpolate, forward-fill, or average half-hour actuals into an hourly figure.
- Never treat a missing value as zero.
- Report forecast coverage and half-hour actual coverage separately.

## Consequences

- Each delivery day has 24 scored pairs out of 48 actual half-hours. The other 24 are visible in the coverage counts but are not scored. This is correct for hourly forecasts, but it is not the same as 100% coverage of actuals.
- The method is conservative and easy to explain. A different aggregation would need its own decision, and the spec puts it out of scope.

Sources: [`docs/planning/wind-pilot-spec.md`](../planning/wind-pilot-spec.md), Accuracy and Out of Scope; [`docs/research/elexon-wind.md`](../research/elexon-wind.md), Forecast cadence does not match actuals.
