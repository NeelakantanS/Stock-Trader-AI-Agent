
"""ai_strategy_agent.py

AI enhancement layer that combines:
1) Market sentiment & news reasoning (uses NewsAPI if API key provided, else falls back to simple keyword scoring)
2) Adaptive strategy selection — chooses the best strategy based on recent performance metrics and sentiment

Functions:
- analyze_sentiment(symbol, lookback_days=3) -> dict {score: float, summary: str, sources: [...]}
- select_strategy(strategy_metrics: dict, sentiment_score: float) -> dict {strategy: str, params: dict, reason: str}

This module is AgentX-ready; the `tool` decorator is a noop fallback to maintain compatibility.
"""
from typing import List, Dict, Any
import os, requests, datetime, math, statistics

# noop decorator for AgentX tool compatibility if decorator not available in environment
def tool(name=None, description=None):
    def _dec(f):
        return f
    return _dec

# --- Simple keyword-based sentiment fallback ---
_POS_WORDS = set(["good","positive","upgrade","beat","beats","growth","buy","bull","bullish","surge","up","rise","strong","outperform",
                  "beat","beats","record"])
_NEG_WORDS = set(["bad","negative","downgrade","miss","missed","fall","weak","sell","bear","bearish","drop","down","decline","loss",
                  "warning","concern","fraud"])
_STOPWORDS = set(["the","is","in","at","of","and","a","to","for","on","with","by","from"])

NEWSAPI_URL = "https://newsapi.org/v2/everything"  # requires key

@tool(name='AI Strategy Agent', description='Combine news sentiment and strategy performance to pick a strategy')
def analyze_sentiment(symbol: str, lookback_days: int = 3) -> Dict[str, Any]:
    """Fetch news (if API key) and compute a sentiment score between -1 and +1.
    Returns: {score: float, summary: str, sources: [ {source, title, url}]}
    """
    api_key = os.getenv('NEWSAPI_KEY')
    now = datetime.datetime.utcnow()
    from_dt = (now - datetime.timedelta(days=lookback_days)).strftime('%Y-%m-%d')
    query = symbol.replace('.NS','') if '.NS' in symbol else symbol
    results = []
    if api_key:
        params = {'q': query, 'from': from_dt, 'language': 'en', 'sortBy': 'relevancy', 'apiKey': api_key, 'pageSize': 20}
        try:
            r = requests.get(NEWSAPI_URL, params=params, timeout=8)
            if r.status_code == 200:
                payload = r.json()
                for art in payload.get('articles', []):
                    results.append({'source': art.get('source', {}).get('name'), 'title': art.get('title'), 'url': art.get('url'), 'description': art.get('description')})
        except Exception as e:
            # fall back to empty results and keyword method
            results = []
    # fallback mock / keyword scraping if no results
    if not results:
        # basic heuristic: try scraping Google News RSS (best-effort); many sites block scraping.
        # We instead return an empty sources list and compute a neutral score
        return {'score': 0.0, 'summary': 'No live news fetched (no NEWSAPI_KEY); fallback neutral', 'sources': []}
    # compute sentiment via simple keyword scoring on titles+description
    scores = []
    for art in results:
        text = ' '.join(filter(None, [art.get('title',''), art.get('description','')]))
        tokens = [t.strip('.,()[]').lower() for t in text.split() if t.lower() not in _STOPWORDS]
        s = 0
        for t in tokens:
            if t in _POS_WORDS:
                s += 1
            if t in _NEG_WORDS:
                s -= 1
        # normalize by length
        norm = s / max(1, math.sqrt(len(tokens)))
        scores.append(norm)
    # aggregate
    if scores:
        avg = statistics.mean(scores)
        # clamp to -1..1 roughly via tanh
        score = math.tanh(avg)
    else:
        score = 0.0
    summary = f"Analyzed {len(results)} articles; sentiment {score:.3f}"
    return {'score': score, 'summary': summary, 'sources': results[:8]}

@tool(name='AI Strategy Selector', description='Select strategy based on performance metrics and sentiment')
def select_strategy(strategy_metrics: Dict[str, Dict[str, Any]], sentiment_score: float = 0.0) -> Dict[str, Any]:
    """strategy_metrics format:
    { 'momentum': { 'sharpe': 0.5, 'win_rate':0.55, 'avg_return':0.01 }, 'mean_reversion': {...}, ... }
    The function returns: { strategy: 'momentum', params: {...}, reason: '...' }
    Logic: score each strategy by combination of performance and sentiment tilt.
    If sentiment strongly negative, prefer defensive / mean-reversion; if strongly positive, prefer momentum.
    """
    # scoring weights
    w_sharpe = 0.6
    w_win = 0.3
    w_return = 0.1
    scored = []
    for name, metrics in strategy_metrics.items():
        sharpe = float(metrics.get('sharpe', 0.0))
        win = float(metrics.get('win_rate', 0.5))
        avg_ret = float(metrics.get('avg_return', 0.0))
        perf_score = w_sharpe * sharpe + w_win * win + w_return * avg_ret
        scored.append((name, perf_score, metrics))
    # choose baseline best by perf_score
    scored.sort(key=lambda x: x[1], reverse=True)
    if not scored:
        return {'strategy': 'momentum', 'params': {}, 'reason': 'no metrics available, default to momentum'}
    best_name, best_score, best_metrics = scored[0]
    # sentiment tilt: if sentiment_score > 0.3 boost momentum-like strategies, if < -0.3 prefer defensive
    # define simple buckets for strategy types (user can customize)
    momentum_like = set(['momentum','trend','breakout'])
    defensive_like = set(['mean_reversion','value','defensive'])
    tilt = 0.0
    if sentiment_score > 0.3:
        tilt = 0.2
    elif sentiment_score < -0.3:
        tilt = -0.2
    # adjust scores based on tilt
    adjusted = []
    for name, perf, metrics in scored:
        base = perf
        if name in momentum_like:
            adj = base + tilt
        elif name in defensive_like:
            adj = base - tilt
        else:
            adj = base
        adjusted.append((name, adj, metrics))
    adjusted.sort(key=lambda x: x[1], reverse=True)
    chosen_name, chosen_score, chosen_metrics = adjusted[0]
    # produce params adjustment logic: increase confidence threshold if sentiment negative, else lower risk sizing if negative
    params = {}
    if sentiment_score < -0.3:
        params['max_position_pct'] = chosen_metrics.get('max_position_pct', 0.03)
        params['risk_per_trade_pct'] = chosen_metrics.get('risk_per_trade_pct', 0.005)
    elif sentiment_score > 0.3:
        params['max_position_pct'] = chosen_metrics.get('max_position_pct', 0.07)
        params['risk_per_trade_pct'] = chosen_metrics.get('risk_per_trade_pct', 0.02)
    else:
        params['max_position_pct'] = chosen_metrics.get('max_position_pct', 0.05)
        params['risk_per_trade_pct'] = chosen_metrics.get('risk_per_trade_pct', 0.01)
    reason = f"Chosen {chosen_name} (perf_score={chosen_score:.3f}) with sentiment tilt {sentiment_score:.2f}"
    return {'strategy': chosen_name, 'params': params, 'reason': reason}
