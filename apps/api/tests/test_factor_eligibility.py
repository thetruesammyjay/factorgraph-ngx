import pandas as pd

from app.factors.eligibility import evaluate_factor_eligibility


def test_public_pilot_marks_partial_factors_and_blocks_liquidity():
    prices = pd.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "volume": [None, None],
            "trading_value": [None, None],
            "number_of_transactions": [None, None],
        }
    )
    monthly = pd.DataFrame(
        {
            "ticker": ["AAA"] * 12,
            "observation_month": [f"2024-{month:02d}" for month in range(1, 13)],
        }
    )
    fundamentals = pd.DataFrame(
        {"ticker": ["AAA"], "book_equity": [100], "shares_outstanding": [10]}
    )

    results = {
        result.factor: result
        for result in evaluate_factor_eligibility(
            prices,
            monthly,
            fundamentals,
            expected_tickers=2,
            expected_fundamentals=4,
        )
    }

    assert results["market"].status == "preliminary"
    assert results["size"].status == "preliminary"
    assert results["value"].metrics["positive_book_equity_rows"] == 1
    assert results["momentum"].status == "preliminary"
    assert results["liquidity"].status == "blocked"
    assert results["liquidity"].metrics["volume"] == 0


def test_market_is_eligible_only_with_an_aligned_excess_return():
    prices = pd.DataFrame({"ticker": ["AAA"]})
    monthly = pd.DataFrame({"ticker": ["AAA"], "observation_month": ["2024-01"]})
    fundamentals = pd.DataFrame(columns=["ticker", "book_equity"])

    result = evaluate_factor_eligibility(
        prices,
        monthly,
        fundamentals,
        benchmark_available=True,
        risk_free_available=True,
        market_factor_observations=1,
    )[0]

    assert result.status == "eligible"
    assert result.metrics["market_factor_observations"] == 1
