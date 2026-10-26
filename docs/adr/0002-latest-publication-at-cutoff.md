# 0002: Select the latest forecast published by the cutoff, per target, with no fallback

Status: Accepted

## Context

A forecast downloaded after delivery contains publications the buyer could not have seen. Scoring against those would overstate how well the decision could have been informed. The cutoff of 09:00 London time is a pilot assumption agreed with the user, not an exchange rule.

## Decision

- The cutoff is 09:00 Europe/London on the decision date. Equality counts as available.
- For each hourly target on the next calendar day, select the greatest `publishTime` at or before the cutoff. Each target is decided independently.
- Keep the selected publication time and the age at the cutoff, so the choice can be inspected.
- Select the latest eligible publication first, then check it for conflicts. If it conflicts or is invalid, exclude that target. Do not fall back to an older forecast.

## Consequences

- A later publication never improves the decision view, even if it would score better.
- Some targets may show as excluded instead of having a value. The coverage counts report how many.
- Changing the cutoff changes every figure, so it needs a new decision record rather than a quiet configuration change.

Sources: [`docs/planning/wind-pilot-spec.md`](../planning/wind-pilot-spec.md), Time and forecast eligibility; [`docs/research/elexon-wind.md`](../research/elexon-wind.md), Latest at a decision time differs from latest retrospectively.
