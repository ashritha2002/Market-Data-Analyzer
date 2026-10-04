"""A minimal equity portfolio: positions and their market value.

Market value:  MV = sum_i  shares_i * price_i
"""
from __future__ import annotations

import math


class Portfolio:
    def __init__(self) -> None:
        # ticker -> {"shares": float, "price": float}
        self.positions: dict[str, dict[str, float]] = {}

    def add_position(self, ticker: str, shares: float, price: float) -> None:
        """Add shares of `ticker` at `price` (the current price per share).

        Adding to an existing ticker accumulates shares and updates the
        price to the latest one given.
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("ticker must be a non-empty string")
        if shares <= 0:
            raise ValueError("shares must be positive")
        if price <= 0:
            raise ValueError("price must be positive")

        ticker = ticker.upper()
        pos = self.positions.setdefault(ticker, {"shares": 0.0, "price": price})
        pos["shares"] += shares
        pos["price"] = price

    def market_value(self) -> float:
        """Total current value: sum of shares * price over all positions."""
        return sum(p["shares"] * p["price"] for p in self.positions.values())

    def __repr__(self) -> str:
        if not self.positions:
            return "Portfolio(empty)"
        lines = [f"{'Ticker':<8}{'Shares':>10}{'Price':>12}{'Value':>14}"]
        for t, p in self.positions.items():
            lines.append(
                f"{t:<8}{p['shares']:>10,.2f}{p['price']:>12,.2f}"
                f"{p['shares'] * p['price']:>14,.2f}"
            )
        lines.append(f"{'Total':<30}{self.market_value():>14,.2f}")
        return "Portfolio(\n  " + "\n  ".join(lines) + "\n)"


if __name__ == "__main__":
    pf = Portfolio()

    # 1. Empty portfolio is worth nothing
    assert pf.market_value() == 0

    pf.add_position("AAPL", 10, 150.0)
    pf.add_position("MSFT", 5, 300.0)

    # 2. MV = 10*150 + 5*300 = 3000
    assert math.isclose(pf.market_value(), 3000.0)

    # 3. Adding to an existing ticker accumulates shares, price updates to latest
    pf.add_position("aapl", 5, 160.0)
    assert pf.positions["AAPL"]["shares"] == 15 and pf.positions["AAPL"]["price"] == 160.0

    # 4. MV = 15*160 + 5*300 = 3900
    assert math.isclose(pf.market_value(), 3900.0)

    # 5. Invalid input is rejected
    try:
        pf.add_position("JPM", -1, 100.0)
        assert False, "negative shares should raise"
    except ValueError:
        pass

    print(pf)
    print("All asserts passed.")
