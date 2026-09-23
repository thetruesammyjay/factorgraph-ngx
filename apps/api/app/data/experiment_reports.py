"""Load packaged deterministic experiment reports."""

import json
from pathlib import Path

from app.core.config import settings

PACKAGED_PILOT_REPORT = Path(__file__).parent / "reports" / "pilot-latest.json"


def pilot_report_path() -> Path:
    if settings.pilot_experiment_report_path:
        return Path(settings.pilot_experiment_report_path)
    return PACKAGED_PILOT_REPORT


def load_pilot_report() -> dict:
    path = pilot_report_path()
    if not path.is_file():
        raise FileNotFoundError(f"pilot experiment report not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
