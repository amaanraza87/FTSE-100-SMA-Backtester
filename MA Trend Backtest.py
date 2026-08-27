import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. FETCH HISTORICAL MARKET DATA

TICKER = "^FTSE"
START_DATE = "2015-01-01"
END_DATE = "2025-01-01"

print(f"Fetching market data for {TICKER} ({START_DATE} to {END_DATE})...")
df = yf.download(TICKER, start=START_DATE, end=END_DATE)

# 2. CALCULATE MOVING AVERAGES & STRATEGY SIGNALS

# Calculate 50-day and 200-day Simple Moving Averages
df['SMA_50'] = df['Close'].rolling(window=50).mean()
df['SMA_200'] = df['Close'].rolling(window=200).mean()

# Signal: 1 (Hold Index) when 50 > 200; 0 (Cash) when 50 <= 200
df['Signal'] = np.where(df['SMA_50'] > df['SMA_200'], 1, 0)

# Lag position by 1 day to eliminate lookahead bias
df['Position'] = df['Signal'].shift(1)

# Drop the first 200 warm-up days with empty values
df = df.dropna().copy()

# 3. CALCULATE RETURNS & WEALTH ACCUMULATION

# Daily percentage return of the market
df['Market_Return'] = df['Close'].pct_change().fillna(0)

# Daily return of the strategy (yesterday's position * today's market return)
df['Strategy_Return'] = df['Position'] * df['Market_Return']

# Cumulative compounding starting from £1.00
df['Cumulative_Market'] = (1 + df['Market_Return']).cumprod()
df['Cumulative_Strategy'] = (1 + df['Strategy_Return']).cumprod()

# 4. QUANTITATIVE PERFORMANCE METRICS

trading_days = len(df)
years = trading_days / 252

# CAGR (Compound Annual Growth Rate)
cagr_market = (df['Cumulative_Market'].iloc[-1]) ** (1 / years) - 1
cagr_strategy = (df['Cumulative_Strategy'].iloc[-1]) ** (1 / years) - 1

# Annualized Volatility
vol_market = df['Market_Return'].std() * np.sqrt(252)
vol_strategy = df['Strategy_Return'].std() * np.sqrt(252)

# Sharpe Ratio (Assuming 0% risk-free rate)
sharpe_market = cagr_market / vol_market
sharpe_strategy = cagr_strategy / vol_strategy

# Maximum Drawdown (Peak to trough decline)
df['Peak_Market'] = df['Cumulative_Market'].cummax()
df['Drawdown_Market'] = (df['Cumulative_Market'] - df['Peak_Market']) / df['Peak_Market']
max_dd_market = df['Drawdown_Market'].min()

df['Peak_Strategy'] = df['Cumulative_Strategy'].cummax()
df['Drawdown_Strategy'] = (df['Cumulative_Strategy'] - df['Peak_Strategy']) / df['Peak_Strategy']
max_dd_strategy = df['Drawdown_Strategy'].min()

# 5. PRINT SUMMARY TABLE TO TERMINAL

print("\n" + "="*58)
print("            FTSE 100 STRATEGY PERFORMANCE SUMMARY")
print("="*58)

metrics_summary = pd.DataFrame({
    'Metric': [
        'Total Cumulative Return', 
        'Annualized Return (CAGR)', 
        'Annualized Volatility', 
        'Sharpe Ratio', 
        'Maximum Drawdown'
    ],
    'Buy & Hold (FTSE 100)': [
        f"{(df['Cumulative_Market'].iloc[-1] - 1)*100:.2f}%",
        f"{cagr_market*100:.2f}%",
        f"{vol_market*100:.2f}%",
        f"{sharpe_market:.2f}",
        f"{max_dd_market*100:.2f}%"
    ],
    '50/200 SMA Strategy': [
        f"{(df['Cumulative_Strategy'].iloc[-1] - 1)*100:.2f}%",
        f"{cagr_strategy*100:.2f}%",
        f"{vol_strategy*100:.2f}%",
        f"{sharpe_strategy:.2f}",
        f"{max_dd_strategy*100:.2f}%"
    ]
})

print(metrics_summary.to_string(index=False))
print("="*58)

# 6. PLOT & SAVE THE PERFORMANCE CHART

plt.figure(figsize=(12, 6))
plt.plot(df.index, df['Cumulative_Market'], label='Buy & Hold (FTSE 100)', color='blue', alpha=0.8)
plt.plot(df.index, df['Cumulative_Strategy'], label='50/200 MA Strategy', color='orange', linewidth=1.5)

plt.title('FTSE 100: Dual Moving Average Crossover vs. Buy & Hold (2015–2024)', fontsize=14)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Growth of £1 Investment', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='upper left', fontsize=11)
plt.tight_layout()

# Save the plot automatically as an image file in your folder
plt.savefig("strategy_performance.png", dpi=300)
print("\nChart saved successfully as 'strategy_performance.png'")

# Display the chart on screen
plt.show()
