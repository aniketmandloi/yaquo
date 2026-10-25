import json
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException

from app.accuracy import decision_accuracy
from app.forecasts import (
    FIRST_DECISION_DATE,
    LAST_DECISION_DATE,
    decision_forecast,
    latest_by_target,
)
from app.snapshot import load_observations


def parse_decision_date(value: str) -> date:
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        parsed = None
    if parsed is None or not FIRST_DECISION_DATE <= parsed <= LAST_DECISION_DATE:
        raise HTTPException(
            422,
            f"decision_date must be a date from {FIRST_DECISION_DATE} "
            f"to {LAST_DECISION_DATE}",
        )
    return parsed


def create_app(snapshot_dir: Path) -> FastAPI:
    forecasts = load_observations(snapshot_dir / "windfor.json")
    # Every retrieved actual is eligible: they are scored only in hindsight.
    actuals = latest_by_target(
        load_observations(snapshot_dir / "fuelhh_wind.json"), lambda obs: True
    )
    metadata = json.loads((snapshot_dir / "metadata.json").read_text())
    app = FastAPI(title="Wind procurement pilot")

    @app.get("/api/forecasts")
    def get_forecasts(decision_date: str) -> dict:
        return decision_forecast(forecasts, parse_decision_date(decision_date))

    @app.get("/api/accuracy")
    def get_accuracy(decision_date: str) -> dict:
        return decision_accuracy(forecasts, actuals, parse_decision_date(decision_date))

    @app.get("/api/snapshot")
    def get_snapshot() -> dict:
        return metadata

    return app
