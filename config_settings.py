"""
Configuration settings for the trading bot.
複製此文件為 config/settings.py 並修改你的設定。
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================== 交易所設定 ====================
EXCHANGE_CONFIG = {
    'exchange': 'binance',  # 支援: binance, coinbase, kraken 等
    'api_key': os.getenv('EXCHANGE_API_KEY', ''),
    'api_secret': os.getenv('EXCHANGE_API_SECRET', ''),
    'testnet': True,  # ⚠️ 建議先用測試網
}

# ==================== 交易設定 ====================
TRADING_CONFIG = {
    'symbol': 'BTC/USDT',
    'timeframe': '1h',  # 1m, 5m, 15m, 1h, 4h, 1d
    'initial_capital': 1000,  # USDT
    'mode': 'paper',  # paper (紙上交易), backtest (回測), live (實盤)
}

# ==================== 風險管理設定 (最重要!) ====================
RISK_MANAGEMENT = {
    # 倉位控制
    'max_position_size': 0.1,  # 單筆最大10%資金 (新手建議0.05)
    'max_total_exposure': 0.5,  # 總倉位不超過50%
    
    # 止損設定
    'stop_loss_pct': 0.02,  # 單筆止損2% (新手建議0.01)
    'take_profit_pct': 0.04,  # 止盈4% (盈虧比2:1)
    'trailing_stop': True,  # 移動止損
    'trailing_stop_pct': 0.015,  # 移動止損1.5%
    
    # 虧損限制
    'max_daily_loss': 0.05,  # 單日最大虧損5% (觸發即停止交易)
    'max_weekly_loss': 0.10,  # 單週最大虧損10%
    'max_consecutive_losses': 3,  # 連續虧損3次熔斷
    
    # 其他保護
    'min_account_balance': 100,  # 最低保留資金 (USDT)
    'emergency_stop': False,  # 緊急停止開關
}

# ==================== 策略選擇 ====================
STRATEGY_CONFIG = {
    'strategy': 'ma_crossover',  # ma_crossover, rsi_strategy, grid_trading
    
    # 均線交叉策略參數
    'ma_crossover': {
        'fast_period': 20,  # 快線週期
        'slow_period': 50,  # 慢線週期
        'ma_type': 'EMA',  # SMA, EMA, WMA
    },
    
    # RSI 策略參數
    'rsi_strategy': {
        'period': 14,
        'oversold': 30,  # 超賣線
        'overbought': 70,  # 超買線
        'exit_middle': 50,  # 中線出場
    },
    
    # 網格交易參數
    'grid_trading': {
        'grid_levels': 10,  # 網格層數
        'price_range': 0.1,  # 價格區間 ±10%
        'profit_per_grid': 0.01,  # 每格利潤1%
    },
}

# ==================== 回測設定 ====================
BACKTEST_CONFIG = {
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'commission': 0.001,  # 0.1% 手續費
    'slippage': 0.0005,  # 0.05% 滑點
}

# ==================== 監控與警報 ====================
MONITORING_CONFIG = {
    # 日誌設定
    'log_level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
    'log_file': 'logs/trading.log',
    'log_to_console': True,
    
    # Email 警報 (使用 Nebula send_email)
    'enable_email_alerts': True,
    'alert_email': os.getenv('ALERT_EMAIL', 'your-email@example.com'),
    
    # 警報觸發條件
    'alert_on_trade': True,  # 每筆交易
    'alert_on_error': True,  # 錯誤
    'alert_on_daily_loss': True,  # 達到日虧損限制
    'alert_on_circuit_breaker': True,  # 熔斷觸發
    
    # 每日報告
    'daily_report': True,
    'report_time': '20:00',  # 每晚8點
}

# ==================== 數據設定 ====================
DATA_CONFIG = {
    'data_source': 'exchange',  # exchange, csv, database
    'cache_data': True,
    'cache_dir': 'data/cache',
    'historical_days': 365,  # 載入歷史數據天數
}

# ==================== 安全檢查 ====================
def validate_config():
    """驗證配置安全性"""
    warnings = []
    
    # 檢查風險設定
    if RISK_MANAGEMENT['max_position_size'] > 0.2:
        warnings.append("⚠️ 單筆倉位 > 20% 風險過高")
    
    if RISK_MANAGEMENT['stop_loss_pct'] > 0.05:
        warnings.append("⚠️ 止損 > 5% 風險過高")
    
    if RISK_MANAGEMENT['max_daily_loss'] > 0.1:
        warnings.append("⚠️ 日虧損限制 > 10% 風險過高")
    
    # 檢查模式設定
    if TRADING_CONFIG['mode'] == 'live' and EXCHANGE_CONFIG['testnet']:
        warnings.append("⚠️ 實盤模式但使用測試網，請確認")
    
    if TRADING_CONFIG['mode'] == 'live':
        warnings.append("🚨 即將使用實盤模式！請確保已充分測試")
    
    # 檢查 API 設定
    if TRADING_CONFIG['mode'] == 'live' and not EXCHANGE_CONFIG['api_key']:
        warnings.append("❌ 實盤模式但未設定 API Key")
    
    return warnings

# ==================== 顯示配置 ====================
def print_config_summary():
    """打印配置摘要"""
    print("=" * 50)
    print("交易機器人配置摘要")
    print("=" * 50)
    print(f"模式: {TRADING_CONFIG['mode'].upper()}")
    print(f"交易對: {TRADING_CONFIG['symbol']}")
    print(f"時間框架: {TRADING_CONFIG['timeframe']}")
    print(f"策略: {STRATEGY_CONFIG['strategy']}")
    print(f"初始資金: ${TRADING_CONFIG['initial_capital']}")
    print("-" * 50)
    print("風險設定:")
    print(f"  單筆倉位: {RISK_MANAGEMENT['max_position_size']*100}%")
    print(f"  止損: {RISK_MANAGEMENT['stop_loss_pct']*100}%")
    print(f"  日虧損限制: {RISK_MANAGEMENT['max_daily_loss']*100}%")
    print(f"  連續虧損熔斷: {RISK_MANAGEMENT['max_consecutive_losses']}次")
    print("=" * 50)
    
    # 顯示警告
    warnings = validate_config()
    if warnings:
        print("\n⚠️  配置警告:")
        for warning in warnings:
            print(f"  {warning}")
        print()

if __name__ == '__main__':
    print_config_summary()
