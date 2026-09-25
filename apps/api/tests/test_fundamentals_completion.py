from pathlib import Path

import pandas as pd
import pytest

from app.data.fundamentals_completion import build_completion_queue, completion_report_path


def test_completion_report_path_uses_packaged_copy_outside_monorepo(monkeypatch):
    module_file = Path("/service/app/data/fundamentals_completion.py")
    packaged_report = module_file.parent / "reports" / "fundamentals-2024-completion.json"
    monkeypatch.setattr(Path, "is_file", lambda path: path == packaged_report)

    assert completion_report_path(module_file) == packaged_report


def test_completion_queue_identifies_missing_issuers_and_periods():
    universe = pd.DataFrame(
        [
            {"ticker": "AAA", "company": "A", "sector": "Banking"},
            {"ticker": "BBB", "company": "B", "sector": "Industrial"},
        ]
    )
    current = pd.DataFrame(
        [{
            "ticker": "AAA", "fiscal_period": "2022-12-31", "book_equity": "100",
            "shares_outstanding": "10", "reporting_scope": "consolidated", "source_id": "a",
        }]
    )
    queue, summary = build_completion_queue(
        universe, current, ["2022-12-31", "2023-12-31"]
    )

    assert summary.expected_issuer_periods == 4
    assert summary.complete_issuer_periods == 1
    assert summary.remaining_issuers == ["BBB"]
    assert set(queue.loc[queue["ticker"] == "BBB", "status"]) == {"missing"}
    assert queue.loc[
        (queue["ticker"] == "AAA") & (queue["fiscal_period"] == "2023-12-31"),
        "status",
    ].item() == "missing"


def test_completion_queue_rejects_duplicate_current_keys():
    universe = pd.DataFrame([{"ticker": "AAA", "company": "A", "sector": "Banking"}])
    current = pd.DataFrame(
        [
            {"ticker": "AAA", "fiscal_period": "2022-12-31"},
            {"ticker": "AAA", "fiscal_period": "2022-12-31"},
        ]
    )
    with pytest.raises(ValueError, match="duplicate"):
        build_completion_queue(universe, current, ["2022-12-31"])
