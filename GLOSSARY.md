# Wind Procurement Pilot

A pilot for a utility's day-ahead procurement team to inspect Elexon wind generation forecasts and evaluate their accuracy.

## Language

**Actual generation**:
The wind generation reported by Elexon for a target interval, used as the observed value when evaluating a forecast.
_Avoid_: Demand, consumption

**Target interval**:
The period identified by a generation record's target start time. Actuals and forecasts can have different target cadences.
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

**Forecast error**:
Forecast generation minus actual generation at a matched target time, in MW. A positive value means wind generation was overforecast.
_Avoid_: Absolute error when referring to a signed difference

**Mean absolute error (MAE)**:
The mean magnitude of forecast errors across matched target times, in MW.
_Avoid_: Bias

**Mean signed error (bias)**:
The mean forecast error across matched target times, in MW, indicating a tendency to overforecast or underforecast wind generation.
_Avoid_: Mean absolute error

**Root mean square error (RMSE)**:
The square root of the mean squared forecast error across matched target times, in MW; larger misses contribute more strongly.
_Avoid_: Typical absolute miss
