import pandas as pd
from app.factors.market import MarketFactor
from app.quant.returns import cumulative_return

def test_market_excess_return():
    data = pd.DataFrame({"market_return": [.02, -.01], "risk_free_rate": [.005, .005]})
    result = MarketFactor().calculate(data)
    assert result.tolist() == [.015, -.015]

def test_cumulative_return():
    assert round(cumulative_return(pd.Series([.1, -.1])), 6) == -.01