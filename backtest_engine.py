"""
Backtesting Engine - 回測引擎
用於測試交易策略的歷史表現
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    回測引擎
    
    功能:
    - 歷史數據回測
    - 績效指標計算
    - 交易記錄追蹤
    """
    
    def __init__(self, initial_capital: float, commission: float = 0.001, slippage: float = 0.0005):
        """
        初始化回測引擎
        
        Args:
            initial_capital: 初始資金
            commission: 手續費率 (默認 0.1%)
            slippage: 滑點 (默認 0.05%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        # 賬戶狀態
        self.capital = initial_capital
        self.position = 0  # 持倉數量
        self.position_value = 0
        self.entry_price = 0
        
        # 交易記錄
        self.trades = []
        self.equity_curve = []
        
        # 績效統計
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        logger.info(f"回測引擎初始化: 初始資金 ${initial_capital:,.2f}")
    
    def execute_trade(self, timestamp: datetime, signal: str, price: float, 
                     quantity: float, strategy_info: Dict = None):
        """
        執行交易
        
        Args:
            timestamp: 時間戳
            signal: 交易信號 (long, close)
            price: 交易價格
            quantity: 交易數量
            strategy_info: 策略信息
        """
        # 計算實際成交價 (考慮滑點)
        if signal == 'long':
            execution_price = price * (1 + self.slippage)
        else:  # close
            execution_price = price * (1 - self.slippage)
        
        # 買入
        if signal == 'long' and self.position == 0:
            cost = execution_price * quantity
            fee = cost * self.commission
            total_cost = cost + fee
            
            if total_cost <= self.capital:
                self.position = quantity
                self.entry_price = execution_price
                self.capital -= total_cost
                self.position_value = cost
                
                trade = {
                    'timestamp': timestamp,
                    'type': 'buy',
                    'price': execution_price,
                    'quantity': quantity,
                    'cost': total_cost,
                    'fee': fee,
                    'capital': self.capital,
                    'strategy_info': strategy_info
                }
                self.trades.append(trade)
                logger.info(f"買入: {quantity:.6f} @ ${execution_price:.2f} (費用: ${fee:.2f})")
        
        # 賣出
        elif signal == 'close' and self.position > 0:
            revenue = execution_price * self.position
            fee = revenue * self.commission
            net_revenue = revenue - fee
            
            pnl = net_revenue - (self.entry_price * self.position + self.entry_price * self.position * self.commission)
            pnl_pct = (pnl / (self.entry_price * self.position)) * 100
            
            self.capital += net_revenue
            
            trade = {
                'timestamp': timestamp,
                'type': 'sell',
                'price': execution_price,
                'quantity': self.position,
                'revenue': net_revenue,
                'fee': fee,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'capital': self.capital,
                'entry_price': self.entry_price,
                'strategy_info': strategy_info
            }
            self.trades.append(trade)
            
            # 更新統計
            self.total_trades += 1
            if pnl > 0:
                self.winning_trades += 1
                logger.info(f"✅ 獲利賣出: ${pnl:.2f} ({pnl_pct:.2f}%)")
            else:
                self.losing_trades += 1
                logger.warning(f"❌ 虧損賣出: ${pnl:.2f} ({pnl_pct:.2f}%)")
            
            self.position = 0
            self.entry_price = 0
            self.position_value = 0
    
    def update_equity(self, timestamp: datetime, current_price: float):
        """
        更新權益曲線
        
        Args:
            timestamp: 時間戳
            current_price: 當前價格
        """
        if self.position > 0:
            position_value = self.position * current_price
        else:
            position_value = 0
        
        total_equity = self.capital + position_value
        
        self.equity_curve.append({
            'timestamp': timestamp,
            'capital': self.capital,
            'position_value': position_value,
            'total_equity': total_equity
        })
    
    def get_performance_metrics(self) -> Dict:
        """
        計算績效指標
        
        Returns:
            績效指標字典
        """
        if not self.trades:
            return {'error': '無交易記錄'}
        
        # 基本指標
        final_capital = self.capital
        total_return = final_capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        # 勝率
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        # 盈虧統計
        sell_trades = [t for t in self.trades if t['type'] == 'sell']
        if sell_trades:
            profits = [t['pnl'] for t in sell_trades if t['pnl'] > 0]
            losses = [t['pnl'] for t in sell_trades if t['pnl'] < 0]
            
            avg_profit = np.mean(profits) if profits else 0
            avg_loss = np.mean(losses) if losses else 0
            
            # 盈虧比
            profit_factor = abs(sum(profits) / sum(losses)) if losses else float('inf')
            
            # 最大單筆盈虧
            max_profit = max(profits) if profits else 0
            max_loss = min(losses) if losses else 0
        else:
            avg_profit = avg_loss = profit_factor = max_profit = max_loss = 0
        
        # 最大回撤
        if self.equity_curve:
            equity_series = pd.Series([e['total_equity'] for e in self.equity_curve])
            running_max = equity_series.expanding().max()
            drawdown = (equity_series - running_max) / running_max * 100
            max_drawdown = drawdown.min()
        else:
            max_drawdown = 0
        
        # 夏普比率 (簡化版)
        if len(sell_trades) > 1:
            returns = [t['pnl_pct'] for t in sell_trades]
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': final_capital,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
        }
    
    def print_performance_report(self):
        """打印績效報告"""
        metrics = self.get_performance_metrics()
        
        if 'error' in metrics:
            print(f"錯誤: {metrics['error']}")
            return
        
        print("\n" + "=" * 60)
        print("回測績效報告")
        print("=" * 60)
        print(f"初始資金: ${metrics['initial_capital']:,.2f}")
        print(f"最終資金: ${metrics['final_capital']:,.2f}")
        print(f"總收益: ${metrics['total_return']:,.2f} ({metrics['total_return_pct']:.2f}%)")
        print("-" * 60)
        print(f"交易次數: {metrics['total_trades']}")
        print(f"獲利次數: {metrics['winning_trades']}")
        print(f"虧損次數: {metrics['losing_trades']}")
        print(f"勝率: {metrics['win_rate']:.2f}%")
        print("-" * 60)
        print(f"平均獲利: ${metrics['avg_profit']:.2f}")
        print(f"平均虧損: ${metrics['avg_loss']:.2f}")
        print(f"盈虧比: {metrics['profit_factor']:.2f}")
        print(f"最大單筆獲利: ${metrics['max_profit']:.2f}")
        print(f"最大單筆虧損: ${metrics['max_loss']:.2f}")
        print("-" * 60)
        print(f"最大回撤: {metrics['max_drawdown']:.2f}%")
        print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
        print("=" * 60)
        
        # 評估
        print("\n策略評估:")
        if metrics['win_rate'] >= 50 and metrics['profit_factor'] >= 1.5:
            print("✅ 策略表現良好")
        elif metrics['win_rate'] >= 40 and metrics['profit_factor'] >= 1.2:
            print("⚠️ 策略表現一般，需要優化")
        else:
            print("❌ 策略表現不佳，不建議使用")
        
        if abs(metrics['max_drawdown']) > 30:
            print("⚠️ 警告: 最大回撤超過 30%，風險過高")
        
        if metrics['total_trades'] < 20:
            print("⚠️ 注意: 交易次數較少，結果可能不具代表性")


if __name__ == '__main__':
    # 測試回測引擎
    logging.basicConfig(level=logging.INFO)
    
    engine = BacktestEngine(initial_capital=10000)
    
    # 模擬交易
    timestamps = pd.date_range(start='2024-01-01', periods=10, freq='1D')
    
    # 買入
    engine.execute_trade(timestamps[0], 'long', 50000, 0.1)
    engine.update_equity(timestamps[0], 50000)
    
    # 價格上漲後賣出
    engine.execute_trade(timestamps[5], 'close', 52000, 0)
    engine.update_equity(timestamps[5], 52000)
    
    # 再次買入
    engine.execute_trade(timestamps[6], 'long', 51000, 0.1)
    engine.update_equity(timestamps[6], 51000)
    
    # 價格下跌賣出
    engine.execute_trade(timestamps[9], 'close', 50500, 0)
    engine.update_equity(timestamps[9], 50500)
    
    # 打印報告
    engine.print_performance_report()
