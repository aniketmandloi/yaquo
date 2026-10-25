import math
from datetime import date, datetime

from app.forecasts import classify, decision_forecast, utc_text
from app.snapshot import Observation

ActualSelection = dict[datetime, tuple[datetime, list]]


def metrics(errors: list) -> dict:
    count = len(errors)
    return {
        "matchedPairs": count,
        "mae": sum(abs(e) for e in errors) / count,
        "bias": sum(errors) / count,
        "rmse": math.sqrt(sum(e * e for e in errors) / count),
    }


def pair(target: dict, actuals: ActualSelection) -> dict:
    start = datetime.fromisoformat(target["startTime"])
    if start in actuals:
        publish, generations = actuals[start]
        actual_status, actual_value = classify(generations)
        actual_publish = utc_text(publish)
    else:
        actual_status, actual_value, actual_publish = "missing", None, None
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
        "day": {"pairs": pairs, "metrics": metrics(errors)},
    }
