import math
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.snapshot import Observation

LONDON = ZoneInfo("Europe/London")
CUTOFF_TIME = time(9, 0)


def london_midnight(day: date) -> datetime:
    return datetime.combine(day, time(0, 0), LONDON).astimezone(UTC)


def is_valid_generation(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def utc_text(instant: datetime) -> str:
    return instant.astimezone(UTC).isoformat()


def missing_target(start: datetime) -> dict:
    return {
        "startTime": utc_text(start),
        "status": "missing",
        "generation": None,
        "publishTime": None,
        "ageMinutes": None,
    }


def selected_target(
    start: datetime, publish: datetime, generations: list, cutoff: datetime
) -> dict:
    # An unusable latest key is reported, never replaced by an older forecast.
    if len(generations) > 1:
        status, generation = "conflicting", None
    elif not is_valid_generation(generations[0]):
        status, generation = "invalid", None
    else:
        status, generation = "selected", generations[0]
    return {
        "startTime": utc_text(start),
        "status": status,
        "generation": generation,
        "publishTime": utc_text(publish),
        "ageMinutes": int((cutoff - publish).total_seconds() // 60),
    }


def decision_forecast(forecasts: list[Observation], decision_date: date) -> dict:
    delivery_date = decision_date + timedelta(days=1)
    cutoff = datetime.combine(decision_date, CUTOFF_TIME, LONDON)
    day_start = london_midnight(delivery_date)
    day_end = london_midnight(delivery_date + timedelta(days=1))

    latest: dict[datetime, datetime] = {}
    values: dict[tuple[datetime, datetime], list] = {}
    for obs in forecasts:
        if day_start <= obs.start < day_end and obs.publish <= cutoff:
            latest[obs.start] = max(latest.get(obs.start, obs.publish), obs.publish)
            key_values = values.setdefault((obs.start, obs.publish), [])
            if obs.generation not in key_values:
                key_values.append(obs.generation)

    hourly = []
    start = day_start
    while start < day_end:
        hourly.append(start)
        start += timedelta(hours=1)

    targets = []
    for start in sorted(set(hourly) | set(latest)):
        publish = latest.get(start)
        if publish is None:
            targets.append(missing_target(start))
        else:
            targets.append(
                selected_target(start, publish, values[start, publish], cutoff)
            )

    statuses = [target["status"] for target in targets]
    quality = {
        "expectedHourlyTargets": len(hourly),
        "selected": statuses.count("selected"),
        "missing": statuses.count("missing"),
        "conflicting": statuses.count("conflicting"),
        "invalid": statuses.count("invalid"),
    }

    return {
        "decisionDate": decision_date.isoformat(),
        "deliveryDate": delivery_date.isoformat(),
        "cutoff": cutoff.isoformat(),
        "timezone": "Europe/London",
        "unit": "MW",
        "targets": targets,
        "quality": quality,
    }
