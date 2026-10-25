# Wind Procurement Pilot

A pilot for a utility's day-ahead procurement team to inspect Elexon wind generation forecasts and evaluate their accuracy.

## Language

**Actual generation**:
The wind generation reported by Elexon for a target interval, used as the observed value when evaluating a forecast.
_Avoid_: Demand, consumption

**Target interval**:
The half-hour period for which wind generation is forecast or reported.
_Avoid_: Publication time

**Publication time**:
The time Elexon records for publication of a forecast for a target interval. A target interval can have forecasts with different publication times.
_Avoid_: Target time, delivery time

**Delivery day**:
The day containing the target intervals for which the procurement team is considering purchasing electricity.
_Avoid_: Decision day

**Decision cutoff**:
The latest publication time allowed when selecting forecasts to represent the information available for a procurement decision.
_Avoid_: Latest forecast without specifying a cutoff
