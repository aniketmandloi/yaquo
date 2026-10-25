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


def get_targets(client, decision_date="2026-01-15"):
    body = client.get("/api/forecasts", params={"decision_date": decision_date}).json()
    return {row["startTime"]: row for row in body["targets"]}


def test_selects_latest_publication_at_or_before_cutoff_per_target(client_for):
    client = client_for(
        [
            forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", 100),
            forecast("2026-01-16T00:00:00Z", "2026-01-15T09:00:00Z", 200),
            forecast("2026-01-16T00:00:00Z", "2026-01-15T09:30:00Z", 300),
            forecast("2026-01-16T01:00:00Z", "2026-01-15T07:30:00Z", 400),
            forecast("2026-01-16T01:00:00Z", "2026-01-15T11:30:00Z", 500),
        ]
    )

    targets = get_targets(client)

    assert targets["2026-01-16T00:00:00+00:00"] == {
        "startTime": "2026-01-16T00:00:00+00:00",
        "status": "selected",
        "generation": 200,
        "publishTime": "2026-01-15T09:00:00+00:00",
        "ageMinutes": 0,
    }
    assert targets["2026-01-16T01:00:00+00:00"]["generation"] == 400
    assert targets["2026-01-16T01:00:00+00:00"]["ageMinutes"] == 90
