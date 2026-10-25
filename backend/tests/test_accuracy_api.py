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


def test_latest_retrieved_actual_publication_is_compared(client_for):
    client = client_for(
        [forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", 1000)],
        [
            actual("2026-01-16T00:00:00Z", "2026-01-16T00:30:00Z", 700),
            actual("2026-01-16T00:00:00Z", "2026-01-17T10:00:00Z", 800),
            actual("2026-01-16T00:00:00Z", "2026-01-16T05:00:00Z", 750),
        ],
    )

    row = pairs_by_start(get_accuracy(client))["2026-01-16T00:00:00+00:00"]

    assert row["actual"] == 800
    assert row["actualPublishTime"] == "2026-01-17T10:00:00+00:00"
    assert row["error"] == 200


@pytest.mark.parametrize(
    "latest_values, status",
    [([800, 850], "conflicting"), ([None], "invalid"), (["800"], "invalid")],
)
def test_unusable_latest_actual_is_excluded_without_older_fallback(
    client_for, latest_values, status
):
    client = client_for(
        [
            forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", 1000),
            forecast("2026-01-16T01:00:00Z", "2026-01-15T07:30:00Z", 1000),
        ],
        [
            actual("2026-01-16T00:00:00Z", "2026-01-16T00:30:00Z", 700),
            *[
                actual("2026-01-16T00:00:00Z", "2026-01-16T06:00:00Z", v)
                for v in latest_values
            ],
            actual("2026-01-16T01:00:00Z", "2026-01-16T01:30:00Z", 900),
        ],
    )

    body = get_accuracy(client)
    row = pairs_by_start(body)["2026-01-16T00:00:00+00:00"]

    assert row["actualStatus"] == status
    assert row["actual"] is None
    assert row["error"] is None
    assert body["day"]["metrics"]["matchedPairs"] == 1
    assert body["day"]["metrics"]["mae"] == 100


def test_identical_duplicate_actuals_count_once(client_for):
    client = client_for(
        [forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", 1000)],
        [
            actual("2026-01-16T00:00:00Z", "2026-01-16T00:30:00Z", 900),
            actual("2026-01-16T00:00:00Z", "2026-01-16T00:30:00Z", 900),
        ],
    )

    body = get_accuracy(client)

    assert pairs_by_start(body)["2026-01-16T00:00:00+00:00"]["actualStatus"] == (
        "selected"
    )
    assert body["day"]["metrics"]["matchedPairs"] == 1


def test_no_valid_pairs_is_insufficient_data_not_zero(client_for):
    client = client_for(
        [forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", 1000)],
        [actual("2026-01-16T01:00:00Z", "2026-01-16T01:30:00Z", 900)],
    )

    body = get_accuracy(client)
    pairs = pairs_by_start(body)

    assert pairs["2026-01-16T00:00:00+00:00"]["actualStatus"] == "missing"
    assert pairs["2026-01-16T00:00:00+00:00"]["actual"] is None
    assert pairs["2026-01-16T01:00:00+00:00"]["forecastStatus"] == "missing"
    assert body["day"]["metrics"] == {
        "matchedPairs": 0,
        "mae": None,
        "bias": None,
        "rmse": None,
    }


def test_valid_zero_error_is_a_zero_score(client_for):
    client = client_for(
        [forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", 0)],
        [actual("2026-01-16T00:00:00Z", "2026-01-16T00:30:00Z", 0)],
    )

    assert get_accuracy(client)["day"]["metrics"] == {
        "matchedPairs": 1,
        "mae": 0,
        "bias": 0,
        "rmse": 0,
    }


def test_coverage_separates_hourly_matches_from_half_hour_actual_timeline(client_for):
    client = client_for(
        [
            forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", 1000),
            forecast("2026-01-16T01:00:00Z", "2026-01-15T07:30:00Z", 1000),
            forecast("2026-01-16T01:00:00Z", "2026-01-15T07:30:00Z", 1100),
            forecast("2026-01-16T02:00:00Z", "2026-01-15T07:30:00Z", None),
        ],
        [
            actual("2026-01-16T00:00:00Z", "2026-01-16T00:30:00Z", 900),
            actual("2026-01-16T00:30:00Z", "2026-01-16T01:00:00Z", 950),
            actual("2026-01-16T01:00:00Z", "2026-01-16T01:30:00Z", 980),
            actual("2026-01-16T03:00:00Z", "2026-01-16T03:30:00Z", 700),
            actual("2026-01-16T03:00:00Z", "2026-01-16T03:30:00Z", 710),
            actual("2026-01-17T00:00:00Z", "2026-01-17T00:30:00Z", 600),
        ],
    )

    assert get_accuracy(client)["day"]["coverage"] == {
        "hourlyForecastTargets": 24,
        "forecast": {"selected": 1, "missing": 21, "conflicting": 1, "invalid": 1},
        "actualAtHourlyTargets": {
            "selected": 2,
            "missing": 21,
            "conflicting": 1,
            "invalid": 0,
        },
        "matchedPairs": 1,
        "halfHourActualTimeline": {
            "targets": 48,
            "selected": 3,
            "missing": 44,
            "conflicting": 1,
            "invalid": 0,
        },
    }


def test_period_metrics_pool_every_matched_error_across_january(client_for):
    client = client_for(
        [
            forecast("2026-01-02T00:00:00Z", "2026-01-01T07:30:00Z", 1300),
            forecast("2026-01-03T00:00:00Z", "2026-01-02T07:30:00Z", 1000),
            forecast("2026-01-03T01:00:00Z", "2026-01-02T07:30:00Z", 1000),
            forecast("2026-01-03T02:00:00Z", "2026-01-02T07:30:00Z", 900),
        ],
        [
            actual("2026-01-02T00:00:00Z", "2026-01-02T00:30:00Z", 1000),
            actual("2026-01-03T00:00:00Z", "2026-01-03T00:30:00Z", 1000),
            actual("2026-01-03T01:00:00Z", "2026-01-03T01:30:00Z", 1000),
            actual("2026-01-03T02:00:00Z", "2026-01-03T02:30:00Z", 1000),
        ],
    )

    body = get_accuracy(client, "2026-01-02")
    period = body["period"]

    assert body["day"]["metrics"]["matchedPairs"] == 3
    assert period["firstDecisionDate"] == "2026-01-01"
    assert period["lastDecisionDate"] == "2026-01-31"
    # Errors +300 on Jan 2 and 0, 0, -100 on Jan 3. Averaging the two daily
    # MAEs would give 166.7 MW instead.
    assert period["metrics"] == {
        "matchedPairs": 4,
        "mae": 100,
        "bias": 50,
        "rmse": pytest.approx(158.113883),
    }
    assert period["coverage"]["hourlyForecastTargets"] == 744
    assert period["coverage"]["forecast"]["selected"] == 4
    assert period["coverage"]["matchedPairs"] == 4
    assert period["coverage"]["halfHourActualTimeline"]["targets"] == 1488
    assert period["coverage"]["halfHourActualTimeline"]["selected"] == 4


def test_period_without_valid_pairs_is_insufficient_data(client_for):
    period = get_accuracy(client_for([], []))["period"]

    assert period["metrics"] == {
        "matchedPairs": 0,
        "mae": None,
        "bias": None,
        "rmse": None,
    }


def test_accuracy_uses_the_forecast_view_selection(client_for):
    client = client_for(
        [
            forecast("2026-01-16T00:00:00Z", "2026-01-15T07:30:00Z", 1000),
            forecast("2026-01-16T00:00:00Z", "2026-01-15T09:30:00Z", 1200),
            forecast("2026-01-16T01:00:00Z", "2026-01-15T07:30:00Z", 900),
            forecast("2026-01-16T01:00:00Z", "2026-01-15T07:30:00Z", 950),
        ],
        [actual("2026-01-16T00:00:00Z", "2026-01-16T00:30:00Z", 1200)],
    )

    view = client.get("/api/forecasts", params={"decision_date": "2026-01-15"}).json()
    body = get_accuracy(client)

    assert [
        (p["startTime"], p["forecast"], p["forecastStatus"], p["forecastPublishTime"])
        for p in body["day"]["pairs"]
    ] == [
        (t["startTime"], t["generation"], t["status"], t["publishTime"])
        for t in view["targets"]
    ]
    assert pairs_by_start(body)["2026-01-16T00:00:00+00:00"]["error"] == -200


@pytest.mark.parametrize("decision_date", ["2025-12-31", "2026-02-01", "nope"])
def test_accuracy_rejects_unsupported_decision_dates(client_for, decision_date):
    client = client_for([], [])

    response = client.get("/api/accuracy", params={"decision_date": decision_date})

    assert response.status_code == 422
    assert response.json() == {
        "detail": "decision_date must be a date from 2026-01-01 to 2026-01-31"
    }
