from datetime import date
from pathlib import Path

from fastapi import FastAPI

from app.forecasts import decision_forecast
from app.snapshot import load_observations


def create_app(snapshot_dir: Path) -> FastAPI:
    forecasts = load_observations(snapshot_dir / "windfor.json")
    app = FastAPI(title="Wind procurement pilot")

    @app.get("/api/forecasts")
    def get_forecasts(decision_date: str) -> dict:
        return decision_forecast(forecasts, date.fromisoformat(decision_date))

    return app
