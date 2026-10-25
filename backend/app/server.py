from pathlib import Path

from app.main import create_app

app = create_app(Path(__file__).resolve().parent.parent / "data" / "snapshot")
