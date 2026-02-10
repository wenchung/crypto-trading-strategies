"""
RSI Strategy - RSI 超買超賣策略

原理:
- RSI < 30 (超賣區) → 買入信號 (預期反彈)
- RSI > 70 (超買區) → 賣出信號 (預期回調)
- RSI 回到 50 中線 → 平倉

適用市況: 震盪盤整市場
勝率: 約 45-55%
風險: 強勢趨勢中會持續超買/超賣
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class RSIStrategy:
    """RSI 超買超賣策略"""
    
    def __init__(self, config: Dict):
        """
        初始化策略
        
        Args:
            config: 策略配置
                - period: RSI 週期 (默認 14)
                - oversold: 超賣線 (默認 30)
                - overbought: 超買線 (默認 70)
                - exit_middle: 中線出場 (默認 50)
        """
        self.config = config
        self.period = config.get('period', 14)
        self.oversold = config.get('oversold', 30)
        self.overbought = config.get('overbought', 70)
        self.exit_middle = config.get('exit_middle', 50)
        
        self.last_signal = None
        self.entry_rsi = None
        self.name = 'RSI Strategy'
        
        logger.info(f"初始化 {self.name}: 週期{self.period}, 超賣{self.oversold}, 超買{self.overbought}")
    
    def get_strategy_name(self) -> str:
        return self.name
    
    def get_min_data_length(self) -> int:
        """需要的最小數據長度"""
        return max(self.period * 3, 100)
    
    def calculate_rsi(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        計算 RSI 指標
        
        Args:
            data: OHLCV 數據
            
        Returns:
            包含 RSI 的數據
        """
        df = data.copy()
        
        # 計算價格變化
        delta = df['close'].diff()
        
        # 分離上漲和下跌
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        # 計算 RS 和 RSI
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 計算 RSI 趨勢 (RSI 的移動平均)
        df['rsi_ma'] = df['rsi'].rolling(window=5).mean()
        
        return df
    
    def generate_signal(self, data: pd.DataFrame) -> Tuple[str, float, Dict]:
        """
        生成交易信號
        
        Args:
            data: OHLCV 數據
            
        Returns:
            (信號, 信號強度, 額外信息)
        """
        # 驗證數據
        if data is None or len(data) < self.get_min_data_length():
            logger.warning("數據不足")
            return 'hold', 0.0, {}
        
        # 計算指標
        df = self.calculate_rsi(data)
        
        # 檢查是否有足夠的數據
        if df['rsi'].isna().iloc[-1]:
            logger.warning("RSI 計算失敗")
            return 'hold', 0.0, {}
        
        # 獲取當前和前一個 RSI 值
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        current_rsi = current['rsi']
        prev_rsi = previous['rsi']
        
        # 計算信號強度
        # RSI 離極值越遠，信號越強
        if current_rsi < self.oversold:
            # 超賣區域 - 越低越強
            strength = min(1.0, (self.oversold - current_rsi) / self.oversold + 0.5)
        elif current_rsi > self.overbought:
            # 超買區域 - 越高越強
            strength = min(1.0, (current_rsi - self.overbought) / (100 - self.overbought) + 0.5)
        else:
            strength = 0.5
        
        # 額外信息
        info = {
            'rsi': float(current_rsi),
            'rsi_prev': float(prev_rsi),
            'rsi_ma': float(current['rsi_ma']) if not pd.isna(current['rsi_ma']) else None,
            'price': float(current['close']),
            'oversold_level': self.oversold,
            'overbought_level': self.overbought,
        }
        
        # 生成信號
        signal = 'hold'
        
        # 買入信號: RSI 從下方穿越超賣線
        if prev_rsi < self.oversold and current_rsi >= self.oversold:
            signal = 'long'
            self.last_signal = 'long'
            self.entry_rsi = current_rsi
            logger.info(f"RSI 超賣反彈信號 - 買入 (RSI: {current_rsi:.2f}, 強度: {strength:.2f})")
        
        # 賣出信號: RSI 從上方穿越超買線
        elif prev_rsi > self.overbought and current_rsi <= self.overbought:
            if self.last_signal == 'long':
                signal = 'close'
                logger.info(f"RSI 超買回調信號 - 賣出 (RSI: {current_rsi:.2f}, 強度: {strength:.2f})")
            self.last_signal = 'close'
        
        # 中線出場: RSI 回到中線
        elif self.last_signal == 'long' and current_rsi >= self.exit_middle:
            # 如果是從超賣區買入，RSI 回到中線就出場
            if self.entry_rsi and self.entry_rsi < self.oversold:
                signal = 'close'
                logger.info(f"RSI 回歸中線 - 平倉 (RSI: {current_rsi:.2f})")
                self.last_signal = 'close'
        
        # 極端超賣/超買 - 增強信號
        if current_rsi < 20:
            signal = 'long'
            strength = 1.0
            logger.info(f"⚠️ RSI 極度超賣 ({current_rsi:.2f}) - 強烈買入信號")
        elif current_rsi > 80 and self.last_signal == 'long':
            signal = 'close'
            strength = 1.0
            logger.info(f"⚠️ RSI 極度超買 ({current_rsi:.2f}) - 強烈賣出信號")
        
        info['signal_reason'] = self._get_signal_reason(signal, current_rsi)
        
        return signal, strength, info
    
    def _get_signal_reason(self, signal: str, rsi: float) -> str:
        """獲取信號原因說明"""
        if signal == 'long':
            if rsi < 20:
                return f"極度超賣 (RSI: {rsi:.1f})"
            else:
                return f"超賣反彈 (RSI: {rsi:.1f})"
        elif signal == 'close':
            if rsi > 80:
                return f"極度超買 (RSI: {rsi:.1f})"
            elif rsi >= self.overbought:
                return f"超買回調 (RSI: {rsi:.1f})"
            else:
                return f"回歸中線 (RSI: {rsi:.1f})"
        else:
            return f"觀望 (RSI: {rsi:.1f})"
    
    def get_strategy_info(self) -> Dict:
        """返回策略信息"""
        return {
            'name': self.name,
            'type': 'Mean Reversion',
            'period': self.period,
            'oversold': self.oversold,
            'overbought': self.overbought,
            'exit_middle': self.exit_middle,
            '适用市况': '震荡盘整市场',
            '预期胜率': '45-55%',
            '主要风险': '强势趋势中持续超买/超賣',
            '盈亏比': '1.2-1.8',
        }


if __name__ == '__main__':
    # 測試策略
    logging.basicConfig(level=logging.INFO)
    
    # 創建測試數據 (震盪市場)
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1H')
    np.random.seed(42)
    
    # 生成震盪價格
    price = 50000
    prices = [price]
    for i in range(199):
        # 震盪模式: 圍繞中心價格波動
        change = np.random.randn() * 200 + np.sin(i/10) * 500
        price = 50000 + change
        prices.append(price)
    
    test_data = pd.DataFrame({
        'timestamp': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': np.random.randint(100, 1000, 200)
    })
    
    # 測試策略
    config = {
        'period': 14,
        'oversold': 30,
        'overbought': 70,
        'exit_middle': 50
    }
    
    strategy = RSIStrategy(config)
    signal, strength, info = strategy.generate_signal(test_data)
    
    print(f"\n策略信息:")
    for key, value in strategy.get_strategy_info().items():
        print(f"  {key}: {value}")
    
    print(f"\n當前信號: {signal}")
    print(f"信號強度: {strength:.2f}")
    print(f"額外信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
