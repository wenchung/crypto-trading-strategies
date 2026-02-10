"""
Risk Management Module - 風險管理模組
這是交易系統最重要的部分，負責保護你的資金。
"""

from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RiskManager:
    """
    風險管理器 - 控制所有交易風險
    
    主要功能:
    1. 倉位大小計算
    2. 止損/止盈管理
    3. 每日虧損限制
    4. 連續虧損熔斷
    5. 總倉位控制
    """
    
    def __init__(self, config: Dict):
        """
        初始化風險管理器
        
        Args:
            config: 風險管理配置字典
        """
        self.config = config
        
        # 賬戶狀態
        self.initial_balance = 0
        self.current_balance = 0
        self.equity = 0
        
        # 虧損追蹤
        self.daily_start_balance = 0
        self.daily_pnl = 0
        self.last_reset_date = datetime.now().date()
        
        # 連續虧損追蹤
        self.consecutive_losses = 0
        self.max_consecutive_losses = config.get('max_consecutive_losses', 3)
        
        # 熔斷狀態
        self.circuit_breaker_active = False
        self.circuit_breaker_reason = None
        
        # 當前持倉
        self.open_positions = {}
        
        logger.info("風險管理器初始化完成")
    
    def initialize(self, balance: float):
        """
        初始化賬戶餘額
        
        Args:
            balance: 初始餘額
        """
        self.initial_balance = balance
        self.current_balance = balance
        self.equity = balance
        self.daily_start_balance = balance
        logger.info(f"賬戶初始化: ${balance:.2f}")
    
    def update_balance(self, balance: float, equity: float = None):
        """
        更新賬戶餘額
        
        Args:
            balance: 當前可用餘額
            equity: 當前權益 (包含持倉)
        """
        self.current_balance = balance
        self.equity = equity if equity is not None else balance
        
        # 檢查是否需要重置每日統計
        self._check_daily_reset()
    
    def _check_daily_reset(self):
        """檢查並重置每日統計"""
        today = datetime.now().date()
        if today > self.last_reset_date:
            logger.info(f"重置每日統計 - 前日 PnL: ${self.daily_pnl:.2f}")
            self.daily_start_balance = self.current_balance
            self.daily_pnl = 0
            self.last_reset_date = today
            
            # 如果是新的一天，重置熔斷 (可選)
            if self.circuit_breaker_active and 'daily' in self.circuit_breaker_reason.lower():
                self.reset_circuit_breaker()
    
    def calculate_position_size(self, price: float, signal_strength: float = 1.0) -> Tuple[float, float]:
        """
        計算倉位大小
        
        Args:
            price: 當前價格
            signal_strength: 信號強度 (0-1)，影響倉位大小
            
        Returns:
            (交易金額, 數量)
        """
        # 檢查熔斷
        if self.circuit_breaker_active:
            logger.warning(f"熔斷啟動: {self.circuit_breaker_reason}")
            return 0, 0
        
        # 檢查緊急停止
        if self.config.get('emergency_stop', False):
            logger.warning("緊急停止啟動")
            return 0, 0
        
        # 計算可用資金
        available_balance = self.current_balance
        min_balance = self.config.get('min_account_balance', 0)
        
        if available_balance <= min_balance:
            logger.warning(f"餘額不足最低要求: ${available_balance:.2f} <= ${min_balance:.2f}")
            return 0, 0
        
        # 計算最大倉位金額
        max_position_pct = self.config.get('max_position_size', 0.1)
        max_position_amount = available_balance * max_position_pct
        
        # 根據信號強度調整
        position_amount = max_position_amount * signal_strength
        
        # 檢查總倉位限制
        max_total_exposure = self.config.get('max_total_exposure', 0.5)
        current_exposure = self._calculate_total_exposure()
        
        if current_exposure >= max_total_exposure * self.equity:
            logger.warning(f"總倉位已達上限: {current_exposure/self.equity*100:.1f}%")
            return 0, 0
        
        # 計算數量
        quantity = position_amount / price
        
        logger.info(f"計算倉位: ${position_amount:.2f} ({quantity:.6f} @ ${price:.2f})")
        return position_amount, quantity
    
    def calculate_stop_loss(self, entry_price: float, side: str) -> float:
        """
        計算止損價格
        
        Args:
            entry_price: 入場價格
            side: 'long' 或 'short'
            
        Returns:
            止損價格
        """
        stop_loss_pct = self.config.get('stop_loss_pct', 0.02)
        
        if side == 'long':
            stop_loss = entry_price * (1 - stop_loss_pct)
        else:  # short
            stop_loss = entry_price * (1 + stop_loss_pct)
        
        logger.info(f"止損設定: ${stop_loss:.2f} ({side}, {stop_loss_pct*100}%)")
        return stop_loss
    
    def calculate_take_profit(self, entry_price: float, side: str) -> float:
        """
        計算止盈價格
        
        Args:
            entry_price: 入場價格
            side: 'long' 或 'short'
            
        Returns:
            止盈價格
        """
        take_profit_pct = self.config.get('take_profit_pct', 0.04)
        
        if side == 'long':
            take_profit = entry_price * (1 + take_profit_pct)
        else:  # short
            take_profit = entry_price * (1 - take_profit_pct)
        
        logger.info(f"止盈設定: ${take_profit:.2f} ({side}, {take_profit_pct*100}%)")
        return take_profit
    
    def check_trade_allowed(self) -> Tuple[bool, Optional[str]]:
        """
        檢查是否允許交易
        
        Returns:
            (是否允許, 拒絕原因)
        """
        # 檢查熔斷
        if self.circuit_breaker_active:
            return False, f"熔斷啟動: {self.circuit_breaker_reason}"
        
        # 檢查緊急停止
        if self.config.get('emergency_stop', False):
            return False, "緊急停止已啟動"
        
        # 檢查餘額
        min_balance = self.config.get('min_account_balance', 0)
        if self.current_balance <= min_balance:
            return False, f"餘額不足: ${self.current_balance:.2f}"
        
        # 檢查每日虧損限制
        max_daily_loss_pct = self.config.get('max_daily_loss', 0.05)
        daily_loss = self.daily_start_balance - self.current_balance
        daily_loss_pct = daily_loss / self.daily_start_balance if self.daily_start_balance > 0 else 0
        
        if daily_loss_pct >= max_daily_loss_pct:
            reason = f"達到每日虧損限制: {daily_loss_pct*100:.2f}%"
            self._activate_circuit_breaker(reason)
            return False, reason
        
        return True, None
    
    def record_trade_result(self, pnl: float, is_win: bool):
        """
        記錄交易結果
        
        Args:
            pnl: 損益金額
            is_win: 是否獲利
        """
        self.daily_pnl += pnl
        
        # 更新連續虧損
        if is_win:
            self.consecutive_losses = 0
            logger.info(f"獲利交易: ${pnl:.2f}")
        else:
            self.consecutive_losses += 1
            logger.warning(f"虧損交易: ${pnl:.2f} (連續虧損: {self.consecutive_losses})")
            
            # 檢查連續虧損熔斷
            if self.consecutive_losses >= self.max_consecutive_losses:
                reason = f"連續虧損 {self.consecutive_losses} 次"
                self._activate_circuit_breaker(reason)
    
    def _activate_circuit_breaker(self, reason: str):
        """
        啟動熔斷機制
        
        Args:
            reason: 熔斷原因
        """
        self.circuit_breaker_active = True
        self.circuit_breaker_reason = reason
        logger.error(f"🚨 熔斷機制啟動: {reason}")
    
    def reset_circuit_breaker(self):
        """重置熔斷機制"""
        if self.circuit_breaker_active:
            logger.info(f"重置熔斷: {self.circuit_breaker_reason}")
            self.circuit_breaker_active = False
            self.circuit_breaker_reason = None
    
    def _calculate_total_exposure(self) -> float:
        """計算總倉位暴露"""
        total = sum(pos.get('value', 0) for pos in self.open_positions.values())
        return total
    
    def add_position(self, symbol: str, side: str, quantity: float, entry_price: float):
        """
        添加持倉記錄
        
        Args:
            symbol: 交易對
            side: 'long' 或 'short'
            quantity: 數量
            entry_price: 入場價格
        """
        self.open_positions[symbol] = {
            'side': side,
            'quantity': quantity,
            'entry_price': entry_price,
            'value': quantity * entry_price,
            'stop_loss': self.calculate_stop_loss(entry_price, side),
            'take_profit': self.calculate_take_profit(entry_price, side),
            'timestamp': datetime.now()
        }
        logger.info(f"添加持倉: {symbol} {side} {quantity} @ ${entry_price:.2f}")
    
    def remove_position(self, symbol: str):
        """移除持倉記錄"""
        if symbol in self.open_positions:
            del self.open_positions[symbol]
            logger.info(f"移除持倉: {symbol}")
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """獲取持倉信息"""
        return self.open_positions.get(symbol)
    
    def get_risk_report(self) -> Dict:
        """
        生成風險報告
        
        Returns:
            風險狀態字典
        """
        daily_loss = self.daily_start_balance - self.current_balance
        daily_loss_pct = daily_loss / self.daily_start_balance if self.daily_start_balance > 0 else 0
        
        total_pnl = self.current_balance - self.initial_balance
        total_pnl_pct = total_pnl / self.initial_balance if self.initial_balance > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'current_balance': self.current_balance,
            'equity': self.equity,
            'daily_pnl': self.daily_pnl,
            'daily_loss_pct': daily_loss_pct,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'consecutive_losses': self.consecutive_losses,
            'circuit_breaker_active': self.circuit_breaker_active,
            'circuit_breaker_reason': self.circuit_breaker_reason,
            'open_positions_count': len(self.open_positions),
            'total_exposure': self._calculate_total_exposure(),
        }


if __name__ == '__main__':
    # 測試風險管理器
    logging.basicConfig(level=logging.INFO)
    
    config = {
        'max_position_size': 0.1,
        'stop_loss_pct': 0.02,
        'take_profit_pct': 0.04,
        'max_daily_loss': 0.05,
        'max_consecutive_losses': 3,
        'min_account_balance': 100,
    }
    
    rm = RiskManager(config)
    rm.initialize(1000)
    
    # 測試倉位計算
    amount, qty = rm.calculate_position_size(50000)
    print(f"建議倉位: ${amount:.2f}, 數量: {qty:.6f}")
    
    # 測試止損/止盈
    stop = rm.calculate_stop_loss(50000, 'long')
    take = rm.calculate_take_profit(50000, 'long')
    print(f"止損: ${stop:.2f}, 止盈: ${take:.2f}")
    
    # 測試風險報告
    report = rm.get_risk_report()
    print("\n風險報告:")
    for key, value in report.items():
        print(f"  {key}: {value}")
