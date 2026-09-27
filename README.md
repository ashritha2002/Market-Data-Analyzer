# Market Data Analyzer

A Python toolkit for pulling daily equity prices, storing them locally, and (in later milestones) computing returns, volatility and risk metrics.

## Status

| Milestone | Scope | Status |
|---|---|---|
| P1.1 | Repo setup + daily price loader (yfinance → CSV) | ✅ |
| P1.2 | Returns: simple `r_t = P_t/P_{t-1} − 1`, log `ln(P_t/P_{t-1})` | ⏳ |
| P1.3 | Volatility, rolling stats, correlation matrix | ⏳ |
| P1.4 | Risk metrics: historical VaR, max drawdown, Sharpe | ⏳ |

## Project structure

```
Market-Data-Analyzer/
├── src/market_data_analyzer/
│   └── data_loader.py      # download OHLCV → data/raw/*.csv
├── tests/
│   └── test_data_loader.py # offline tests (yfinance mocked)
├── data/raw/               # generated CSVs (git-ignored)
├── requirements.txt
└── pyproject.toml
```

## Setup

```bash
git clone https://github.com/ashritha2002/Market-Data-Analyzer.git
cd Market-Data-Analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Default: AAPL, MSFT, GOOGL, JPM, SPY from 2015-01-01 to today
PYTHONPATH=src python -m market_data_analyzer.data_loader

# Custom tickers / date range
PYTHONPATH=src python -m market_data_analyzer.data_loader --tickers NVDA TSLA --start 2020-01-01 --end 2025-01-01
```

Output in `data/raw/`:

1. `<TICKER>.csv` with columns `Date, Open, High, Low, Close, Adj Close, Volume`
2. `adj_close.csv`, a wide table with one Adj Close column per ticker, ready for returns analysis

## Tests

```bash
pytest
```

The tests mock `yfinance`, so they need no network access.

## Notes

1. `Adj Close` is adjusted for splits and dividends. Use it for return calculations. `Close` is the raw traded price.
2. Data comes from Yahoo Finance via `yfinance` (unofficial API). It's for research and learning, not production trading.
