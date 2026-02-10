"""
5 年期完整回測報告 (2021/02 - 2026/02)
執行網格交易 V2 和均線交叉策略
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
from datetime import datetime

print("=" * 80)
print("📊 5 年期回測報告 (2021/02 - 2026/02)")
print("=" * 80)
print()

# ==================== 步驟 1: 生成數據 ====================
print("📈 生成 5 年期數據...")

np.random.seed(2021)
periods = 1825 * 24  # 43,800 根K線
dates = pd.date_range(start='2021-02-08', periods=periods, freq='1h')

# 模擬真實 BTC 價格
base_price = 40000
long_trend = np.linspace(0, 45000, periods)
bull_bear_cycle = (
    15000 * np.sin(2 * np.pi * np.arange(periods) / (365 * 24 * 2)) +
    8000 * np.sin(2 * np.pi * np.arange(periods) / (365 * 24 * 4))
)
seasonal = 2000 * np.sin(2 * np.pi * np.arange(periods) / (365 * 24 / 4))
noise = np.random.normal(0, 1200, periods).cumsum()

close_prices = base_price + long_trend + bull_bear_cycle + seasonal + noise
close_prices = np.maximum(close_prices, 10000)

# OHLC
high_prices = close_prices * (1 + np.abs(np.random.normal(0, 0.01, periods)))
low_prices = close_prices * (1 - np.abs(np.random.normal(0, 0.01, periods)))
open_prices = np.roll(close_prices, 1)
open_prices[0] = close_prices[0]
volumes = np.random.lognormal(10, 1, periods)

df = pd.DataFrame({
    'timestamp': dates,
    'open': open_prices,
    'high': high_prices,
    'low': low_prices,
    'close': close_prices,
    'volume': volumes
})

# 計算技術指標
df['ma20'] = df['close'].rolling(window=20).mean()
df['ma50'] = df['close'].rolling(window=50).mean()

delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

tr1 = df['high'] - df['low']
tr2 = abs(df['high'] - df['close'].shift(1))
tr3 = abs(df['low'] - df['close'].shift(1))
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
df['atr'] = tr.rolling(window=14).mean()

print(f"✅ 生成 {len(df):,} 根 K 線完成")
print(f"   起始價格: ${df['close'].iloc[100]:,.0f}")
print(f"   結束價格: ${df['close'].iloc[-1]:,.0f}")
print(f"   期間漲幅: {((df['close'].iloc[-1] / df['close'].iloc[100]) - 1) * 100:.2f}%")
print()

# ==================== 步驟 2: 網格策略回測 ====================
print("🔷 執行網格交易 V2 策略...")

initial_capital = 10000
capital_grid = initial_capital
position_grid = 0
trades_grid = []
equity_grid = []

grid_spacing = 0.03
grid_levels = 8
position_size = initial_capital / grid_levels

start_idx = 100
initial_price = df['close'].iloc[start_idx]
volatility = df['atr'].iloc[start_idx:start_idx+168].mean() / initial_price
dynamic_spacing = max(0.02, min(0.04, volatility * 2))

grid_prices = [initial_price * (1 + dynamic_spacing * i) for i in range(-grid_levels//2, grid_levels//2 + 1)]
last_buy_price = None
last_sell_price = None

for i in range(start_idx, len(df)):
    price = df['close'].iloc[i]
    equity_grid.append(capital_grid + position_grid * price)
    
    # 每週重新調整網格
    if i % 168 == 0 and i > start_idx:
        current_volatility = df['atr'].iloc[i-168:i].mean() / price
        dynamic_spacing = max(0.02, min(0.04, current_volatility * 2))
        grid_prices = [price * (1 + dynamic_spacing * j) for j in range(-grid_levels//2, grid_levels//2 + 1)]
    
    # 買入邏輯
    for grid_price in sorted(grid_prices):
        if grid_price < price:
            continue
        if last_buy_price is None or price <= last_buy_price * (1 - dynamic_spacing):
            if capital_grid >= position_size:
                shares = position_size / price
                capital_grid -= position_size
                position_grid += shares
                last_buy_price = price
                last_sell_price = None
                trades_grid.append({
                    'type': 'buy',
                    'price': price,
                    'shares': shares,
                    'capital': capital_grid,
                    'position': position_grid,
                    'timestamp': df['timestamp'].iloc[i]
                })
                break
    
    # 賣出邏輯
    for grid_price in sorted(grid_prices, reverse=True):
        if grid_price > price:
            continue
        if last_sell_price is None or price >= last_sell_price * (1 + dynamic_spacing):
            if position_grid > 0:
                sell_shares = min(position_grid, position_size / price)
                capital_grid += sell_shares * price
                position_grid -= sell_shares
                last_sell_price = price
                last_buy_price = None
                trades_grid.append({
                    'type': 'sell',
                    'price': price,
                    'shares': sell_shares,
                    'capital': capital_grid,
                    'position': position_grid,
                    'timestamp': df['timestamp'].iloc[i]
                })
                break

# 最終平倉
final_price = df['close'].iloc[-1]
if position_grid > 0:
    capital_grid += position_grid * final_price
    position_grid = 0

final_capital_grid = capital_grid
print(f"✅ 網格策略完成: ${final_capital_grid:,.0f} ({len(trades_grid)} 筆交易)")
print()

# ==================== 步驟 3: 均線策略回測 ====================
print("🔶 執行均線交叉 MA20/50 策略...")

capital_ma = initial_capital
position_ma = 0
trades_ma = []
equity_ma = []

for i in range(len(df)):
    price = df['close'].iloc[i]
    equity_ma.append(capital_ma + position_ma * price)
    
    if i < 50 or pd.isna(df['ma20'].iloc[i]) or pd.isna(df['ma50'].iloc[i]):
        continue
    
    ma20_curr = df['ma20'].iloc[i]
    ma50_curr = df['ma50'].iloc[i]
    ma20_prev = df['ma20'].iloc[i-1]
    ma50_prev = df['ma50'].iloc[i-1]
    
    # 黃金交叉 - 買入
    if ma20_prev <= ma50_prev and ma20_curr > ma50_curr:
        if position_ma == 0 and capital_ma > 0:
            shares = capital_ma / price
            position_ma = shares
            capital_ma = 0
            trades_ma.append({
                'type': 'buy',
                'price': price,
                'shares': shares,
                'timestamp': df['timestamp'].iloc[i]
            })
    
    # 死亡交叉 - 賣出
    elif ma20_prev >= ma50_prev and ma20_curr < ma50_curr:
        if position_ma > 0:
            capital_ma = position_ma * price
            position_ma = 0
            trades_ma.append({
                'type': 'sell',
                'price': price,
                'shares': 0,
                'timestamp': df['timestamp'].iloc[i]
            })

# 最終平倉
if position_ma > 0:
    capital_ma = position_ma * final_price
    position_ma = 0

final_capital_ma = capital_ma
print(f"✅ 均線策略完成: ${final_capital_ma:,.0f} ({len(trades_ma)} 筆交易)")
print()

# ==================== 步驟 4: 計算績效指標 ====================
print("📊 計算績效指標...")

def calculate_metrics(final_capital, trades, equity_curve, strategy_name):
    total_return = (final_capital - initial_capital) / initial_capital
    annual_return = (1 + total_return) ** (1/5) - 1
    
    # 交易統計
    buy_trades = [t for t in trades if t['type'] == 'buy']
    
    # 配對交易
    matched_trades = []
    if strategy_name == 'Grid V2':
        buy_queue = []
        for trade in trades:
            if trade['type'] == 'buy':
                buy_queue.append(trade)
            elif trade['type'] == 'sell' and len(buy_queue) > 0:
                buy_trade = buy_queue.pop(0)
                profit = (trade['price'] - buy_trade['price']) * min(trade['shares'], buy_trade['shares'])
                matched_trades.append({'profit': profit})
    else:  # MA Crossover
        for i in range(0, len(trades)-1, 2):
            if i+1 < len(trades) and trades[i]['type'] == 'buy' and trades[i+1]['type'] == 'sell':
                profit = (trades[i+1]['price'] - trades[i]['price']) * trades[i]['shares']
                matched_trades.append({'profit': profit})
    
    winning_trades = [t for t in matched_trades if t['profit'] > 0]
    losing_trades = [t for t in matched_trades if t['profit'] < 0]
    
    win_rate = len(winning_trades) / len(matched_trades) if matched_trades else 0
    avg_win = np.mean([t['profit'] for t in winning_trades]) if winning_trades else 0
    avg_loss = np.mean([t['profit'] for t in losing_trades]) if losing_trades else 0
    
    # 風險指標
    equity_series = pd.Series(equity_curve)
    returns = equity_series.pct_change().dropna()
    
    running_max = equity_series.expanding().max()
    drawdown = (equity_series - running_max) / running_max
    max_drawdown = drawdown.min()
    
    excess_returns = returns - (0.03 / (365 * 24))
    sharpe = np.sqrt(365 * 24) * excess_returns.mean() / returns.std() if returns.std() > 0 else 0
    
    return {
        'total_return': total_return,
        'annual_return': annual_return,
        'final_capital': final_capital,
        'total_trades': len(trades),
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'max_drawdown': max_drawdown,
        'sharpe': sharpe
    }

metrics_grid = calculate_metrics(final_capital_grid, trades_grid, equity_grid, 'Grid V2')
metrics_ma = calculate_metrics(final_capital_ma, trades_ma, equity_ma, 'MA Crossover')

print("✅ 績效計算完成")
print()

# ==================== 步驟 5: 生成報告 ====================
print("=" * 80)
print("🏆 5 年期回測績效報告")
print("=" * 80)
print()

print("【網格交易 V2】")
print(f"  總收益率: {metrics_grid['total_return']*100:.2f}%")
print(f"  年化收益: {metrics_grid['annual_return']*100:.2f}%")
print(f"  最終淨值: ${metrics_grid['final_capital']:,.0f}")
print(f"  最大回撤: {metrics_grid['max_drawdown']*100:.2f}%")
print(f"  夏普比率: {metrics_grid['sharpe']:.2f}")
print(f"  勝率: {metrics_grid['win_rate']*100:.2f}%")
print(f"  交易次數: {metrics_grid['total_trades']:,}")
print()

print("【均線交叉 MA20/50】")
print(f"  總收益率: {metrics_ma['total_return']*100:.2f}%")
print(f"  年化收益: {metrics_ma['annual_return']*100:.2f}%")
print(f"  最終淨值: ${metrics_ma['final_capital']:,.0f}")
print(f"  最大回撤: {metrics_ma['max_drawdown']*100:.2f}%")
print(f"  夏普比率: {metrics_ma['sharpe']:.2f}")
print(f"  勝率: {metrics_ma['win_rate']*100:.2f}%")
print(f"  交易次數: {metrics_ma['total_trades']:,}")
print()

# 保存 JSON 報告
report = {
    'period': '2021-02-08 to 2026-02-06 (5 years)',
    'initial_capital': initial_capital,
    'market_performance': {
        'start_price': float(df['close'].iloc[100]),
        'end_price': float(df['close'].iloc[-1]),
        'return': float((df['close'].iloc[-1] / df['close'].iloc[100]) - 1)
    },
    'grid_v2': {
        'final_capital': float(metrics_grid['final_capital']),
        'total_return': float(metrics_grid['total_return']),
        'annual_return': float(metrics_grid['annual_return']),
        'max_drawdown': float(metrics_grid['max_drawdown']),
        'sharpe': float(metrics_grid['sharpe']),
        'win_rate': float(metrics_grid['win_rate']),
        'trades': metrics_grid['total_trades']
    },
    'ma_crossover': {
        'final_capital': float(metrics_ma['final_capital']),
        'total_return': float(metrics_ma['total_return']),
        'annual_return': float(metrics_ma['annual_return']),
        'max_drawdown': float(metrics_ma['max_drawdown']),
        'sharpe': float(metrics_ma['sharpe']),
        'win_rate': float(metrics_ma['win_rate']),
        'trades': metrics_ma['total_trades']
    }
}

with open('tmp/backtest_5year_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print("💾 報告已保存: tmp/backtest_5year_report.json")
print()

# ==================== 步驟 6: 生成圖表 ====================
print("📊 生成視覺化圖表...")

fig, axes = plt.subplots(3, 1, figsize=(16, 12))
fig.suptitle('5-Year Backtesting Report (2021-2026)', fontsize=16, fontweight='bold')

# 圖1: BTC 價格與均線
ax1 = axes[0]
sample_indices = range(0, len(df), 24)  # 每天採樣1次
sampled_dates = df['timestamp'].iloc[sample_indices]
ax1.plot(sampled_dates, df['close'].iloc[sample_indices], label='BTC Price', linewidth=1, alpha=0.7)
ax1.plot(sampled_dates, df['ma20'].iloc[sample_indices], label='MA20', linewidth=1, alpha=0.6)
ax1.plot(sampled_dates, df['ma50'].iloc[sample_indices], label='MA50', linewidth=1, alpha=0.6)
ax1.set_ylabel('Price (USD)', fontsize=10)
ax1.set_title('BTC Price & Moving Averages', fontsize=12, fontweight='bold')
ax1.legend(loc='upper left', fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# 圖2: 資金曲線對比
ax2 = axes[1]
sampled_equity_grid = [equity_grid[i] for i in sample_indices if i < len(equity_grid)]
sampled_equity_ma = [equity_ma[i] for i in sample_indices if i < len(equity_ma)]
sampled_dates_equity = sampled_dates[:len(sampled_equity_grid)]

ax2.plot(sampled_dates_equity, sampled_equity_grid, label='Grid V2', linewidth=2, color='#2ecc71')
ax2.plot(sampled_dates_equity, sampled_equity_ma, label='MA Crossover', linewidth=2, color='#3498db')
ax2.axhline(y=initial_capital, color='red', linestyle='--', alpha=0.5, label='Initial Capital')
ax2.set_ylabel('Equity (USD)', fontsize=10)
ax2.set_title('Equity Curve Comparison', fontsize=12, fontweight='bold')
ax2.legend(loc='upper left', fontsize=9)
ax2.grid(True, alpha=0.3)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# 圖3: 績效對比
ax3 = axes[2]
categories = ['Total Return', 'Annual Return', 'Max Drawdown', 'Sharpe Ratio', 'Win Rate']
grid_values = [
    metrics_grid['total_return'] * 100,
    metrics_grid['annual_return'] * 100,
    metrics_grid['max_drawdown'] * 100,
    metrics_grid['sharpe'] * 10,  # 縮放以便顯示
    metrics_grid['win_rate'] * 100
]
ma_values = [
    metrics_ma['total_return'] * 100,
    metrics_ma['annual_return'] * 100,
    metrics_ma['max_drawdown'] * 100,
    metrics_ma['sharpe'] * 10,
    metrics_ma['win_rate'] * 100
]

x = np.arange(len(categories))
width = 0.35

bars1 = ax3.bar(x - width/2, grid_values, width, label='Grid V2', color='#2ecc71', alpha=0.8)
bars2 = ax3.bar(x + width/2, ma_values, width, label='MA Crossover', color='#3498db', alpha=0.8)

ax3.set_ylabel('Value (%)', fontsize=10)
ax3.set_title('Performance Metrics Comparison', fontsize=12, fontweight='bold')
ax3.set_xticks(x)
ax3.set_xticklabels(categories, rotation=15, ha='right', fontsize=9)
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3, axis='y')
ax3.axhline(y=0, color='black', linewidth=0.8)

# 標註數值
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax3.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=7)

plt.tight_layout()
plt.savefig('tmp/backtest_5year_results.png', dpi=150, bbox_inches='tight')
print("✅ 圖表已保存: tmp/backtest_5year_results.png")
print()

print("=" * 80)
print("✅ 5 年期回測完成！")
print("=" * 80)
