# 0007: Use only the two Elexon wind datasets

Status: Accepted

## Context

The brief says no other data sources may be used. Demand, prices and customer portfolios would make the analysis look more useful, but they are outside the brief and would not support the purchase volumes or savings they might suggest.

## Decision

Use WINDFOR and FUELHH with `fuelType` `WIND` only. Describe the data as Elexon-reported GB wind generation in MW. Do not present volumes, costs or savings.

## Consequences

- Each claim the app makes can be traced to one of two datasets.
- The app cannot show what the forecast error cost the buyer. That analysis would need data outside the brief.

Sources: [`docs/planning/wind-pilot-spec.md`](../planning/wind-pilot-spec.md), Out of Scope; `problem.md`, Scope limitation.
