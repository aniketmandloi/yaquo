# 0001: Bundle a historical Elexon snapshot instead of fetching live

Status: Accepted

## Context

The evaluator must be able to open the app without depending on Elexon being available, and the analysis must be reproducible. The brief limits the work to January 2026.

## Decision

Store the WINDFOR and FUELHH WIND responses for the agreed range in `backend/data/snapshot/`, together with `metadata.json` (query URLs, bounds, retrieval time, record counts, SHA-256 hashes, and the one transformation applied). The app reads only these files. `backend/scripts/fetch_snapshot.py` can retrieve them again.

## Consequences

- The demo works offline and gives the same numbers on every run.
- Results describe the data retrieved on the recorded date. The provider may return different data later, so a new retrieval needs review before it is committed.
- There is no refresh schedule and no live forecasting, which the spec places out of scope.

Source: [`docs/planning/wind-pilot-spec.md`](../planning/wind-pilot-spec.md), Snapshot and data quality.
