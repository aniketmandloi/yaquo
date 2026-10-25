from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.snapshot import Observation

LONDON = ZoneInfo("Europe/London")
CUTOFF_TIME = time(9, 0)


def london_midnight(day: date) -> datetime:
    return datetime.combine(day, time(0, 0), LONDON).astimezone(UTC)


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


def selected_target(obs: Observation, cutoff: datetime) -> dict:
    return {
        "startTime": utc_text(obs.start),
        "status": "selected",
        "generation": obs.generation,
        "publishTime": utc_text(obs.publish),
        "ageMinutes": int((cutoff - obs.publish).total_seconds() // 60),
    }


def decision_forecast(forecasts: list[Observation], decision_date: date) -> dict:
    delivery_date = decision_date + timedelta(days=1)
    cutoff = datetime.combine(decision_date, CUTOFF_TIME, LONDON)
    day_start = london_midnight(delivery_date)
    day_end = london_midnight(delivery_date + timedelta(days=1))

    latest: dict[datetime, Observation] = {}
    for obs in forecasts:
        if day_start <= obs.start < day_end and obs.publish <= cutoff:
            current = latest.get(obs.start)
            if current is None or obs.publish > current.publish:
                latest[obs.start] = obs

    hourly = []
    start = day_start
    while start < day_end:
        hourly.append(start)
        start += timedelta(hours=1)

    targets = []
    for start in sorted(set(hourly) | set(latest)):
        obs = latest.get(start)
        if obs is None:
            targets.append(missing_target(start))
        else:
            targets.append(selected_target(obs, cutoff))

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
