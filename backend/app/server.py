from pathlib import Path

from app.main import create_app

backend_dir = Path(__file__).resolve().parent.parent
frontend_dir = backend_dir.parent / "frontend" / "dist"

app = create_app(
    backend_dir / "data" / "snapshot",
    frontend_dir if frontend_dir.is_dir() else None,
)
