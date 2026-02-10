"""
完整的回測示範程式（包含所有策略代碼）
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== 策略類別 ====================

class MACrossoverStrategy:
    """均線交叉策略"""
    
    def __init__(self, config):
        self.fast_period = config.get('fast_period', 20)
        self.slow_period = config.get('slow_period', 50)
    
    def generate_signal(self, data):
        """生成交易信號"""
        df = data.copy()
        
        # 計算均線
        df['ma_fast'] = df['close'].rolling(window=self.fast_period).mean()
        df['ma_slow'] = df['close'].rolling(window=self.slow_period).mean()
        
        # 生成信號
        df['signal'] = 0
        df.loc[df['ma_fast'] > df['ma_slow'], 'signal'] = 1  # 買入
        df.loc[df['ma_fast'] < df['ma_slow'], 'signal'] = -1  # 賣出
        
        return df['signal'].iloc[-1], df


class RSIStrategy:
    """RSI 超買超賣策略"""
    
    def __init__(self, config):
        self.period = config.get('period', 14)
        self.oversold = config.get('oversold', 30)
        self.overbought = config.get('overbought', 70)
    
    def calculate_rsi(self, data, period):
        """計算 RSI"""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signal(self, data):
        """生成交易信號"""
        df = data.copy()
        df['rsi'] = self.calculate_rsi(df, self.period)
        
        # 生成信號
        df['signal'] = 0
        df.loc[df['rsi'] < self.oversold, 'signal'] = 1  # 超賣買入
        df.loc[df['rsi'] > self.overbought, 'signal'] = -1  # 超買賣出
        
        return df['signal'].iloc[-1], df


class GridTradingStrategy:
    """網格交易策略"""
    
    def __init__(self, config):
        self.grid_levels = config.get('grid_levels', 10)
        self.grid_spacing_pct = config.get('grid_spacing_pct', 2.0)
        self.grids = []
        self.last_price = None
    
    def initialize_grids(self, current_price):
        """初始化網格"""
        self.grids = []
        for i in range(self.grid_levels):
            buy_price = current_price * (1 - (i + 1) * self.grid_spacing_pct / 100)
            sell_price = current_price * (1 + (i + 1) * self.grid_spacing_pct / 100)
            self.grids.append({'buy': buy_price, 'sell': sell_price, 'filled': False})
    
    def generate_signal(self, data):
        """生成交易信號"""
        df = data.copy()
        current_price = df['close'].iloc[-1]
        
        if not self.grids or self.last_price is None:
            self.initialize_grids(current_price)
            self.last_price = current_price
            df['signal'] = 0
            return 0, df
        
        # 檢查是否觸發買入網格
        for grid in self.grids:
            if current_price <= grid['buy'] and self.last_price > grid['buy']:
                df['signal'] = 1
                self.last_price = current_price
                return 1, df
        
        # 檢查是否觸發賣出網格
        for grid in self.grids:
            if current_price >= grid['sell'] and self.last_price < grid['sell']:
                df['signal'] = -1
                self.last_price = current_price
                return -1, df
        
        self.last_price = current_price
        df['signal'] = 0
        return 0, df


# ==================== 回測引擎 ====================

class BacktestEngine:
    """回測引擎"""
    
    def __init__(self, initial_capital, commission=0.001, slippage=0.0005):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.reset()
    
    def reset(self):
        """重置回測狀態"""
        self.cash = self.initial_capital
        self.position = 0
        self.equity = self.initial_capital
        self.trades = []
        self.equity_curve = []
    
    def run_backtest(self, data, strategy):
        """執行回測"""
        self.reset()
        df = data.copy()
        
        for i in range(len(df)):
            current_data = df.iloc[:i+1]
            
            if len(current_data) < 50:  # 需要足夠數據計算指標
                self.equity_curve.append(self.initial_capital)
                continue
            
            # 生成信號
            signal, _ = strategy.generate_signal(current_data)
            current_price = df['close'].iloc[i]
            
            # 執行交易
            if signal == 1 and self.position == 0:  # 買入
                cost = current_price * (1 + self.slippage)
                shares = (self.cash * 0.95) / cost  # 使用 95% 資金
                total_cost = shares * cost * (1 + self.commission)
                
                if total_cost <= self.cash:
                    self.position = shares
                    self.cash -= total_cost
                    self.trades.append({
                        'type': 'BUY',
                        'price': cost,
                        'shares': shares,
                        'timestamp': df.index[i]
                    })
            
            elif signal == -1 and self.position > 0:  # 賣出
                sell_price = current_price * (1 - self.slippage)
                total_value = self.position * sell_price * (1 - self.commission)
                
                self.cash += total_value
                self.trades.append({
                    'type': 'SELL',
                    'price': sell_price,
                    'shares': self.position,
                    'timestamp': df.index[i]
                })
                self.position = 0
            
            # 更新權益
            position_value = self.position * current_price if self.position > 0 else 0
            self.equity = self.cash + position_value
            self.equity_curve.append(self.equity)
        
        # 計算績效指標
        return self.calculate_performance(df)
    
    def calculate_performance(self, data):
        """計算績效指標"""
        equity_series = pd.Series(self.equity_curve, index=data.index[:len(self.equity_curve)])
        
        # 基本指標
        total_return = ((self.equity - self.initial_capital) / self.initial_capital) * 100
        
        # 計算年化收益
        days = (data.index[-1] - data.index[0]).days
        years = days / 365.25
        annualized_return = ((self.equity / self.initial_capital) ** (1/years) - 1) * 100 if years > 0 else 0
        
        # 計算夏普比率
        returns = equity_series.pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std() * np.sqrt(365 * 24)) if returns.std() > 0 else 0
        
        # 計算最大回撤
        rolling_max = equity_series.expanding().max()
        drawdown = ((equity_series - rolling_max) / rolling_max) * 100
        max_drawdown = drawdown.min()
        
        # 交易統計
        winning_trades = [t for i, t in enumerate(self.trades[1::2]) 
                         if i < len(self.trades[::2]) and 
                         t['price'] > self.trades[i*2]['price']]
        
        total_trades = len(self.trades) // 2
        winning_count = len(winning_trades)
        win_rate = (winning_count / total_trades * 100) if total_trades > 0 else 0
        
        # 盈虧比
        profit_factor = 0
        if total_trades > 0:
            profits = sum([t['price'] - self.trades[i*2]['price'] 
                          for i, t in enumerate(self.trades[1::2]) 
                          if i < len(self.trades[::2]) and t['price'] > self.trades[i*2]['price']])
            losses = abs(sum([t['price'] - self.trades[i*2]['price'] 
                             for i, t in enumerate(self.trades[1::2]) 
                             if i < len(self.trades[::2]) and t['price'] <= self.trades[i*2]['price']]))
            profit_factor = (profits / losses) if losses > 0 else 0
        
        return {
            'equity_curve': equity_series,
            'drawdown': drawdown,
            'trades': self.trades,
            'performance_metrics': {
                'total_return': total_return,
                'annualized_return': annualized_return,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate,
                'profit_factor': profit_factor,
                'total_trades': total_trades,
                'winning_trades': winning_count,
                'losing_trades': total_trades - winning_count
            }
        }


# ==================== 主程式 ====================

def download_historical_data(symbol='BTC/USDT', timeframe='1h', days=180):
    """下載歷史數據"""
    print(f"📥 正在下載 {symbol} 最近 {days} 天的數據...")
    
    try:
        exchange = ccxt.binance({'enableRateLimit': True})
        since = exchange.parse8601((datetime.now() - timedelta(days=days)).isoformat())
        
        all_ohlcv = []
        current_since = since
        
        while True:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=current_since, limit=1000)
            if not ohlcv:
                break
            all_ohlcv.extend(ohlcv)
            current_since = ohlcv[-1][0] + 1
            if current_since >= exchange.milliseconds():
                break
            print(f"  已下載 {len(all_ohlcv)} 根 K 線...")
        
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        print(f"✅ 成功下載 {len(df)} 根 K 線")
        print(f"   時間範圍: {df.index[0]} 至 {df.index[-1]}")
        print(f"   價格範圍: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        
        return df
    except Exception as e:
        print(f"❌ 下載失敗: {e}")
        return None


def main():
    """主程式"""
    print("="*80)
    print("🚀 加密貨幣交易策略回測系統")
    print("="*80)
    
    # 下載數據
    data = download_historical_data(symbol='BTC/USDT', timeframe='1h', days=180)
    if data is None or len(data) == 0:
        print("❌ 無法取得數據")
        return
    
    # 策略配置
    initial_capital = 10000
    strategies = {
        '均線交叉策略 (MA20/50)': (MACrossoverStrategy, {'fast_period': 20, 'slow_period': 50}),
        'RSI超買超賣策略': (RSIStrategy, {'period': 14, 'oversold': 30, 'overbought': 70}),
        '網格交易策略': (GridTradingStrategy, {'grid_levels': 10, 'grid_spacing_pct': 2.0})
    }
    
    # 執行回測
    results = {}
    for name, (strategy_class, config) in strategies.items():
        print(f"\n{'='*60}")
        print(f"🔄 正在回測: {name}")
        print(f"{'='*60}")
        
        try:
            strategy = strategy_class(config)
            backtest = BacktestEngine(initial_capital, commission=0.001, slippage=0.0005)
            result = backtest.run_backtest(data.copy(), strategy)
            results[name] = result
            
            metrics = result['performance_metrics']
            print(f"\n📊 {name} 回測結果:")
            print(f"總收益率: {metrics['total_return']:.2f}%")
            print(f"年化收益率: {metrics['annualized_return']:.2f}%")
            print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
            print(f"最大回撤: {metrics['max_drawdown']:.2f}%")
            print(f"勝率: {metrics['win_rate']:.2f}%")
            print(f"盈虧比: {metrics['profit_factor']:.2f}")
            print(f"總交易次數: {metrics['total_trades']}")
        except Exception as e:
            print(f"❌ 回測失敗: {e}")
            import traceback
            traceback.print_exc()
    
    # 比較結果
    if results:
        print(f"\n{'='*80}")
        print(f"📈 策略績效比較")
        print(f"{'='*80}")
        
        comparison = []
        for name, result in results.items():
            m = result['performance_metrics']
            comparison.append({
                '策略': name,
                '總收益(%)': f"{m['total_return']:.2f}",
                '年化收益(%)': f"{m['annualized_return']:.2f}",
                '夏普比率': f"{m['sharpe_ratio']:.2f}",
                '最大回撤(%)': f"{m['max_drawdown']:.2f}",
                '勝率(%)': f"{m['win_rate']:.2f}",
                '交易次數': m['total_trades']
            })
        
        df_comp = pd.DataFrame(comparison)
        print(df_comp.to_string(index=False))
        
        # 生成圖表
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        
        # 資金曲線
        colors = ['blue', 'green', 'red']
        for idx, (name, result) in enumerate(results.items()):
            equity = result['equity_curve']
            axes[0].plot(equity.index, equity.values, label=name, color=colors[idx], linewidth=2)
        axes[0].set_title('Equity Curve Comparison', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Portfolio Value (USDT)')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 回撤
        for idx, (name, result) in enumerate(results.items()):
            dd = result['drawdown']
            axes[1].fill_between(dd.index, 0, dd.values, label=name, alpha=0.3, color=colors[idx])
        axes[1].set_title('Drawdown Comparison', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Drawdown (%)')
        axes[1].set_xlabel('Date')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/home/user/files/tmp/backtest_results.png', dpi=150, bbox_inches='tight')
        print(f"\n✅ 圖表已儲存: tmp/backtest_results.png")
        
        # 儲存結果
        output = {
            'backtest_date': datetime.now().isoformat(),
            'comparison': df_comp.to_dict('records')
        }
        with open('/home/user/files/tmp/backtest_summary.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"✅ 結果已儲存: tmp/backtest_summary.json")
    
    print("\n" + "="*80)
    print("✅ 回測完成！")
    print("="*80)


if __name__ == '__main__':
    main()
