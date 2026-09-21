from app.data.ngx_dol import parse_layout_text

HEADER = (
    "  Symbol                 Security Name            Price (N)      Official Open     "
    "Official Close    Market Price         Div    Sc      Price"
)


def test_parses_active_security_from_positioned_columns():
    row = list(" " * 170)
    values = {
        3: "ZENITHBANK",
        HEADER.index("Security Name"): "ZENITH BANK PLC",
        HEADER.index("Price (N)"): "0.50",
        HEADER.index("Official Open"): "44.85",
        HEADER.index("Official Close"): "45",
        HEADER.index("Market Price"): "45.00",
    }
    for start, value in values.items():
        row[start : start + len(value)] = value
    text = "Daily Official List (Equities) For 03/12/2024\n" + HEADER + "\n" + "".join(row)

    parsed = parse_layout_text(text, {"ZENITHBANK"}, "sample.pdf")[0]

    assert parsed.trading_date == "2024-12-03"
    assert parsed.security_name == "ZENITH BANK PLC"
    assert parsed.official_open == 44.85
    assert parsed.official_close == 45.0
    assert parsed.close == 45.0
    assert parsed.price_status == "official_trade"


def test_flags_carried_market_price_and_leaves_liquidity_missing():
    row = list(" " * 170)
    values = {
        3: "DANGCEM",
        HEADER.index("Security Name"): "DANGOTE CEMENT",
        HEADER.index("Price (N)"): "0.50",
        HEADER.index("Market Price"): "478.80",
    }
    for start, value in values.items():
        row[start : start + len(value)] = value
    text = "Daily Official List (Equities) For 03/12/2024\n" + HEADER + "\n" + "".join(row)

    parsed = parse_layout_text(text, {"DANGCEM"}, "sample.pdf")[0]

    assert parsed.official_open is None
    assert parsed.security_name == "DANGOTE CEMENT"
    assert parsed.official_close is None
    assert parsed.close == 478.8
    assert parsed.volume is None
    assert parsed.trading_value is None
    assert parsed.price_status == "carried_market_price"
