import json

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    snapshot = tmp_path / "snapshot"
    snapshot.mkdir()
    (snapshot / "windfor.json").write_text("[]")
    (snapshot / "fuelhh_wind.json").write_text("[]")
    (snapshot / "metadata.json").write_text(json.dumps({"retrievedAt": "x"}))
    frontend = tmp_path / "dist"
    (frontend / "assets").mkdir(parents=True)
    (frontend / "index.html").write_text("<div id=root></div>")
    (frontend / "assets" / "app.js").write_text("console.log(1)")
    return TestClient(create_app(snapshot, frontend))


def test_root_serves_the_built_frontend(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.text == "<div id=root></div>"


def test_built_assets_are_served_as_files(client):
    response = client.get("/assets/app.js")

    assert response.status_code == 200
    assert response.text == "console.log(1)"
    assert "javascript" in response.headers["content-type"]


def test_other_paths_fall_back_to_the_frontend_for_refresh(client):
    response = client.get("/accuracy")

    assert response.status_code == 200
    assert response.text == "<div id=root></div>"


def test_unknown_api_paths_are_not_found(client):
    assert client.get("/api/unknown").status_code == 404


def test_paths_cannot_escape_the_frontend_directory(client):
    response = client.get("/%2e%2e/snapshot/metadata.json")

    assert response.text == "<div id=root></div>"
