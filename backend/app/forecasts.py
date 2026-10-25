import math
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.snapshot import Observation

LONDON = ZoneInfo("Europe/London")
CUTOFF_TIME = time(9, 0)
FIRST_DECISION_DATE = date(2026, 1, 1)
LAST_DECISION_DATE = date(2026, 1, 31)


def london_midnight(day: date) -> datetime:
    return datetime.combine(day, time(0, 0), LONDON).astimezone(UTC)


def target_starts(day_start: datetime, day_end: datetime, step: timedelta) -> list:
    starts = []
    start = day_start
    while start < day_end:
        starts.append(start)
        start += step
    return starts


def is_valid_generation(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def same_value(a: object, b: object) -> bool:
    # Python treats True == 1, which would let a duplicate hide an invalid value.
    return isinstance(a, bool) == isinstance(b, bool) and a == b


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


def classify(generations: list) -> tuple[str, object]:
    # An unusable latest key is reported, never replaced by an older value.
    if len(generations) > 1:
        return "conflicting", None
    if not is_valid_generation(generations[0]):
        return "invalid", None
    return "selected", generations[0]


def latest_by_target(
    observations: list[Observation], keep
) -> dict[datetime, tuple[datetime, list]]:
    latest: dict[datetime, datetime] = {}
    values: dict[tuple[datetime, datetime], list] = {}
    for obs in observations:
        if keep(obs):
            latest[obs.start] = max(latest.get(obs.start, obs.publish), obs.publish)
            key_values = values.setdefault((obs.start, obs.publish), [])
            if not any(same_value(obs.generation, v) for v in key_values):
                key_values.append(obs.generation)
    return {
        start: (publish, values[start, publish]) for start, publish in latest.items()
    }


def selected_target(
    start: datetime, publish: datetime, generations: list, cutoff: datetime
) -> dict:
    status, generation = classify(generations)
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

    latest = latest_by_target(
        forecasts,
        lambda obs: day_start <= obs.start < day_end and obs.publish <= cutoff,
    )
    hourly = target_starts(day_start, day_end, timedelta(hours=1))

    targets = []
    for start in sorted(set(hourly) | set(latest)):
        if start not in latest:
            targets.append(missing_target(start))
        else:
            targets.append(selected_target(start, *latest[start], cutoff))

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
