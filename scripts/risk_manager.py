
"""risk_manager.py

AgentX-ready risk manager tool.
Function:
- validate_trades(candidates, account_equity=100000, params=None)

Defaults:
- account_equity default 100000 (₹100k) unless provided.
- default risk_per_trade_pct = 0.02 (2%)
- default stop_loss_pct = 0.05 (5%)
"""
from typing import List, Dict, Any
import os, math, uuid

def tool(name=None, description=None):
    def _dec(f):
        return f
    return _dec

@tool(name='Risk Manager', description='Position sizing and hard checks')
def validate_trades(candidates: List[Dict[str, Any]], account_equity: float = None, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    params = params or {}
    if account_equity is None:
        # default equity from env var or fallback
        account_equity = float(os.getenv('DEFAULT_EQUITY', '100000'))
    risk_per_trade_pct = float(params.get('risk_per_trade_pct', 0.02))
    stop_loss_pct = float(params.get('stop_loss_pct', 0.05))
    max_position_pct = float(params.get('max_position_pct', 0.05))
    validated = []
    for c in candidates:
        side = 'BUY' if c.get('signal') == 'BUY' else 'SELL'
        price = float(c.get('price'))
        stop_distance = price * stop_loss_pct
        risk_amount = account_equity * risk_per_trade_pct
        raw_qty = int(max(1, (risk_amount / stop_distance)))
        max_notional = account_equity * max_position_pct
        if raw_qty * price > max_notional:
            qty = int(max(1, max_notional // price))
        else:
            qty = raw_qty
        if qty <= 0:
            continue
        order = {
            'symbol': c.get('symbol'),
            'side': side,
            'qty': qty,
            'price': price,
            'stop_loss': round(price - stop_distance, 2) if side == 'BUY' else round(price + stop_distance, 2),
            'client_order_id': f"{c.get('symbol')}-{uuid.uuid4().hex[:8]}",
            'notional': round(qty * price, 2),
            'reason': c.get('reason'),
            'confidence': c.get('confidence', 0.0)
        }
        # enforce minimum notional (₹1000)
        if order['notional'] < 1000:
            continue
        validated.append(order)
    return validated

if __name__ == '__main__':
    sample = [{'symbol':'RELIANCE.NS','signal':'BUY','price':2600,'confidence':0.7,'reason':'test'}]
    print(validate_trades(sample))
