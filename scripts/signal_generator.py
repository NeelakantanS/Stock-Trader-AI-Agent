
"""signal_generator.py

AgentX-ready tool that consumes OHLC candles and generates simple signals.
Functions:
- generate_signals(data: dict) -> list of candidate dicts

Input 'data' format: { 'SYMBOL': [ {timestamp, open, high, low, close, volume}, ... ] }
Output candidate example:
  { 'symbol': 'RELIANCE.NS', 'signal': 'BUY', 'price': 2600.0, 'confidence': 0.7, 'reason': '...' }
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np

def tool(name=None, description=None):
    def _dec(f):
        return f
    return _dec

@tool(name='Signal Generator', description='SMA crossover + RSI filter')
def generate_signals(data: Dict[str, List[Dict[str, Any]]], params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    params = params or {}
    sma_short = params.get('sma_short', 20)
    sma_long = params.get('sma_long', 50)
    rsi_period = params.get('rsi_period', 14)
    rsi_upper = params.get('rsi_upper', 70)
    rsi_lower = params.get('rsi_lower', 30)
    candidates = []
    for symbol, candles in data.items():
        if not candles or len(candles) < max(sma_long, sma_short) + 1:
            continue
        df = pd.DataFrame(candles)
        df = df.sort_values('timestamp').reset_index(drop=True)
        close = df['close']
        df['sma_short'] = close.rolling(window=sma_short, min_periods=1).mean()
        df['sma_long'] = close.rolling(window=sma_long, min_periods=1).mean()
        # compute RSI
        delta = close.diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ma_up = up.rolling(window=rsi_period, min_periods=1).mean()
        ma_down = down.rolling(window=rsi_period, min_periods=1).mean()
        rs = ma_up / ma_down.replace(0, np.nan)
        df['rsi'] = 100 - (100 / (1 + rs))
        prev = df.iloc[-2]
        last = df.iloc[-1]
        bullish = (prev['sma_short'] <= prev['sma_long']) and (last['sma_short'] > last['sma_long'])
        bearish = (prev['sma_short'] >= prev['sma_long']) and (last['sma_short'] < last['sma_long'])
        if bullish and (rsi_lower <= last['rsi'] <= rsi_upper):
            candidates.append({'symbol': symbol, 'signal': 'BUY', 'price': float(last['close']), 'confidence': 0.7, 'reason': f'sma{(sma_short)}/{(sma_long)} crossover + rsi'})
        elif bearish:
            candidates.append({'symbol': symbol, 'signal': 'SELL', 'price': float(last['close']), 'confidence': 0.6, 'reason': 'bearish crossover'})
    return candidates

if __name__ == '__main__':
    from scripts.market_data_fetcher import fetch_ohlc
    data = {'RELIANCE.NS': fetch_ohlc('RELIANCE.NS', range='1mo')}
    print(generate_signals(data))
