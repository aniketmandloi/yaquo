from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

LONDON = ZoneInfo("Europe/London")
CUTOFF_TIME = time(9, 0)


def decision_forecast(decision_date: date) -> dict:
    delivery_date = decision_date + timedelta(days=1)
    cutoff = datetime.combine(decision_date, CUTOFF_TIME, LONDON)
    return {
        "decisionDate": decision_date.isoformat(),
        "deliveryDate": delivery_date.isoformat(),
        "cutoff": cutoff.isoformat(),
        "timezone": "Europe/London",
        "unit": "MW",
    }
