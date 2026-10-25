from datetime import date
from pathlib import Path

from fastapi import FastAPI

from app.forecasts import decision_forecast


def create_app(snapshot_dir: Path) -> FastAPI:
    app = FastAPI(title="Wind procurement pilot")

    @app.get("/api/forecasts")
    def get_forecasts(decision_date: str) -> dict:
        return decision_forecast(date.fromisoformat(decision_date))

    return app
