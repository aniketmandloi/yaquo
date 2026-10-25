import json
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.accuracy import decision_accuracy, period_accuracy
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


def create_app(snapshot_dir: Path, frontend_dir: Path | None = None) -> FastAPI:
    forecasts = load_observations(snapshot_dir / "windfor.json")
    # Every retrieved actual is eligible: they are scored only in hindsight.
    actuals = latest_by_target(
        load_observations(snapshot_dir / "fuelhh_wind.json"), lambda obs: True
    )
    metadata = json.loads((snapshot_dir / "metadata.json").read_text())
    period = period_accuracy(forecasts, actuals)
    app = FastAPI(title="Wind procurement pilot")

    @app.get("/api/forecasts")
    def get_forecasts(decision_date: str) -> dict:
        return decision_forecast(forecasts, parse_decision_date(decision_date))

    @app.get("/api/accuracy")
    def get_accuracy(decision_date: str) -> dict:
        day = decision_accuracy(forecasts, actuals, parse_decision_date(decision_date))
        return {**day, "period": period}

    @app.get("/api/snapshot")
    def get_snapshot() -> dict:
        return metadata

    if frontend_dir is not None:

        @app.get("/{path:path}")
        def get_frontend(path: str) -> FileResponse:
            if path == "api" or path.startswith("api/"):
                raise HTTPException(404)
            file = (frontend_dir / path).resolve()
            if file.is_file() and file.is_relative_to(frontend_dir.resolve()):
                return FileResponse(file)
            return FileResponse(frontend_dir / "index.html")

    return app
