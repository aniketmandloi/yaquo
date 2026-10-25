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


def test_reports_hourly_targets_without_eligible_forecast_as_missing(client_for):
    client = client_for(
        [
            forecast("2026-01-16T05:00:00Z", "2026-01-15T07:30:00Z", 100),
            forecast("2026-01-16T06:00:00Z", "2026-01-15T09:30:00Z", 200),
            forecast("2026-01-15T23:00:00Z", "2026-01-15T07:30:00Z", 300),
            forecast("2026-01-17T00:00:00Z", "2026-01-15T07:30:00Z", 400),
        ]
    )

    body = client.get("/api/forecasts", params={"decision_date": "2026-01-15"}).json()
    targets = {row["startTime"]: row for row in body["targets"]}

    assert len(targets) == 24
    assert min(targets) == "2026-01-16T00:00:00+00:00"
    assert max(targets) == "2026-01-16T23:00:00+00:00"
    assert targets["2026-01-16T06:00:00+00:00"] == {
        "startTime": "2026-01-16T06:00:00+00:00",
        "status": "missing",
        "generation": None,
        "publishTime": None,
        "ageMinutes": None,
    }
    assert body["quality"] == {
        "expectedHourlyTargets": 24,
        "selected": 1,
        "missing": 23,
        "conflicting": 0,
        "invalid": 0,
    }


def test_conflicting_latest_key_is_excluded_without_older_fallback(client_for):
    client = client_for(
        [
            forecast("2026-01-16T00:00:00Z", "2026-01-15T04:30:00Z", 100),
            forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", 110),
            forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", 120),
            forecast("2026-01-16T01:00:00Z", "2026-01-15T07:30:00Z", 130),
            forecast("2026-01-16T01:00:00Z", "2026-01-15T07:30:00Z", 130),
        ]
    )

    body = client.get("/api/forecasts", params={"decision_date": "2026-01-15"}).json()
    targets = {row["startTime"]: row for row in body["targets"]}

    assert targets["2026-01-16T00:00:00+00:00"] == {
        "startTime": "2026-01-16T00:00:00+00:00",
        "status": "conflicting",
        "generation": None,
        "publishTime": "2026-01-15T07:30:00+00:00",
        "ageMinutes": 90,
    }
    assert targets["2026-01-16T01:00:00+00:00"]["status"] == "selected"
    assert targets["2026-01-16T01:00:00+00:00"]["generation"] == 130
    assert body["quality"]["conflicting"] == 1
    assert body["quality"]["selected"] == 1


@pytest.mark.parametrize("bad_value", [None, "1200", True, [1], float("nan")])
def test_invalid_latest_value_is_excluded_without_older_fallback(client_for, bad_value):
    client = client_for(
        [
            forecast("2026-01-16T00:00:00Z", "2026-01-15T04:30:00Z", 100),
            forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", bad_value),
            forecast("2026-01-16T01:00:00Z", "2026-01-15T07:30:00Z", 0),
        ]
    )

    body = client.get("/api/forecasts", params={"decision_date": "2026-01-15"}).json()
    targets = {row["startTime"]: row for row in body["targets"]}

    assert targets["2026-01-16T00:00:00+00:00"]["status"] == "invalid"
    assert targets["2026-01-16T00:00:00+00:00"]["generation"] is None
    assert targets["2026-01-16T01:00:00+00:00"]["status"] == "selected"
    assert targets["2026-01-16T01:00:00+00:00"]["generation"] == 0
    assert body["quality"]["invalid"] == 1


def test_first_and_last_january_decisions_cover_their_delivery_days(client_for):
    client = client_for(
        [
            forecast("2026-01-02T00:00:00Z", "2026-01-01T07:30:00Z", 100),
            forecast("2026-02-01T23:00:00Z", "2026-01-31T07:30:00Z", 200),
        ]
    )

    first = client.get("/api/forecasts", params={"decision_date": "2026-01-01"}).json()
    last = client.get("/api/forecasts", params={"decision_date": "2026-01-31"}).json()

    assert first["deliveryDate"] == "2026-01-02"
    assert first["targets"][0]["startTime"] == "2026-01-02T00:00:00+00:00"
    assert first["targets"][0]["generation"] == 100
    assert last["deliveryDate"] == "2026-02-01"
    assert last["targets"][-1]["startTime"] == "2026-02-01T23:00:00+00:00"
    assert last["targets"][-1]["generation"] == 200


@pytest.mark.parametrize(
    "decision_date", ["2025-12-31", "2026-02-01", "2026-01-32", "January 5", ""]
)
def test_unsupported_decision_dates_are_rejected(client_for, decision_date):
    client = client_for([])

    response = client.get("/api/forecasts", params={"decision_date": decision_date})

    assert response.status_code == 422
    assert response.json() == {
        "detail": "decision_date must be a date from 2026-01-01 to 2026-01-31"
    }


def test_snapshot_provenance_is_exposed(client_for):
    client = client_for([])

    assert client.get("/api/snapshot").json() == {"retrievedAt": "x"}


@pytest.mark.parametrize("values", [[1, True], [True, 1], [0, False], [False, 0]])
def test_boolean_and_number_at_latest_key_conflict_in_any_order(client_for, values):
    client = client_for(
        [forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", v) for v in values]
    )

    targets = get_targets(client)

    assert targets["2026-01-16T00:00:00+00:00"]["status"] == "conflicting"
    assert targets["2026-01-16T00:00:00+00:00"]["generation"] is None
