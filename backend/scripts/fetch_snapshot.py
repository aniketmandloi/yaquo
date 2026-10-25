"""Retrieve the bundled Elexon wind snapshot.

Usage: python scripts/fetch_snapshot.py [output_dir]

Writes windfor.json, fuelhh_wind.json and metadata.json. Provider responses are
not guaranteed to be identical between retrievals, so a rerun may change hashes.
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

API = "https://data.elexon.co.uk/bmrs/api/v1/datasets"

# Publication-time windows, not target-time windows. Bounds are inclusive on
# the provider side, so targets are filtered later by the application.
QUERIES = {
    "WINDFOR": {
        "file": "windfor.json",
        "publishDateTimeFrom": "2026-01-01T00:00:00Z",
        "publishDateTimeTo": "2026-02-01T00:00:00Z",
        "transformation": "None; all returned records are stored unchanged.",
    },
    "FUELHH": {
        "file": "fuelhh_wind.json",
        "publishDateTimeFrom": "2026-01-02T00:00:00Z",
        "publishDateTimeTo": "2026-02-03T00:00:00Z",
        "transformation": 'Records kept only where fuelType == "WIND"; '
        "kept records are stored unchanged.",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(dataset: str, query: dict) -> tuple[str, bytes]:
    params = {
        "publishDateTimeFrom": query["publishDateTimeFrom"],
        "publishDateTimeTo": query["publishDateTimeTo"],
    }
    url = f"{API}/{dataset}/stream?{urlencode(params)}"
    with urlopen(url, timeout=120) as response:
        return url, response.read()


def main(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    datasets = {}
    for dataset, query in QUERIES.items():
        url, raw = fetch(dataset, query)
        records = json.loads(raw)
        if dataset == "FUELHH":
            stored = [r for r in records if r.get("fuelType") == "WIND"]
        else:
            stored = records
        content = json.dumps(stored, separators=(",", ":")).encode()
        (output_dir / query["file"]).write_bytes(content)
        datasets[dataset] = {
            "file": query["file"],
            "url": url,
            "publishDateTimeFrom": query["publishDateTimeFrom"],
            "publishDateTimeTo": query["publishDateTimeTo"],
            "responseBytes": len(raw),
            "responseSha256": sha256(raw),
            "responseRecords": len(records),
            "transformation": query["transformation"],
            "storedRecords": len(stored),
            "storedSha256": sha256(content),
        }
    metadata = {"retrievedAt": retrieved_at, "datasets": datasets}
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    default = Path(__file__).resolve().parent.parent / "data" / "snapshot"
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else default)
