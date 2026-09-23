import pandas as pd

from app.data.fundamentals import validate_and_align_fundamentals


def row(**overrides) -> dict:
    value = {
        "ticker": "ZENITHBANK",
        "fiscal_period": "2023-12-31",
        "publication_date": "2024-03-15",
        "book_equity": 100,
        "shares_outstanding": 31_396,
        "earnings_per_share": 3.4,
        "revenue": 250,
        "net_income": 50,
        "total_assets": 2_000,
        "total_liabilities": 1_900,
        "currency": "NGN",
        "monetary_unit_multiplier": 1_000_000,
        "shares_unit_multiplier": 1,
        "reporting_scope": "GROUP",
        "source_id": "zenith-2023-annual-report",
        "source_url": "https://example.test/zenith-2023.pdf",
        "source_sha256": "a" * 64,
        "source_document": "zenith-2023.pdf",
        "page_reference": "pp. 120-121",
        "notes": "",
    }
    value.update(overrides)
    return value


def test_actual_publication_date_controls_effective_date_and_units():
    result = validate_and_align_fundamentals(
        pd.DataFrame([row()]), {"ZENITHBANK"}
    )

    assert result.errors == []
    assert result.frame.loc[0, "effective_from"] == "2024-03-15"
    assert result.frame.loc[0, "effective_date_source"] == "ACTUAL_PUBLICATION_DATE"
    assert result.frame.loc[0, "book_equity"] == 100_000_000
    assert result.frame.loc[0, "shares_outstanding"] == 31_396
    assert result.frame.loc[0, "earnings_per_share"] == 3.4


def test_missing_publication_date_uses_declared_fixed_lag():
    result = validate_and_align_fundamentals(
        pd.DataFrame([row(publication_date=None)]), {"ZENITHBANK"}, lag_days=90
    )

    assert result.errors == []
    assert result.frame.loc[0, "effective_from"] == "2024-03-30"
    assert result.frame.loc[0, "effective_date_source"] == "FIXED_LAG_ESTIMATE"


def test_rejects_look_ahead_and_missing_source_hash():
    result = validate_and_align_fundamentals(
        pd.DataFrame([row(publication_date="2023-12-01", source_sha256="")]),
        {"ZENITHBANK"},
    )

    assert "publication_date precedes fiscal_period" in result.errors
    assert any("source_sha256" in error for error in result.errors)


def test_scales_monetary_values_and_share_counts_independently():
    result = validate_and_align_fundamentals(
        pd.DataFrame([
            row(
                book_equity=125,
                shares_outstanding=31_396,
                monetary_unit_multiplier=1_000_000,
                shares_unit_multiplier=1_000,
            )
        ]),
        {"ZENITHBANK"},
    )

    assert result.errors == []
    assert result.frame.loc[0, "book_equity"] == 125_000_000
    assert result.frame.loc[0, "shares_outstanding"] == 31_396_000


def test_can_revalidate_already_normalized_canonical_values_without_rescaling():
    result = validate_and_align_fundamentals(
        pd.DataFrame([row(book_equity=100_000_000, shares_outstanding=31_396_000)]),
        {"ZENITHBANK"},
        normalize_units=False,
    )

    assert result.errors == []
    assert result.frame.loc[0, "book_equity"] == 100_000_000
    assert result.frame.loc[0, "shares_outstanding"] == 31_396_000
