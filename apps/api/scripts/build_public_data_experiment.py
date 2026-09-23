"""Build the first deterministic experiment from validated public NGX data."""

from __future__ import annotations

import json
from argparse import ArgumentParser
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from app.data.market_inputs import build_monthly_market_inputs
from app.factors.characteristics import (
    build_point_in_time_characteristics,
    latest_characteristic_snapshot,
)
from app.factors.eligibility import evaluate_factor_eligibility
from app.quant.momentum_pilot import run_momentum_pilot
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
    parser.add_argument("--characteristics-output", type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--api-report", required=True, type=Path)
    parser.add_argument("--momentum-months", type=int, default=3)
    parser.add_argument("--benchmark", type=Path)
    parser.add_argument("--risk-free", type=Path)
    parser.add_argument("--benchmark-code", default="NGXASI")
    parser.add_argument("--risk-free-tenor", default="91D")
    args = parser.parse_args()
    if bool(args.benchmark) != bool(args.risk_free):
        parser.error("--benchmark and --risk-free must be provided together")

    prices = pd.read_csv(args.prices)
    fundamentals = pd.read_csv(args.fundamentals)
    daily, coverage = build_daily_returns(prices)
    monthly = build_monthly_returns(daily)
    characteristics, characteristic_coverage = build_point_in_time_characteristics(
        monthly, fundamentals
    )
    characteristic_snapshot = latest_characteristic_snapshot(characteristics)
    market_proxy = build_equal_weight_market_proxy(monthly)
    momentum = latest_momentum_snapshot(monthly, months=args.momentum_months)
    momentum_portfolio = run_momentum_pilot(
        monthly,
        lookback_months=args.momentum_months,
        portfolio_size=5,
        transaction_cost_bps=50,
    )
    market_inputs = pd.DataFrame()
    market_input_coverage = None
    if args.benchmark and args.risk_free:
        market_inputs, market_input_coverage = build_monthly_market_inputs(
            pd.read_csv(args.benchmark),
            pd.read_csv(args.risk_free),
            benchmark_code=args.benchmark_code,
            risk_free_tenor=args.risk_free_tenor,
        )
    benchmark_available = bool(
        market_input_coverage and market_input_coverage.benchmark_months > 0
    )
    risk_free_available = bool(
        market_input_coverage and market_input_coverage.risk_free_months > 0
    )
    eligibility = evaluate_factor_eligibility(
        prices,
        monthly,
        fundamentals,
        benchmark_available=benchmark_available,
        risk_free_available=risk_free_available,
        market_factor_observations=(
            int(market_inputs["market_excess_return"].notna().sum())
            if not market_inputs.empty
            else 0
        ),
    )
    marked_statistics = describe_returns(market_proxy["marked_equal_weight_return"])
    official_statistics = describe_returns(market_proxy["official_equal_weight_return"])
    market_factor_statistics = (
        describe_returns(market_inputs["market_excess_return"])
        if not market_inputs.empty
        else None
    )

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
            "risk_free_conversion": "effective monthly rate: (1 + annual rate)^(1/12) - 1",
        },
        "coverage": coverage.to_dict(),
        "market_input_coverage": (
            market_input_coverage.to_dict() if market_input_coverage else None
        ),
        "factor_eligibility": [result.to_dict() for result in eligibility],
        "characteristic_coverage": characteristic_coverage.to_dict(),
        "characteristics": records(characteristics),
        "latest_characteristics": records(characteristic_snapshot),
        "market_proxy_statistics": {
            "marked_price": marked_statistics,
            "official_trade": official_statistics,
            "annualised_return_difference": (
                marked_statistics["annualised_return"]
                - official_statistics["annualised_return"]
            ),
        },
        "market_proxy": records(market_proxy),
        "market_factor": records(market_inputs),
        "market_factor_statistics": market_factor_statistics,
        "latest_momentum": records(momentum),
        "momentum_portfolio": {
            **{key: value for key, value in momentum_portfolio.items() if key not in {"performance", "holdings"}},
            "performance": records(momentum_portfolio["performance"]),
            "holdings": records(momentum_portfolio["holdings"]),
        },
    }

    args.daily_output.parent.mkdir(parents=True, exist_ok=True)
    args.monthly_output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.api_report.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(args.daily_output, index=False)
    monthly.to_csv(args.monthly_output, index=False)
    if args.characteristics_output:
        args.characteristics_output.parent.mkdir(parents=True, exist_ok=True)
        characteristics.to_csv(args.characteristics_output, index=False)
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
