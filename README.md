
# AgentX Indian Stock Trader — README

## Overview

This project implements a **fully autonomous, AI-driven stock trading system** for the Indian stock market using **AgentX**. It combines:

- **Market data fetching** (historical OHLC)  
- **AI-driven sentiment analysis** (transformer-based, NewsAPI, or keyword fallback)  
- **Adaptive strategy selection** based on historical performance  
- **Trading signal generation** (technical indicators)  
- **Risk management** (position sizing, capital allocation)  
- **Live trade execution** via Kite Connect (or mock testing)  
- **Trade logging and performance metrics**  

The system is designed for **modular deployment in AgentX**, using Agents and Tools to orchestrate end-to-end trading.

---

## Folder Structure

```
agentx-stock-trader-agentx-ready/
├─ scripts/
│  ├─ ai_strategy_agent.py         # AI sentiment + adaptive strategy selector
│  ├─ metrics_calculator.py        # Computes rolling strategy metrics
│  ├─ trader_manager_agent.py      # Full Manager Agent integrating all tools
│  ├─ market_data_fetcher.py       # Fetch historical OHLC data
│  ├─ signal_generator.py          # Generates BUY/SELL/HOLD signals
│  ├─ risk_manager.py              # Validates risk & calculates position size
│  ├─ trade_executor.py            # Executes mock trades
│  ├─ trade_executor_live.py       # Executes live trades via Kite Connect
│  └─ trade_logger.py              # Logs trade details and history
├─ logs/                           # Stores trade logs and history
├─ README.md                       # This file
```

---

## Requirements

- Python 3.10+  
- Required packages (install via pip):

```bash
pip install pandas requests kiteconnect yfinance transformers torch
```

> **Optional:** `transformers` and `torch` are required only for transformer-based sentiment (FinBERT).  

- Environment variables:  
  - `KITE_API_KEY` / `KITE_ACCESS_TOKEN` → for live trading  
  - `NEWSAPI_KEY` → optional, for richer sentiment analysis  

---

## Features

### 1. AI-Enhanced Sentiment Analysis

- **Transformer-based FinBERT** (preferred if `transformers` available)  
- **NewsAPI** fallback (requires `NEWSAPI_KEY`)  
- **Keyword-based** fallback if no API key or transformer available  
- Outputs: `{ score, summary, sources }`  
- Score ranges: `-1` (very negative) → `+1` (very positive)

### 2. Adaptive Strategy Selection

- Uses rolling **strategy performance metrics**:
  - Sharpe ratio  
  - Win rate  
  - Average return  
- Chooses best strategy based on **performance + sentiment tilt**  
- Supports momentum, trend, breakout, mean-reversion, and defensive strategies  

### 3. Manager Agent Orchestration

- **TraderManagerAgent** coordinates:
  1. Fetch market data → `market_data_fetcher`  
  2. Compute sentiment → `ai_strategy_agent.analyze_sentiment` / transformer / NewsAPI  
  3. Compute historical metrics → `metrics_calculator.compute_strategy_metrics`  
  4. Select strategy → `ai_strategy_agent.select_strategy`  
  5. Generate signal → `signal_generator`  
  6. Validate risk → `risk_manager`  
  7. Execute trade → `trade_executor` / `trade_executor_live`  
  8. Log trade → `trade_logger`  

- Returns comprehensive summary JSON:

```json
{
  "symbol": "RELIANCE.NS",
  "sentiment": {"score": 0.42, "summary": "...", "sources": [...]},
  "strategy_choice": {"strategy": "momentum", "params": {...}, "reason": "..."},
  "signal": {"action": "BUY", "confidence": 0.85},
  "risk": {"status": "APPROVED", "position_size": 30},
  "trade": {"status": "EXECUTED", "order_id": "T12345"},
  "log": {"file_path": "logs/trades.csv"}
}
```

---

## AgentX Setup

1. **Upload Scripts as Tools/Agents**:

   - Go to AgentX → `Create Agent` → `Custom Python Agent`  
   - Upload all `.py` files from `scripts/`  
   - Ensure `trader_manager_agent.py` is exposed as the main orchestrator  

2. **Create Workforce (Optional)**:

   - Combine all agents into a **single workforce** for scheduling  
   - Allows orchestration via GUI or API  

3. **Automation & Scheduling**:

   - Use **Automations → Scheduler** to run at market open (09:15 IST)  
   - Sample input JSON:

```json
{
  "symbol": "RELIANCE.NS",
  "capital": 100000,
  "period": "1mo"
}
```

- The system will now fetch market data, compute sentiment, auto-select strategy, execute trades, log trades, and update metrics.

---

## Environment Variables

| Variable       | Description                                        |
|----------------|---------------------------------------------------|
| KITE_API_KEY   | Kite Connect API key for live trading             |
| KITE_ACCESS_TOKEN | Kite Connect access token                     |
| NEWSAPI_KEY    | Optional, for fetching live news sentiment       |

---

## Optional Transformer Sentiment

- If `transformers` + `torch` are installed, `FinBERT` sentiment is preferred  
- Automatically falls back to NewsAPI or keyword sentiment if unavailable  

---

## Logs & Metrics

- All trades are logged to `logs/trade_history.csv`  
- Metrics are computed from this CSV automatically to adapt strategies  
- Logs include: timestamp, symbol, strategy, side, qty, price, exit_price, pnl  

---

## Notes

- Start with **mock execution** (`trade_executor.py`) to verify workflow  
- Switch to **live execution** (`trade_executor_live.py`) only after validation  
- Always verify **capital allocation and risk settings** before trading real funds  

---

## ASCII Workflow Diagram (AgentX)

```
[User Input] --> [MarketDataAgent] --> [AIAnalysisAgent] --> [StrategyAgent]
                                      |                         |
                                      v                         v
                               [MetricsAgent] --> [AI Strategy Selector]
                                      |
                                      v
                                [RiskAgent] --> [TradeExecutorAgent] --> [LoggerAgent]
```

- Flow is fully orchestrated by **TraderManagerAgent**  
