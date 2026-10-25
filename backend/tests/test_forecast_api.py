import json

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def forecast(start, publish, generation):
    return {
        "dataset": "WINDFOR",
        "publishTime": publish,
        "startTime": start,
        "generation": generation,
    }


@pytest.fixture
def client_for(tmp_path):
    def make(windfor):
        (tmp_path / "windfor.json").write_text(json.dumps(windfor))
        (tmp_path / "fuelhh_wind.json").write_text("[]")
        (tmp_path / "metadata.json").write_text(json.dumps({"retrievedAt": "x"}))
        return TestClient(create_app(tmp_path))

    return make


def test_decision_date_maps_to_next_delivery_day_and_london_cutoff(client_for):
    client = client_for([])

    body = client.get("/api/forecasts", params={"decision_date": "2026-01-15"}).json()

    assert body["decisionDate"] == "2026-01-15"
    assert body["deliveryDate"] == "2026-01-16"
    assert body["cutoff"] == "2026-01-15T09:00:00+00:00"
    assert body["timezone"] == "Europe/London"
    assert body["unit"] == "MW"
