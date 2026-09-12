import pandas as pd
from app.quant.transaction_costs import net_returns
from app.quant.returns import cumulative_return, max_drawdown

def run_backtest(returns: pd.DataFrame, weights: pd.DataFrame, transaction_cost_bps: float = 50) -> dict:
    portfolio = (returns * weights.shift(1).fillna(0)).sum(axis=1)
    turnover = weights.diff().abs().sum(axis=1).fillna(0)
    net = net_returns(portfolio, turnover, transaction_cost_bps)
    return {"returns": net, "cumulative_return": cumulative_return(net), "max_drawdown": max_drawdown(net), "turnover": turnover}