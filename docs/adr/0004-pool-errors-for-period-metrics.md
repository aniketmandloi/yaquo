# 0004: Pool every matched error for the January metrics

Status: Accepted

## Context

The January figure could be an average of the 31 daily MAE values, or it could be computed from all matched errors together. The two differ whenever days contain different numbers of pairs.

## Decision

Compute the January MAE, bias and RMSE from every matched hourly error in the period. Do not average the daily metrics. Each day's metrics remain available on their own.

## Consequences

- Days with more matched pairs carry more weight. Every day currently has 24 pairs, so pooled MAE and bias equal the average of the daily values here. RMSE does not average that way in general, so the pooled rule still matters.
- Tests include an unequal-count case, so this rule is checked by the test suite.

Sources: [`docs/planning/wind-pilot-spec.md`](../planning/wind-pilot-spec.md), Accuracy; `backend/tests/test_accuracy_api.py`, `test_period_metrics_pool_every_matched_error_across_january`.
