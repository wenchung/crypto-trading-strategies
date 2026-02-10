"""
Monitoring and Alert System - 監控與警報系統
追蹤交易狀態並發送警報通知
"""

import logging
from datetime import datetime
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)


class TradingMonitor:
    """
    交易監控系統
    
    功能:
    - 交易執行監控
    - 風險狀態追蹤
    - 異常檢測
    - Email 警報通知
    """
    
    def __init__(self, config: Dict):
        """
        初始化監控系統
        
        Args:
            config: 監控配置
        """
        self.config = config
        self.enable_email = config.get('enable_email_alerts', False)
        self.alert_email = config.get('alert_email', '')
        
        # 警報設定
        self.alert_on_trade = config.get('alert_on_trade', True)
        self.alert_on_error = config.get('alert_on_error', True)
        self.alert_on_daily_loss = config.get('alert_on_daily_loss', True)
        self.alert_on_circuit_breaker = config.get('alert_on_circuit_breaker', True)
        
        # 統計數據
        self.alerts_sent = 0
        self.last_alert_time = None
        
        logger.info("監控系統初始化完成")
    
    def log_trade(self, trade_info: Dict):
        """
        記錄交易
        
        Args:
            trade_info: 交易信息
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        trade_type = trade_info.get('type', 'unknown')
        
        log_message = f"[{timestamp}] 交易執行: {trade_type.upper()}"
        
        if trade_type == 'buy':
            log_message += f" | 價格: ${trade_info.get('price', 0):.2f}"
            log_message += f" | 數量: {trade_info.get('quantity', 0):.6f}"
            log_message += f" | 成本: ${trade_info.get('cost', 0):.2f}"
        elif trade_type == 'sell':
            log_message += f" | 價格: ${trade_info.get('price', 0):.2f}"
            pnl = trade_info.get('pnl', 0)
            pnl_pct = trade_info.get('pnl_pct', 0)
            if pnl > 0:
                log_message += f" | 獲利: ${pnl:.2f} ({pnl_pct:.2f}%) ✅"
            else:
                log_message += f" | 虧損: ${pnl:.2f} ({pnl_pct:.2f}%) ❌"
        
        logger.info(log_message)
        
        # 發送交易警報
        if self.alert_on_trade:
            self._send_alert(
                subject="交易執行通知",
                message=log_message,
                level='info'
            )
    
    def log_risk_status(self, risk_report: Dict):
        """
        記錄風險狀態
        
        Args:
            risk_report: 風險報告
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        daily_loss_pct = risk_report.get('daily_loss_pct', 0) * 100
        total_pnl = risk_report.get('total_pnl', 0)
        consecutive_losses = risk_report.get('consecutive_losses', 0)
        
        log_message = f"[{timestamp}] 風險狀態:"
        log_message += f" | 當日盈虧: {daily_loss_pct:.2f}%"
        log_message += f" | 總盈虧: ${total_pnl:.2f}"
        log_message += f" | 連續虧損: {consecutive_losses}"
        
        logger.info(log_message)
        
        # 檢查警報條件
        if abs(daily_loss_pct) > 3 and self.alert_on_daily_loss:
            self._send_alert(
                subject="⚠️ 每日盈虧警報",
                message=f"當日盈虧已達 {daily_loss_pct:.2f}%",
                level='warning'
            )
        
        if consecutive_losses >= 2:
            self._send_alert(
                subject="⚠️ 連續虧損警報",
                message=f"已連續虧損 {consecutive_losses} 次",
                level='warning'
            )
    
    def log_circuit_breaker(self, reason: str):
        """
        記錄熔斷事件
        
        Args:
            reason: 熔斷原因
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] 🚨 熔斷機制啟動: {reason}"
        
        logger.error(log_message)
        
        if self.alert_on_circuit_breaker:
            self._send_alert(
                subject="🚨 熔斷機制啟動",
                message=f"交易已暫停\n原因: {reason}\n請檢查系統狀態",
                level='critical'
            )
    
    def log_error(self, error_message: str, error_details: Optional[str] = None):
        """
        記錄錯誤
        
        Args:
            error_message: 錯誤訊息
            error_details: 錯誤詳情
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] ❌ 錯誤: {error_message}"
        
        if error_details:
            log_message += f"\n詳情: {error_details}"
        
        logger.error(log_message)
        
        if self.alert_on_error:
            self._send_alert(
                subject="❌ 系統錯誤通知",
                message=log_message,
                level='error'
            )
    
    def _send_alert(self, subject: str, message: str, level: str = 'info'):
        """
        發送警報 (內部方法)
        
        Args:
            subject: 主題
            message: 訊息內容
            level: 警報等級 (info, warning, error, critical)
        """
        if not self.enable_email or not self.alert_email:
            return
        
        # 防止警報過於頻繁
        if self.last_alert_time:
            time_since_last = (datetime.now() - self.last_alert_time).seconds
            if time_since_last < 60 and level == 'info':  # info 級別最少間隔 1 分鐘
                return
        
        # 格式化訊息
        alert_body = f"""
{message}

---
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
警報等級: {level.upper()}
系統: 加密貨幣自動交易機器人

此為自動發送的警報通知。
"""
        
        # 這裡應該調用 send_email 功能
        # 在實際使用時會與 Nebula 的 send_email 整合
        logger.info(f"📧 發送警報郵件: {subject} -> {self.alert_email}")
        
        self.alerts_sent += 1
        self.last_alert_time = datetime.now()
    
    def generate_daily_report(self, performance_metrics: Dict, risk_report: Dict) -> str:
        """
        生成每日報告
        
        Args:
            performance_metrics: 績效指標
            risk_report: 風險報告
            
        Returns:
            報告文本
        """
        report = []
        report.append("=" * 60)
        report.append("每日交易報告")
        report.append("=" * 60)
        report.append(f"日期: {datetime.now().strftime('%Y-%m-%d')}")
        report.append("")
        
        # 賬戶狀態
        report.append("賬戶狀態:")
        report.append(f"  當前餘額: ${risk_report.get('current_balance', 0):,.2f}")
        report.append(f"  權益: ${risk_report.get('equity', 0):,.2f}")
        report.append(f"  當日盈虧: ${risk_report.get('daily_pnl', 0):.2f} ({risk_report.get('daily_loss_pct', 0)*100:.2f}%)")
        report.append(f"  總盈虧: ${risk_report.get('total_pnl', 0):.2f} ({risk_report.get('total_pnl_pct', 0)*100:.2f}%)")
        report.append("")
        
        # 交易統計
        if performance_metrics:
            report.append("交易統計:")
            report.append(f"  交易次數: {performance_metrics.get('total_trades', 0)}")
            report.append(f"  獲利次數: {performance_metrics.get('winning_trades', 0)}")
            report.append(f"  虧損次數: {performance_metrics.get('losing_trades', 0)}")
            report.append(f"  勝率: {performance_metrics.get('win_rate', 0):.2f}%")
            report.append("")
        
        # 風險狀態
        report.append("風險狀態:")
        report.append(f"  連續虧損: {risk_report.get('consecutive_losses', 0)}")
        report.append(f"  持倉數量: {risk_report.get('open_positions_count', 0)}")
        report.append(f"  總倉位: ${risk_report.get('total_exposure', 0):,.2f}")
        
        if risk_report.get('circuit_breaker_active'):
            report.append(f"  ⚠️ 熔斷狀態: 啟動 ({risk_report.get('circuit_breaker_reason')})")
        else:
            report.append("  ✅ 熔斷狀態: 正常")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def get_monitor_stats(self) -> Dict:
        """
        獲取監控統計
        
        Returns:
            監控統計字典
        """
        return {
            'alerts_sent': self.alerts_sent,
            'last_alert_time': self.last_alert_time.isoformat() if self.last_alert_time else None,
            'email_enabled': self.enable_email,
            'alert_email': self.alert_email,
        }


# 配置日誌格式
def setup_logging(log_file: str = 'logs/trading.log', log_level: str = 'INFO'):
    """
    配置日誌系統
    
    Args:
        log_file: 日誌文件路徑
        log_level: 日誌等級
    """
    import os
    
    # 確保日誌目錄存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 配置日誌格式
    log_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 設置日誌處理器
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("日誌系統初始化完成")


if __name__ == '__main__':
    # 測試監控系統
    setup_logging()
    
    config = {
        'enable_email_alerts': True,
        'alert_email': 'trader@example.com',
        'alert_on_trade': True,
        'alert_on_error': True,
        'alert_on_daily_loss': True,
        'alert_on_circuit_breaker': True,
    }
    
    monitor = TradingMonitor(config)
    
    # 測試交易記錄
    monitor.log_trade({
        'type': 'buy',
        'price': 50000,
        'quantity': 0.1,
        'cost': 5000
    })
    
    # 測試風險狀態
    monitor.log_risk_status({
        'daily_loss_pct': -0.03,
        'total_pnl': 500,
        'consecutive_losses': 2,
        'current_balance': 10500,
        'equity': 10500,
    })
    
    # 測試每日報告
    report = monitor.generate_daily_report(
        performance_metrics={'total_trades': 5, 'winning_trades': 3, 'losing_trades': 2, 'win_rate': 60},
        risk_report={'current_balance': 10500, 'equity': 10500, 'daily_pnl': 500, 
                    'daily_loss_pct': 0.05, 'total_pnl': 500, 'total_pnl_pct': 0.05,
                    'consecutive_losses': 0, 'open_positions_count': 0, 'total_exposure': 0,
                    'circuit_breaker_active': False}
    )
    print("\n" + report)
