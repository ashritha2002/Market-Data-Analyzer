"""Offline tests: yfinance is mocked, so these run without network."""
import numpy as np
import pandas as pd
import pytest

from market_data_analyzer import data_loader as dl

FIELDS = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]


def fake_download(tickers, **kwargs):
    idx = pd.date_range("2024-01-01", periods=5, freq="B", name="Date")
    cols = pd.MultiIndex.from_product([tickers, FIELDS])
    data = np.arange(len(idx) * len(cols), dtype=float).reshape(len(idx), len(cols))
    df = pd.DataFrame(data, index=idx, columns=cols)
    if "BAD" in tickers:
        df["BAD"] = np.nan
    return df


def test_download_and_save(tmp_path, monkeypatch):
    monkeypatch.setattr(dl.yf, "download", fake_download)
    frames = dl.download_prices(["AAPL", "MSFT", "BAD"], start="2024-01-01")

    assert set(frames) == {"AAPL", "MSFT"}          # all-NaN ticker skipped
    assert list(frames["AAPL"].columns) == FIELDS

    written = dl.save_prices(frames, tmp_path)
    assert {p.name for p in written} == {"AAPL.csv", "MSFT.csv", "adj_close.csv"}

    back = pd.read_csv(tmp_path / "AAPL.csv", index_col="Date", parse_dates=True)
    assert len(back) == 5
    panel = pd.read_csv(tmp_path / "adj_close.csv", index_col="Date")
    assert list(panel.columns) == ["AAPL", "MSFT"]


def test_empty_download_raises(monkeypatch):
    monkeypatch.setattr(dl.yf, "download", lambda *a, **k: pd.DataFrame())
    with pytest.raises(RuntimeError):
        dl.download_prices(["AAPL"], start="2024-01-01")
