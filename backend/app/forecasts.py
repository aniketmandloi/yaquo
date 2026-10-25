from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.snapshot import Observation

LONDON = ZoneInfo("Europe/London")
CUTOFF_TIME = time(9, 0)


def london_midnight(day: date) -> datetime:
    return datetime.combine(day, time(0, 0), LONDON).astimezone(UTC)


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

    targets = [
        {
            "startTime": start.astimezone(UTC).isoformat(),
            "status": "selected",
            "generation": obs.generation,
            "publishTime": obs.publish.astimezone(UTC).isoformat(),
            "ageMinutes": int((cutoff - obs.publish).total_seconds() // 60),
        }
        for start, obs in sorted(latest.items())
    ]

    return {
        "decisionDate": decision_date.isoformat(),
        "deliveryDate": delivery_date.isoformat(),
        "cutoff": cutoff.isoformat(),
        "timezone": "Europe/London",
        "unit": "MW",
        "targets": targets,
    }
