
import pandas as pd
import math

def compute_strategy_metrics(log_path="logs/trade_history.csv"):
    """Compute performance metrics per strategy from trade history"""
    if not pd.io.common.file_exists(log_path):
        return {}
    df = pd.read_csv(log_path)
    metrics = {}
    for strat, g in df.groupby("strategy"):
        pnl_pct = ((g["exit_price"] - g["price"]) / g["price"]) * g["qty"]
        avg_return = pnl_pct.mean()
        win_rate = (pnl_pct > 0).sum() / max(1, len(pnl_pct))
        sharpe = (avg_return / (pnl_pct.std() + 1e-6)) * math.sqrt(len(pnl_pct))
        metrics[strat] = {"sharpe": sharpe, "win_rate": win_rate, "avg_return": avg_return,
                          "max_position_pct": 0.05, "risk_per_trade_pct": 0.01}
    return metrics
