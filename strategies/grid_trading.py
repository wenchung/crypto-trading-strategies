"""
Grid Trading Strategy - 網格交易策略

原理:
- 在價格區間內設置多層買賣網格
- 每跌一格就買入，每漲一格就賣出
- 低買高賣，賺取震盪利潤

適用市況: 橫盤震盪
勝率: 單筆 60-70%
風險: ⚠️ 單邊突破會導致重大虧損 (只適合震盪市)
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)


class GridTradingStrategy:
    """
    網格交易策略
    
    ⚠️ 警告: 此策略僅適合震盪市場
    單邊突破會造成重大虧損！
    """
    
    def __init__(self, config: Dict):
        """
        初始化策略
        
        Args:
            config: 策略配置
                - grid_levels: 網格層數 (默認 10)
                - price_range: 價格區間百分比 (默認 0.1 = ±10%)
                - profit_per_grid: 每格利潤百分比 (默認 0.01 = 1%)
                - base_price: 基準價格 (可選，默認使用當前價)
        """
        self.config = config
        self.grid_levels = config.get('grid_levels', 10)
        self.price_range = config.get('price_range', 0.1)
        self.profit_per_grid = config.get('profit_per_grid', 0.01)
        self.base_price = config.get('base_price', None)
        
        self.grids = []
        self.grid_positions = {}  # 記錄每個網格的持倉
        self.name = 'Grid Trading'
        
        logger.info(f"初始化 {self.name}: {self.grid_levels}層網格, 區間±{self.price_range*100}%")
    
    def get_strategy_name(self) -> str:
        return self.name
    
    def get_min_data_length(self) -> int:
        """需要的最小數據長度"""
        return 50
    
    def setup_grids(self, current_price: float):
        """
        設置網格
        
        Args:
            current_price: 當前價格
        """
        if self.base_price is None:
            self.base_price = current_price
        
        # 計算價格上下限
        upper_price = self.base_price * (1 + self.price_range)
        lower_price = self.base_price * (1 - self.price_range)
        
        # 計算每格價差
        grid_size = (upper_price - lower_price) / self.grid_levels
        
        # 生成網格價位
        self.grids = []
        for i in range(self.grid_levels + 1):
            grid_price = lower_price + (grid_size * i)
            self.grids.append({
                'level': i,
                'price': grid_price,
                'type': 'buy' if i < self.grid_levels / 2 else 'sell',
            })
        
        logger.info(f"網格設置完成:")
        logger.info(f"  基準價: ${self.base_price:.2f}")
        logger.info(f"  上限: ${upper_price:.2f}")
        logger.info(f"  下限: ${lower_price:.2f}")
        logger.info(f"  網格數: {len(self.grids)}")
        logger.info(f"  每格: ${grid_size:.2f} ({self.profit_per_grid*100}%)")
    
    def find_nearest_grid(self, price: float) -> Dict:
        """
        找到最接近當前價格的網格
        
        Args:
            price: 當前價格
            
        Returns:
            最近的網格信息
        """
        if not self.grids:
            return None
        
        nearest = min(self.grids, key=lambda g: abs(g['price'] - price))
        return nearest
    
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
        
        current = data.iloc[-1]
        current_price = current['close']
        
        # 初始化網格 (首次運行)
        if not self.grids:
            self.setup_grids(current_price)
        
        # 找到當前價格所在網格
        nearest_grid = self.find_nearest_grid(current_price)
        
        # 檢查是否觸及網格邊界 (風險警告)
        upper_limit = self.grids[-1]['price']
        lower_limit = self.grids[0]['price']
        
        risk_warning = None
        if current_price >= upper_limit * 0.95:
            risk_warning = "⚠️ 接近上限 - 可能突破網格！"
        elif current_price <= lower_limit * 1.05:
            risk_warning = "⚠️ 接近下限 - 可能突破網格！"
        
        # 計算價格波動率 (用於判斷市場狀態)
        if len(data) >= 20:
            volatility = data['close'].pct_change().tail(20).std() * 100
        else:
            volatility = 0
        
        # 額外信息
        info = {
            'current_price': float(current_price),
            'base_price': float(self.base_price),
            'nearest_grid_level': nearest_grid['level'] if nearest_grid else None,
            'nearest_grid_price': float(nearest_grid['price']) if nearest_grid else None,
            'upper_limit': float(upper_limit),
            'lower_limit': float(lower_limit),
            'volatility': float(volatility),
            'risk_warning': risk_warning,
            'grid_count': len(self.grids),
        }
        
        # 網格交易邏輯
        signal = 'hold'
        strength = 0.5
        
        # 檢查是否需要買入或賣出
        for i, grid in enumerate(self.grids):
            grid_price = grid['price']
            
            # 價格下穿網格線 → 買入
            if current_price <= grid_price and i not in self.grid_positions:
                # 檢查是否在下半部分網格 (更激進的買入)
                if i < len(self.grids) / 2:
                    signal = 'long'
                    # 越靠近底部，信號越強
                    strength = 0.5 + (0.5 * (1 - i / (len(self.grids) / 2)))
                    self.grid_positions[i] = {
                        'entry_price': current_price,
                        'target_price': grid_price * (1 + self.profit_per_grid)
                    }
                    logger.info(f"觸及網格 {i} - 買入信號 (${grid_price:.2f}, 強度: {strength:.2f})")
                    info['triggered_grid'] = i
                    info['action'] = 'buy'
                    break
            
            # 價格上穿目標價 → 賣出
            elif i in self.grid_positions:
                target_price = self.grid_positions[i]['target_price']
                if current_price >= target_price:
                    signal = 'close'
                    strength = 0.75
                    entry_price = self.grid_positions[i]['entry_price']
                    profit = (current_price - entry_price) / entry_price * 100
                    del self.grid_positions[i]
                    logger.info(f"達到目標價 - 賣出信號 (網格{i}, 利潤: {profit:.2f}%)")
                    info['triggered_grid'] = i
                    info['action'] = 'sell'
                    info['profit_pct'] = profit
                    break
        
        # 風險控制: 價格突破網格範圍
        if current_price > upper_limit:
            signal = 'close'
            strength = 1.0
            logger.error(f"🚨 價格突破上限 (${current_price:.2f} > ${upper_limit:.2f}) - 強制平倉！")
            info['forced_close'] = 'upper_breakout'
        elif current_price < lower_limit:
            signal = 'close'
            strength = 1.0
            logger.error(f"🚨 價格突破下限 (${current_price:.2f} < ${lower_limit:.2f}) - 強制平倉！")
            info['forced_close'] = 'lower_breakout'
        
        # 高波動警告
        if volatility > 5:
            logger.warning(f"⚠️ 高波動市場 (波動率: {volatility:.2f}%) - 網格交易風險增加")
            info['high_volatility_warning'] = True
        
        return signal, strength, info
    
    def reset_grids(self, new_base_price: float = None):
        """
        重置網格
        
        Args:
            new_base_price: 新的基準價格
        """
        logger.info("重置網格")
        self.grids = []
        self.grid_positions = {}
        self.base_price = new_base_price
    
    def get_strategy_info(self) -> Dict:
        """返回策略信息"""
        return {
            'name': self.name,
            'type': 'Range Trading',
            'grid_levels': self.grid_levels,
            'price_range': f"±{self.price_range*100}%",
            'profit_per_grid': f"{self.profit_per_grid*100}%",
            'base_price': self.base_price,
            'active_positions': len(self.grid_positions),
            '适用市况': '横盘震荡 (非常重要!)',
            '预期胜率': '60-70% (单笔)',
            '主要风险': '⚠️ 单边突破会重大亏损',
            '盈亏比': '0.8-1.2 (小赚多次，但怕大跌)',
            '⚠️ 警告': '仅适合震荡市场，趋势市场禁用！',
        }


if __name__ == '__main__':
    # 測試策略
    logging.basicConfig(level=logging.INFO)
    
    # 創建測試數據 (震盪市場)
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1H')
    np.random.seed(42)
    
    # 生成震盪價格 (圍繞 50000 波動)
    base = 50000
    prices = [base + np.sin(i/10) * 2000 + np.random.randn() * 500 for i in range(200)]
    
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
        'grid_levels': 10,
        'price_range': 0.1,
        'profit_per_grid': 0.01,
    }
    
    strategy = GridTradingStrategy(config)
    signal, strength, info = strategy.generate_signal(test_data)
    
    print(f"\n策略信息:")
    for key, value in strategy.get_strategy_info().items():
        print(f"  {key}: {value}")
    
    print(f"\n當前信號: {signal}")
    print(f"信號強度: {strength:.2f}")
    print(f"額外信息:")
    for key, value in info.items():
        if value is not None:
            print(f"  {key}: {value}")
