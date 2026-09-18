"""
Build and evaluate an RSI Strategy

Dependencies: pandas, numpy, yfinance, TA-Lib, matplotlib.
Run this file to download prices, print numeric results, and show two plots.
"""

import numpy as np
import pandas as pd
import yfinance as yf
import talib
import matplotlib.pyplot as plt

TICKER = "DELL"
START_DATE = "2020-09-01"
END_DATE = "2026-09-01"
SPLIT_DATE = "2025-09-01"
TRANSACTION_COST = 0.001
TRADING_DAYS = 252


def download_prices(ticker=TICKER, start=START_DATE, end=END_DATE):
    """Download one ticker; keep the original adjusted-close data choice."""
    data = yf.download(ticker, start=start, end=end, auto_adjust=False)
    if data.empty:
        raise ValueError(f"No prices returned for {ticker}.")
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    if "Adj Close" not in data.columns:
        raise ValueError("Price data must include 'Adj Close'.")
    return data.sort_index()


def add_indicators(data):
    """Compute indicators before removing their warm-up rows."""
    data = data.copy()
    close = data["Adj Close"].astype(float)
    data["RSI_14"] = talib.RSI(close, timeperiod=14)
    data["MA_200"] = close.rolling(window=200).mean()
    return data.dropna(subset=["RSI_14", "MA_200"]).copy()


def generate_positions(data):
    """Keep entry priority, long/cash state, and the original one-row shift."""
    data = data.copy()
    rsi = data["RSI_14"]
    previous_rsi = rsi.shift(1)
    data["Entry"] = (
        (rsi > 50) & (previous_rsi <= 50)
        & (data["Adj Close"] > data["MA_200"])
    )
    # Exit: RSI crosses below 40 OR adjusted close is below MA200.
    data["Exit"] = (
        ((rsi < 40) & (previous_rsi >= 40))
        | (data["Adj Close"] < data["MA_200"])
    )
    position = 0
    positions = []
    for entry, exit_signal in zip(data["Entry"], data["Exit"]):
        if entry:
            position = 1
        elif exit_signal:
            position = 0
        positions.append(position)
    data["Position"] = positions
    data["Trade_Position"] = data["Position"].shift(1).fillna(0)
    data["Trade"] = data["Trade_Position"].diff().fillna(0)
    return data


def equity_curve(returns):
    """Compound returns using an initial investment of $1 before the first row."""
    return (1 + returns.fillna(0)).cumprod()


def calculate_returns(data, transaction_cost=TRANSACTION_COST):
    """Preserve close-to-close returns and cost per position change."""
    data = data.copy()
    data["Market_Return"] = data["Adj Close"].pct_change()
    data["Strategy_Return"] = data["Market_Return"] * data["Trade_Position"]
    data["Cost"] = data["Trade"].abs() * transaction_cost
    data["Net_Strategy_Return"] = data["Strategy_Return"] - data["Cost"]
    # Retain these columns for compatibility and optional full-period analysis.
    data["Market_Equity"] = equity_curve(data["Market_Return"])
    data["Strategy_Equity"] = equity_curve(data["Net_Strategy_Return"])
    return data


def backtest(prices, transaction_cost=TRANSACTION_COST):
    """Run the strategy independently of downloading or plotting."""
    data = add_indicators(prices.sort_index())
    if data.empty:
        raise ValueError("Not enough valid prices after indicator warm-up.")
    return calculate_returns(generate_positions(data), transaction_cost)


def return_metrics(returns):
    """Original metric definitions; zero/undefined volatility gives NaN Sharpe.

    Drawdown intentionally uses observed equity peaks, as in the source file.
    Sharpe assumes a zero risk-free rate and uses sample standard deviation.
    """
    std = returns.std()
    equity = equity_curve(returns)
    return {
        "Return": (1 + returns.fillna(0)).prod() - 1,
        "Volatility": std * np.sqrt(TRADING_DAYS),
        "Sharpe": (returns.mean() / std * np.sqrt(TRADING_DAYS)
                   if pd.notna(std) and std > 0 else np.nan),
        "Max Drawdown": (equity / equity.cummax() - 1).min(),
    }


def performance(data):
    """Compare market and net strategy returns, keeping original row order."""
    if data.empty:
        raise ValueError("Cannot evaluate an empty period; check the split date.")
    market = return_metrics(data["Market_Return"])
    strategy = return_metrics(data["Net_Strategy_Return"])
    return {
        f"{label} {metric}": metrics[metric]
        for metric in market
        for label, metrics in (("Market", market), ("Strategy", strategy))
    }


def split_data(data, split_date=SPLIT_DATE):
    """Slice the continuous backtest; carry positions/returns across the boundary."""
    train = data.loc[data.index < split_date].copy()
    test = data.loc[data.index >= split_date].copy()
    if train.empty or test.empty:
        raise ValueError("The split must leave nonempty Train and Test periods.")
    return train, test


def plot_equity(data, title):
    """Recompute equity within each period rather than slice full-period equity."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(equity_curve(data["Market_Return"]), label="Buy & Hold")
    ax.plot(equity_curve(data["Net_Strategy_Return"]), label="RSI Strategy")
    ax.set(title=title, xlabel="Date", ylabel="Growth of $1")
    ax.legend()
    ax.grid()
    fig.tight_layout()
    return fig, ax


def main():
    df = backtest(download_prices())
    train, test = split_data(df)
    results = pd.DataFrame({"Train": performance(train), "Test": performance(test)})
    print(results)  # Numeric values, without percentage/string conversion.
    plot_equity(test, "Out-of-Sample Test: RSI Strategy vs Buy & Hold")
    plot_equity(train, "In-Sample Train: RSI Strategy vs Buy & Hold")
    plt.show()
    return df, results


if __name__ == "__main__":
    main()
