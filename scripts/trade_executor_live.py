
"""trade_executor_live.py

Optional Kite Connect integration (end-to-end helper).

Functions:
- get_login_url(api_key, redirect_uri) -> str
- fetch_access_token(api_key, api_secret, request_token) -> access_token
- init_kite(api_key, access_token) -> kite_client
- place_order_live(kite_client, order) -> result dict

Usage:
1. Set KITE_API_KEY and KITE_API_SECRET as env vars or pass them explicitly.
2. Call get_login_url() and open in browser.
3. After login, obtain `request_token` from redirect URL and call fetch_access_token(...)
4. Save ACCESS_TOKEN and call init_kite(...) then place_order_live(...)

Security: Use AgentX secret store or env vars. Do NOT commit secrets.
"""
from typing import Dict, Any
import os, time
try:
    from kiteconnect import KiteConnect, KiteTicker
except Exception as e:
    KiteConnect = None  # kiteconnect not installed; functions will raise if used without installing

def get_login_url(api_key: str, redirect_uri: str = "http://127.0.0.1:8080/") -> str:
    """Returns the login URL to fetch request_token."""
    if not api_key:
        raise ValueError("api_key required")
    if KiteConnect is None:
        raise RuntimeError("kiteconnect package not installed. pip install kiteconnect")
    kite = KiteConnect(api_key=api_key)
    return kite.login_url(redirect_uri=redirect_uri)

def fetch_access_token(api_key: str, api_secret: str, request_token: str) -> str:
    """Exchanges request_token for access_token. Returns access_token string."""
    if KiteConnect is None:
        raise RuntimeError("kiteconnect package not installed. pip install kiteconnect")
    kite = KiteConnect(api_key=api_key)
    # this will raise if invalid; also stores access_token in kite.client
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data.get('access_token')
    return access_token

def init_kite(api_key: str, access_token: str):
    """Initialize and return a KiteConnect client with access_token set."""
    if KiteConnect is None:
        raise RuntimeError("kiteconnect package not installed. pip install kiteconnect")
    kite = KiteConnect(api_key=api_key)
    kite.set_access_token(access_token)
    return kite

def place_order_live(kite, order: Dict[str, Any]) -> Dict[str, Any]:
    """Place an order via kite API. Order keys expected: symbol (e.g., 'RELIANCE'), side 'BUY'/'SELL', qty, price, order_type ('MARKET'/'LIMIT'), product ('MIS'/'NRML')"""
    if kite is None:
        raise ValueError("kite client required")
    # map symbol to exchange instrument token / tradingsymbol expected by kite
    # For simplicity assume NSE equity, instrument token lookup is required for real use.
    tradingsymbol = order.get('symbol')
    side = order.get('side', 'BUY').upper()
    qty = int(order.get('qty', 1))
    order_type = order.get('order_type', 'MARKET').upper()
    product = order.get('product', 'MIS')  # intraday by default
    variety = order.get('variety', 'regular')
    price = order.get('price', None)
    try:
        params = {
            'tradingsymbol': tradingsymbol,
            'exchange': 'NSE',
            'transaction_type': 'BUY' if side == 'BUY' else 'SELL',
            'quantity': qty,
            'product': product,
            'order_type': order_type
        }
        if order_type == 'LIMIT' and price is not None:
            params['price'] = float(price)
            params['trigger_price'] = float(order.get('trigger_price', 0.0))
        # place order
        res = kite.place_order(**params)
        return {'status': 'ok', 'kite_response': res}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

if __name__ == '__main__':
    print('This module provides helper functions to integrate with Zerodha KiteConnect.')
