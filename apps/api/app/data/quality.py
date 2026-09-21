"""Load the latest packaged dataset-quality report."""

import json
from pathlib import Path

from app.core.config import settings

PACKAGED_REPORT = Path(__file__).parent / "reports" / "latest.json"


def quality_report_path() -> Path:
    if settings.data_quality_report_path:
        return Path(settings.data_quality_report_path)
    return PACKAGED_REPORT


def load_quality_report() -> dict:
    path = quality_report_path()
    if not path.is_file():
        raise FileNotFoundError(f"dataset quality report not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))
