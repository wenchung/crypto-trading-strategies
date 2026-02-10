"""
Moving Average Crossover Strategy - 均線交叉策略

原理:
- 短期均線上穿長期均線 (金叉) → 買入信號
- 短期均線下穿長期均線 (死叉) → 賣出信號

適用市況: 趨勢明確的市場
勝率: 約 40-50%
風險: 震盪市會產生假突破
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class MACrossoverStrategy:
    """均線交叉策略"""
    
    def __init__(self, config: Dict):
        """
        初始化策略
        
        Args:
            config: 策略配置
                - fast_period: 快線週期 (默認 20)
                - slow_period: 慢線週期 (默認 50)
                - ma_type: 均線類型 (SMA, EMA, WMA) (默認 EMA)
        """
        self.config = config
        self.fast_period = config.get('fast_period', 20)
        self.slow_period = config.get('slow_period', 50)
        self.ma_type = config.get('ma_type', 'EMA')
        
        self.last_signal = None
        self.name = 'MA Crossover'
        
        logger.info(f"初始化 {self.name}: 快線{self.fast_period}, 慢線{self.slow_period}, 類型{self.ma_type}")
    
    def get_strategy_name(self) -> str:
        return self.name
    
    def get_min_data_length(self) -> int:
        """需要的最小數據長度"""
        return max(self.slow_period * 2, 100)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        計算均線指標
        
        Args:
            data: OHLCV 數據
            
        Returns:
            包含均線的數據
        """
        df = data.copy()
        
        # 根據類型計算均線
        if self.ma_type == 'SMA':
            df['ma_fast'] = df['close'].rolling(window=self.fast_period).mean()
            df['ma_slow'] = df['close'].rolling(window=self.slow_period).mean()
        elif self.ma_type == 'EMA':
            df['ma_fast'] = df['close'].ewm(span=self.fast_period, adjust=False).mean()
            df['ma_slow'] = df['close'].ewm(span=self.slow_period, adjust=False).mean()
        elif self.ma_type == 'WMA':
            df['ma_fast'] = df['close'].rolling(window=self.fast_period).apply(
                lambda x: np.average(x, weights=np.arange(1, len(x)+1)), raw=True
            )
            df['ma_slow'] = df['close'].rolling(window=self.slow_period).apply(
                lambda x: np.average(x, weights=np.arange(1, len(x)+1)), raw=True
            )
        
        # 計算均線差值
        df['ma_diff'] = df['ma_fast'] - df['ma_slow']
        df['ma_diff_pct'] = (df['ma_diff'] / df['ma_slow']) * 100
        
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
        df = self.calculate_indicators(data)
        
        # 檢查是否有足夠的數據
        if df['ma_fast'].isna().iloc[-1] or df['ma_slow'].isna().iloc[-1]:
            logger.warning("指標計算失敗")
            return 'hold', 0.0, {}
        
        # 獲取最近兩根K線的數據
        current = df.iloc[-1]
        previous = df.iloc[-2]
        
        # 當前狀態
        current_fast = current['ma_fast']
        current_slow = current['ma_slow']
        prev_fast = previous['ma_fast']
        prev_slow = previous['ma_slow']
        
        # 檢測交叉
        golden_cross = prev_fast <= prev_slow and current_fast > current_slow  # 金叉
        death_cross = prev_fast >= prev_slow and current_fast < current_slow   # 死叉
        
        # 計算信號強度 (基於均線差值百分比)
        ma_diff_pct = abs(current['ma_diff_pct'])
        
        # 信號強度: 差值越大，信號越強
        if ma_diff_pct < 0.5:
            strength = 0.5  # 弱信號
        elif ma_diff_pct < 1.0:
            strength = 0.75  # 中等信號
        else:
            strength = 1.0  # 強信號
        
        # 額外信息
        info = {
            'ma_fast': float(current_fast),
            'ma_slow': float(current_slow),
            'ma_diff_pct': float(current['ma_diff_pct']),
            'golden_cross': golden_cross,
            'death_cross': death_cross,
            'price': float(current['close'])
        }
        
        # 生成信號
        if golden_cross:
            signal = 'long'
            self.last_signal = 'long'
            logger.info(f"金叉信號 - 買入 (強度: {strength:.2f}, 差值: {ma_diff_pct:.2f}%)")
        elif death_cross:
            signal = 'close' if self.last_signal == 'long' else 'hold'
            self.last_signal = 'close'
            logger.info(f"死叉信號 - 賣出 (強度: {strength:.2f}, 差值: {ma_diff_pct:.2f}%)")
        else:
            # 持有當前狀態
            signal = 'hold'
            strength = 0.0
        
        return signal, strength, info
    
    def get_strategy_info(self) -> Dict:
        """返回策略信息"""
        return {
            'name': self.name,
            'type': 'Trend Following',
            'fast_period': self.fast_period,
            'slow_period': self.slow_period,
            'ma_type': self.ma_type,
            '适用市况': '趋势明确的市场',
            '预期胜率': '40-50%',
            '主要风险': '震荡市假突破',
            '盈亏比': '1.5-2.0',
        }


if __name__ == '__main__':
    # 測試策略
    logging.basicConfig(level=logging.INFO)
    
    # 創建測試數據
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1H')
    np.random.seed(42)
    
    # 生成模擬價格 (帶趨勢)
    price = 50000
    prices = [price]
    for _ in range(199):
        change = np.random.randn() * 100 + 10  # 帶上升趨勢
        price = price + change
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
        'fast_period': 20,
        'slow_period': 50,
        'ma_type': 'EMA'
    }
    
    strategy = MACrossoverStrategy(config)
    signal, strength, info = strategy.generate_signal(test_data)
    
    print(f"\n策略信息:")
    for key, value in strategy.get_strategy_info().items():
        print(f"  {key}: {value}")
    
    print(f"\n當前信號: {signal}")
    print(f"信號強度: {strength:.2f}")
    print(f"額外信息:")
    for key, value in info.items():
        print(f"  {key}: {value}")
