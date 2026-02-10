"""
Base Strategy Class - 策略基類
所有交易策略都繼承此類
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """
    策略基類
    
    所有策略必須實作以下方法:
    - generate_signal(): 生成交易信號
    - get_strategy_name(): 返回策略名稱
    """
    
    def __init__(self, config: Dict):
        """
        初始化策略
        
        Args:
            config: 策略配置字典
        """
        self.config = config
        self.name = self.get_strategy_name()
        logger.info(f"初始化策略: {self.name}")
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> Tuple[str, float, Dict]:
        """
        生成交易信號
        
        Args:
            data: OHLCV 數據 DataFrame (包含 open, high, low, close, volume)
        
        Returns:
            (信號, 信號強度, 額外信息)
            信號: 'long' (買入), 'short' (賣出), 'close' (平倉), 'hold' (持有)
            信號強度: 0.0-1.0 (用於調整倉位大小)
            額外信息: 策略相關數據
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """返回策略名稱"""
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        驗證數據完整性
        
        Args:
            data: OHLCV 數據
            
        Returns:
            數據是否有效
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        if data is None or data.empty:
            logger.error("數據為空")
            return False
        
        for col in required_columns:
            if col not in data.columns:
                logger.error(f"缺少必要欄位: {col}")
                return False
        
        if len(data) < self.get_min_data_length():
            logger.error(f"數據長度不足: {len(data)} < {self.get_min_data_length()}")
            return False
        
        return True
    
    def get_min_data_length(self) -> int:
        """
        返回策略所需的最小數據長度
        子類可以覆蓋此方法
        """
        return 100  # 默認需要至少100根K線
    
    def get_strategy_info(self) -> Dict:
        """
        返回策略信息
        
        Returns:
            策略詳細信息字典
        """
        return {
            'name': self.name,
            'config': self.config,
            'min_data_length': self.get_min_data_length(),
        }
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        計算技術指標
        子類應覆蓋此方法來計算特定指標
        
        Args:
            data: 原始 OHLCV 數據
            
        Returns:
            包含指標的數據
        """
        return data


class SignalType:
    """信號類型常量"""
    LONG = 'long'      # 做多/買入
    SHORT = 'short'    # 做空/賣出
    CLOSE = 'close'    # 平倉
    HOLD = 'hold'      # 持有/觀望


class SignalStrength:
    """信號強度常量"""
    WEAK = 0.5
    MODERATE = 0.75
    STRONG = 1.0


if __name__ == '__main__':
    # 測試基類
    print("策略基類定義完成")
    print(f"信號類型: {SignalType.LONG}, {SignalType.SHORT}, {SignalType.CLOSE}, {SignalType.HOLD}")
    print(f"信號強度: 弱({SignalStrength.WEAK}), 中({SignalStrength.MODERATE}), 強({SignalStrength.STRONG})")
