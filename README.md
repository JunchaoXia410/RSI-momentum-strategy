# RSI Strategy Backtest

A Python backtesting project that implements and evaluates a simple **RSI momentum strategy with a 200-day moving average trend filter**.

The strategy is tested on historical stock price data downloaded from Yahoo Finance and compared against a buy-and-hold benchmark.

## Strategy Logic

The strategy combines the **14-day Relative Strength Index (RSI)** with the **200-day Moving Average (MA200)**.

### Entry Signal

Enter a long position when:

- RSI crosses **above 50**
- The stock price is **above its 200-day moving average**

### Exit Signal

Exit the position when:

- RSI crosses **below 40**, or
- The stock price falls **below its 200-day moving average**

The strategy only takes long positions and otherwise stays in cash.

A one-day shift is applied to the trading position to avoid look-ahead bias. This means a signal generated using today's market data is executed starting on the next trading day.

## Default Settings

```python
TICKER = "DELL"
START_DATE = "2020-09-01"
END_DATE = "2026-09-01"
SPLIT_DATE = "2025-09-01"
TRANSACTION_COST = 0.001
TRADING_DAYS = 252
```

The dataset is divided into:

- **Train Period:** Before September 1, 2025
- **Test Period:** September 1, 2025 and after

This allows the strategy to be evaluated on both in-sample and out-of-sample data.

## Project Structure

```text
RSI_Strategy_clean.py
README.md
```

## Main Functions

### `download_prices()`

Downloads historical stock price data from Yahoo Finance using `yfinance`.

```python
download_prices(ticker, start, end)
```

The strategy uses adjusted closing prices to account for stock splits and dividends.

---

### `add_indicators()`

Calculates:

- 14-day RSI
- 200-day Moving Average

```python
add_indicators(data)
```

Rows without enough historical observations to calculate the indicators are removed.

---

### `generate_positions()`

Generates entry and exit signals according to the strategy rules and constructs the trading position.

```python
generate_positions(data)
```

The final `Trade_Position` is shifted by one day to prevent look-ahead bias.

---

### `calculate_returns()`

Calculates:

- Buy-and-hold market returns
- Strategy returns
- Transaction costs
- Net strategy returns
- Equity curves

```python
calculate_returns(data, transaction_cost)
```

Transaction costs are charged whenever the strategy changes its position.

---

### `backtest()`

Runs the complete trading strategy on a price dataset.

```python
backtest(prices)
```

This function combines indicator calculation, signal generation, position construction, and return calculation.

---

### `return_metrics()`

Calculates the main performance statistics:

- Total Return
- Annualized Volatility
- Sharpe Ratio
- Maximum Drawdown

```python
return_metrics(returns)
```

The Sharpe ratio assumes a zero risk-free rate.

---

### `performance()`

Compares the performance of the RSI strategy against the buy-and-hold benchmark.

```python
performance(data)
```

Example output metrics include:

```text
Market Return
Strategy Return
Market Volatility
Strategy Volatility
Market Sharpe
Strategy Sharpe
Market Max Drawdown
Strategy Max Drawdown
```

---

### `split_data()`

Divides the backtest into training and testing periods.

```python
split_data(data, split_date)
```

The strategy itself is calculated continuously before the dataset is split, so existing positions can carry across the train/test boundary.

---

### `plot_equity()`

Plots the growth of $1 invested in:

- Buy & Hold
- RSI Strategy

```python
plot_equity(data, title)
```

This makes it easier to visually compare cumulative performance and drawdowns.

## Installation

Install the required Python packages:

```bash
pip install numpy pandas yfinance matplotlib TA-Lib
```

Required libraries:

```text
numpy
pandas
yfinance
TA-Lib
matplotlib
```

## Running the Backtest

Run the script from the terminal:

```bash
python RSI_Strategy_clean.py
```

The program will:

1. Download historical stock prices
2. Calculate RSI and MA200
3. Generate trading signals
4. Backtest the strategy
5. Split the results into Train and Test periods
6. Calculate performance metrics
7. Print the performance comparison
8. Plot strategy and buy-and-hold equity curves

## Example Workflow

```python
prices = download_prices()

df = backtest(prices)

train, test = split_data(df)

train_results = performance(train)
test_results = performance(test)

plot_equity(test, "Out-of-Sample Test")
```

Because the functions are separated from `main()`, they can also be imported and reused in another Python script or Jupyter Notebook.

## Customization

The strategy can easily be tested on another stock by changing:

```python
TICKER = "AAPL"
```

You can also modify:

```python
START_DATE
END_DATE
SPLIT_DATE
TRANSACTION_COST
```

The RSI thresholds and moving-average period can also be changed inside `add_indicators()` and `generate_positions()` to test alternative strategy specifications.

## Performance Evaluation

The strategy is evaluated using four metrics:

### Total Return

Measures cumulative investment return over the selected period.

### Annualized Volatility

Measures the annualized standard deviation of daily returns.

### Sharpe Ratio

Measures return relative to volatility:

```text
Sharpe Ratio = Mean Daily Return / Daily Volatility × √252
```

A zero risk-free rate is assumed.

### Maximum Drawdown

Measures the largest percentage decline from a previous equity peak.

## Notes

This project is designed for educational and quantitative investment research purposes.

The backtest includes transaction costs but does not model factors such as:

- Bid-ask spreads
- Slippage
- Taxes
- Liquidity constraints
- Market impact

Historical backtest performance does not guarantee future results.

## Technologies

- Python
- Pandas
- NumPy
- Yahoo Finance / yfinance
- TA-Lib
- Matplotlib

## Author

**Junchao Xia**

Duke University  
M.S. in Financial Technology
