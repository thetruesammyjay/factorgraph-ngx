"""Build the first deterministic experiment from validated public NGX data."""

from __future__ import annotations

import json
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from app.factors.eligibility import evaluate_factor_eligibility
from app.quant.return_engine import (
    build_daily_returns,
    build_equal_weight_market_proxy,
    build_monthly_returns,
    latest_momentum_snapshot,
)
from app.quant.statistics import describe_returns


def records(frame: pd.DataFrame) -> list[dict]:
    clean = frame.copy()
    for column in clean.select_dtypes(include=["datetime", "datetimetz"]).columns:
        clean[column] = clean[column].dt.strftime("%Y-%m-%d")
    return json.loads(clean.where(pd.notna(clean), None).to_json(orient="records"))


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--prices", required=True, type=Path)
    parser.add_argument("--fundamentals", required=True, type=Path)
    parser.add_argument("--daily-output", required=True, type=Path)
    parser.add_argument("--monthly-output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--api-report", required=True, type=Path)
    parser.add_argument("--momentum-months", type=int, default=3)
    args = parser.parse_args()

    prices = pd.read_csv(args.prices)
    fundamentals = pd.read_csv(args.fundamentals)
    daily, coverage = build_daily_returns(prices)
    monthly = build_monthly_returns(daily)
    market_proxy = build_equal_weight_market_proxy(monthly)
    momentum = latest_momentum_snapshot(monthly, months=args.momentum_months)
    eligibility = evaluate_factor_eligibility(prices, monthly, fundamentals)
    marked_statistics = describe_returns(market_proxy["marked_equal_weight_return"])
    official_statistics = describe_returns(market_proxy["official_equal_weight_return"])

    report = {
        "experiment_id": "ngx-public-data-2024-pilot-v1",
        "name": "2024 public-data return and eligibility pilot",
        "status": "completed_with_constraints",
        "generated_at": datetime.now(UTC).isoformat(),
        "price_dataset": args.prices.name,
        "fundamentals_dataset": args.fundamentals.name,
        "methodology": {
            "marked_return": "close-to-close return using every staged market price",
            "official_trade_return": "return between consecutive official-trade observations",
            "market_proxy": "equal-weight mean across available security returns",
            "momentum_window_months": args.momentum_months,
            "missing_values": "not imputed",
        },
        "coverage": coverage.to_dict(),
        "factor_eligibility": [result.to_dict() for result in eligibility],
        "market_proxy_statistics": {
            "marked_price": marked_statistics,
            "official_trade": official_statistics,
            "annualised_return_difference": (
                marked_statistics["annualised_return"]
                - official_statistics["annualised_return"]
            ),
        },
        "market_proxy": records(market_proxy),
        "latest_momentum": records(momentum),
    }

    args.daily_output.parent.mkdir(parents=True, exist_ok=True)
    args.monthly_output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.api_report.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(args.daily_output, index=False)
    monthly.to_csv(args.monthly_output, index=False)
    document = json.dumps(report, indent=2, allow_nan=False) + "\n"
    args.report.write_text(document, encoding="utf-8")
    args.api_report.write_text(document, encoding="utf-8")
    print(
        json.dumps(
            {
                "experiment_id": report["experiment_id"],
                "coverage": report["coverage"],
                "factor_statuses": {
                    item["factor"]: item["status"]
                    for item in report["factor_eligibility"]
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
