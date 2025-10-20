
from agentx import tool
import json, os

# fallback decorator for AgentX tool
def tool(name=None, description=None):
    def _dec(f):
        return f
    return _dec

from scripts.market_data_fetcher import fetch_market_data
from scripts.signal_generator import generate_signal
from scripts.risk_manager import validate_risk
from scripts.trade_executor import execute_trade
from scripts.trade_logger import log_trade
from scripts.ai_strategy_agent import analyze_sentiment, select_strategy
from scripts.metrics_calculator import compute_strategy_metrics

# Optional transformer-based sentiment using FinBERT
def transformer_sentiment(symbol):
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
        tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
        model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")
        nlp = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
        # simple example: fetch last 5 news headlines (replace with proper news API in real use)
        headlines = [f"{symbol} stock up" for _ in range(5)]
        scores = []
        for h in headlines:
            res = nlp(h)[0]
            label = res['label']
            score = res['score']
            if label == 'positive':
                scores.append(score)
            elif label == 'negative':
                scores.append(-score)
            else:
                scores.append(0.0)
        avg = sum(scores)/len(scores)
        return avg
    except Exception:
        return None  # fallback to AI agent sentiment

@tool
def trader_manager(symbol: str, capital: float = 100000.0, period: str = "1mo"):
    """Manager Agent integrating AI sentiment, metrics, strategy selection, and trade execution"""
    try:
        print(f"🚀 Starting TraderManager for {symbol}")

        # 1️⃣ Market data
        data = fetch_market_data(symbol=symbol, period=period)
        print(f"✅ Market data fetched: {len(data['closes'])} candles")

        # 2️⃣ Sentiment analysis (transformer > NEWSAPI > keyword)
        sent_score = transformer_sentiment(symbol)
        if sent_score is None:
            sent = analyze_sentiment(symbol)
            sent_score = sent['score']
        else:
            sent = {'score': sent_score, 'summary': 'Transformer-based sentiment', 'sources': []}
        print(f"🧠 Sentiment score: {sent_score:.3f}")

        # 3️⃣ Compute metrics
        metrics = compute_strategy_metrics("logs/trade_history.csv")
        print(f"📊 Metrics computed: {metrics.keys()}")

        # 4️⃣ AI strategy selection
        choice = select_strategy(metrics, sentiment_score=sent_score)
        print(f"🤖 AI selected strategy: {choice['strategy']} | {choice['reason']}")

        # 5️⃣ Generate signal
        signal = generate_signal(data=data)
        print(f"📈 Signal generated: {signal['action']}")

        # 6️⃣ Risk validation
        risk = validate_risk(capital=capital, signal=signal)
        print(f"🧮 Risk check: {risk['status']} | Position Size: {risk.get('position_size', 0)}")

        # 7️⃣ Execute trade
        trade = execute_trade(symbol=symbol, side=signal['action'], qty=risk['position_size'])
        print(f"💹 Trade executed: {trade['status']}")

        # 8️⃣ Log trade
        log = log_trade(symbol=symbol, signal=signal, trade=trade, capital=capital)
        print(f"📝 Trade logged: {log['file_path']}")

        return {'symbol': symbol, 'sentiment': sent, 'strategy_choice': choice, 'signal': signal, 'risk': risk, 'trade': trade, 'log': log}

    except Exception as e:
        return {"error": str(e)}
