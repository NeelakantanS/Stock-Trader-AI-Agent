
"""market_data_fetcher.py

AgentX-ready tool to fetch OHLC data from Yahoo Finance (public endpoint).
Functions:
- fetch_ohlc(symbol, range='1mo', interval='1d') -> list of candles dict

Symbols: use Yahoo format, e.g., 'RELIANCE.NS' for NSE Reliance Industries.
"""
from typing import List, Dict, Any
import requests, time, os

# AgentX may expect a decorator like @tool; create a safe noop decorator if not present.
def tool(name=None, description=None):
    def _dec(f):
        return f
    return _dec

@tool(name='Market Data Fetcher', description='Fetch OHLC from Yahoo Finance')
def fetch_ohlc(symbol: str, range: str = '1mo', interval: str = '1d') -> List[Dict[str, Any]]:
    """Fetch OHLC data for `symbol` using Yahoo Finance chart API.
    Returns a list of candles: {timestamp, open, high, low, close, volume}
    """
    # sanitize symbol input
    if not symbol.upper().endswith('.NS'):
        # assume NSE if no suffix provided
        if '.' not in symbol:
            symbol = symbol + '.NS'
    url = f"https://query1.finance.yahoo.com/v7/finance/chart/{symbol}?range={range}&interval={interval}"
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        raise Exception(f"Yahoo Finance request failed: {resp.status_code} {resp.text}")
    data = resp.json().get('chart', {}).get('result')
    if not data:
        return []
    result = data[0]
    timestamps = result.get('timestamp', [])
    indicators = result.get('indicators', {}).get('quote', [])
    if not indicators:
        return []
    quote = indicators[0]
    candles = []
    for i, ts in enumerate(timestamps):
        o = quote.get('open', [None])[i]
        h = quote.get('high', [None])[i]
        l = quote.get('low', [None])[i]
        c = quote.get('close', [None])[i]
        v = quote.get('volume', [None])[i]
        # skip if data missing
        if o is None or c is None:
            continue
        candles.append({
            'timestamp': int(ts),
            'open': float(o),
            'high': float(h),
            'low': float(l),
            'close': float(c),
            'volume': int(v) if v is not None else None
        })
    return candles

if __name__ == '__main__':
    # quick demo
    print(fetch_ohlc('RELIANCE.NS', range='1mo', interval='1d')[:3])
