"""Download daily OHLCV prices from Yahoo Finance and save them to CSV.

Usage (from repo root, venv active):
    python -m market_data_analyzer.data_loader
    python -m market_data_analyzer.data_loader --tickers AAPL MSFT --start 2020-01-01
"""
from __future__ import annotations

import argparse
import logging
from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf

DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "JPM", "SPY"]
DEFAULT_START = "2015-01-01"
DEFAULT_OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
PRICE_COLUMNS = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]

log = logging.getLogger(__name__)


def download_prices(tickers: list[str], start: str, end: str | None = None) -> dict[str, pd.DataFrame]:
    """Return {ticker: OHLCV DataFrame indexed by Date}. Tickers with no data are skipped."""
    raw = yf.download(
        tickers,
        start=start,
        end=end,
        interval="1d",
        auto_adjust=False,   # keep both Close and Adj Close
        group_by="ticker",   # columns: (ticker, field)
        progress=False,
        threads=True,
    )
    if raw is None or raw.empty:
        raise RuntimeError(f"No data returned for {tickers}")

    frames: dict[str, pd.DataFrame] = {}
    # Loop over tickers to extract their data and clean it up
    for ticker in tickers:
        if ticker not in raw.columns.get_level_values(0):
            log.warning("No data for %s, skipping", ticker)
            continue
        df = raw[ticker].dropna(how="all")
        if df.empty:
            log.warning("All-NaN data for %s, skipping", ticker)
            continue
        df = df[[c for c in PRICE_COLUMNS if c in df.columns]].copy()
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df.index.name = "Date"
        frames[ticker] = df.sort_index()
    return frames


def save_prices(frames: dict[str, pd.DataFrame], out_dir: Path) -> list[Path]:
    """Write one CSV per ticker plus a combined Adj Close panel. Returns written paths."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for ticker, df in frames.items():
        path = out_dir / f"{ticker}.csv"
        df.to_csv(path)
        written.append(path)
        log.info("%s: %d rows (%s -> %s) -> %s", ticker, len(df),
                 df.index.min().date(), df.index.max().date(), path.name)

    if frames:
        panel = pd.DataFrame({t: df["Adj Close"] for t, df in frames.items()})
        panel_path = out_dir / "adj_close.csv"
        panel.to_csv(panel_path)
        written.append(panel_path)
    return written


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS)
    p.add_argument("--start", default=DEFAULT_START, help="YYYY-MM-DD (inclusive)")
    p.add_argument("--end", default=None, help="YYYY-MM-DD (exclusive); default today")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    tickers = [t.upper() for t in args.tickers]
    log.info("Downloading %s from %s to %s", tickers, args.start, args.end or date.today())
    frames = download_prices(tickers, args.start, args.end)
    save_prices(frames, args.out)


if __name__ == "__main__":
    main()
