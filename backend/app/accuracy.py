import math
from datetime import date, datetime, timedelta

from app.forecasts import (
    FIRST_DECISION_DATE,
    LAST_DECISION_DATE,
    classify,
    decision_forecast,
    london_midnight,
    target_starts,
    utc_text,
)
from app.snapshot import Observation

ActualSelection = dict[datetime, tuple[datetime, list]]
STATUSES = ("selected", "missing", "conflicting", "invalid")


def status_counts(statuses: list[str]) -> dict:
    return {status: statuses.count(status) for status in STATUSES}


def select_actual(start: datetime, actuals: ActualSelection) -> tuple:
    if start not in actuals:
        return "missing", None, None
    publish, generations = actuals[start]
    status, value = classify(generations)
    return status, value, utc_text(publish)


def half_hour_timeline(delivery_date: date, actuals: ActualSelection) -> dict:
    day_start = london_midnight(delivery_date)
    day_end = london_midnight(delivery_date + timedelta(days=1))
    grid = target_starts(day_start, day_end, timedelta(minutes=30))
    starts = set(grid) | {s for s in actuals if day_start <= s < day_end}
    statuses = [select_actual(start, actuals)[0] for start in starts]
    return {"targets": len(grid), **status_counts(statuses)}


def metrics(errors: list) -> dict:
    count = len(errors)
    if count == 0:
        return {"matchedPairs": 0, "mae": None, "bias": None, "rmse": None}
    return {
        "matchedPairs": count,
        "mae": sum(abs(e) for e in errors) / count,
        "bias": sum(errors) / count,
        "rmse": math.sqrt(sum(e * e for e in errors) / count),
    }


def pair(target: dict, actuals: ActualSelection) -> dict:
    start = datetime.fromisoformat(target["startTime"])
    actual_status, actual_value, actual_publish = select_actual(start, actuals)
    matched = target["status"] == "selected" and actual_status == "selected"
    return {
        "startTime": target["startTime"],
        "forecast": target["generation"],
        "forecastStatus": target["status"],
        "forecastPublishTime": target["publishTime"],
        "actual": actual_value,
        "actualStatus": actual_status,
        "actualPublishTime": actual_publish,
        "error": target["generation"] - actual_value if matched else None,
    }


def decision_accuracy(
    forecasts: list[Observation], actuals: ActualSelection, decision_date: date
) -> dict:
    view = decision_forecast(forecasts, decision_date)
    pairs = [pair(target, actuals) for target in view["targets"]]
    errors = [p["error"] for p in pairs if p["error"] is not None]
    return {
        "decisionDate": view["decisionDate"],
        "deliveryDate": view["deliveryDate"],
        "cutoff": view["cutoff"],
        "timezone": view["timezone"],
        "unit": view["unit"],
        "day": {
            "pairs": pairs,
            "metrics": metrics(errors),
            "coverage": {
                "hourlyForecastTargets": view["quality"]["expectedHourlyTargets"],
                "forecast": status_counts([p["forecastStatus"] for p in pairs]),
                "actualAtHourlyTargets": status_counts(
                    [p["actualStatus"] for p in pairs]
                ),
                "matchedPairs": len(errors),
                "halfHourActualTimeline": half_hour_timeline(
                    date.fromisoformat(view["deliveryDate"]), actuals
                ),
            },
        },
    }


def summed(items: list):
    if isinstance(items[0], dict):
        return {key: summed([item[key] for item in items]) for key in items[0]}
    return sum(items)


def period_accuracy(forecasts: list[Observation], actuals: ActualSelection) -> dict:
    days = []
    decision_date = FIRST_DECISION_DATE
    while decision_date <= LAST_DECISION_DATE:
        days.append(decision_accuracy(forecasts, actuals, decision_date)["day"])
        decision_date += timedelta(days=1)
    # Pooled errors, so days with more matched pairs carry more weight.
    errors = [
        p["error"] for day in days for p in day["pairs"] if p["error"] is not None
    ]
    return {
        "firstDecisionDate": FIRST_DECISION_DATE.isoformat(),
        "lastDecisionDate": LAST_DECISION_DATE.isoformat(),
        "metrics": metrics(errors),
        "coverage": summed([day["coverage"] for day in days]),
    }
