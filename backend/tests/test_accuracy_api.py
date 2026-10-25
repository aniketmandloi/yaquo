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


def actual(start, publish, generation):
    return {
        "dataset": "FUELHH",
        "publishTime": publish,
        "startTime": start,
        "fuelType": "WIND",
        "generation": generation,
    }


@pytest.fixture
def client_for(tmp_path):
    def make(windfor, fuelhh):
        (tmp_path / "windfor.json").write_text(json.dumps(windfor))
        (tmp_path / "fuelhh_wind.json").write_text(json.dumps(fuelhh))
        (tmp_path / "metadata.json").write_text("{}")
        return TestClient(create_app(tmp_path))

    return make


def get_accuracy(client, decision_date="2026-01-15"):
    return client.get("/api/accuracy", params={"decision_date": decision_date}).json()


def pairs_by_start(body):
    return {row["startTime"]: row for row in body["day"]["pairs"]}


def test_day_scores_forecast_minus_actual_at_identical_targets(client_for):
    client = client_for(
        [
            forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", 1000),
            forecast("2026-01-16T01:00:00Z", "2026-01-15T07:30:00Z", 2000),
            forecast("2026-01-16T02:00:00Z", "2026-01-15T07:30:00Z", 1500),
        ],
        [
            actual("2026-01-16T00:00:00Z", "2026-01-16T00:30:00Z", 900),
            actual("2026-01-16T01:00:00Z", "2026-01-16T01:30:00Z", 2300),
            actual("2026-01-16T02:00:00Z", "2026-01-16T02:30:00Z", 1500),
        ],
    )

    body = get_accuracy(client)

    assert body["decisionDate"] == "2026-01-15"
    assert body["deliveryDate"] == "2026-01-16"
    assert body["cutoff"] == "2026-01-15T09:00:00+00:00"
    assert body["unit"] == "MW"
    assert pairs_by_start(body)["2026-01-16T00:00:00+00:00"] == {
        "startTime": "2026-01-16T00:00:00+00:00",
        "forecast": 1000,
        "forecastStatus": "selected",
        "forecastPublishTime": "2026-01-15T07:30:00+00:00",
        "actual": 900,
        "actualStatus": "selected",
        "actualPublishTime": "2026-01-16T00:30:00+00:00",
        "error": 100,
    }
    # Errors +100, -300, 0 MW.
    assert body["day"]["metrics"] == {
        "matchedPairs": 3,
        "mae": pytest.approx(400 / 3),
        "bias": pytest.approx(-200 / 3),
        "rmse": pytest.approx(182.574186),
    }
