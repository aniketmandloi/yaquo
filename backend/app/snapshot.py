import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Observation:
    start: datetime
    publish: datetime
    generation: object


def parse_instant(value: str) -> datetime:
    return datetime.fromisoformat(value)


def load_observations(path: Path) -> list[Observation]:
    return [
        Observation(
            parse_instant(record["startTime"]),
            parse_instant(record["publishTime"]),
            record["generation"],
        )
        for record in json.loads(path.read_text())
    ]
