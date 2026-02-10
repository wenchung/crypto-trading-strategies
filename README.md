# Crypto Trading Strategies

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-AGPLv3-blue.svg)](LICENSE.txt)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

一個功能完整的加密貨幣量化交易策略框架，支援多種技術指標、回測引擎和風險管理系統。

## 特色功能

- **多策略支援**: 內建 RSI、MA、MACD 等常見技術指標策略
- **回測引擎**: 基於 Backtrader 的專業級回測系統
- **風險管理**: 完整的倉位管理、止損止盈機制
- **交易所整合**: 透過 CCXT 支援超過 100+ 交易所
- **實時監控**: Telegram 即時通知和警報系統
- **數據視覺化**: 美觀的圖表和回測報告
- **模組化設計**: 易於擴展和自定義策略

## 快速開始

### 前置需求

- Python 3.8 或更高版本
- pip 套件管理工具
- 穩定的網路連接（用於 API 調用）

### 安裝步驟

1. **克隆倉庫**

```bash
git clone https://github.com/wenchung/crypto-trading-strategies.git
cd crypto-trading-strategies
```

2. **創建虛擬環境**

```bash
# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

3. **安裝依賴**

```bash
pip install -r requirements.txt
```

4. **配置環境變數**

```bash
# 複製範例配置文件
cp .env.example .env

# 編輯 .env 文件，添加您的 API 密鑰
nano .env  # 或使用您喜歡的編輯器
```

在 `.env` 文件中設定：

```bash
# 交易所 API 設定
EXCHANGE_API_KEY=your_api_key_here
EXCHANGE_API_SECRET=your_api_secret_here

# Telegram 通知（可選）
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 交易模式
TRADING_MODE=testnet  # 或 production
```

5. **運行第一個回測**

```bash
# 執行範例策略回測
python examples/backtest_example.py
```

### 五分鐘快速體驗

```python
# quick_start.py
from strategies.rsi_strategy import RSIStrategy
from backtest_engine import BacktestEngine
import ccxt

# 1. 初始化交易所
exchange = ccxt.binance({
    'enableRateLimit': True,
})

# 2. 創建策略
strategy = RSIStrategy(
    rsi_period=14,
    overbought=70,
    oversold=30
)

# 3. 運行回測
engine = BacktestEngine(
    strategy=strategy,
    symbol='BTC/USDT',
    timeframe='1h',
    start_date='2023-01-01',
    end_date='2023-12-31',
    initial_capital=10000
)

# 4. 執行並查看結果
results = engine.run()
print(f"總收益: {results['total_return']:.2%}")
print(f"夏普比率: {results['sharpe_ratio']:.2f}")
print(f"最大回撤: {results['max_drawdown']:.2%}")

# 5. 生成圖表
engine.plot()
```

運行：

```bash
python quick_start.py
```

## 專案結構

```
crypto-trading-strategies/
├── strategies/              # 交易策略
│   ├── base.py             # 策略基礎類別
│   ├── rsi_strategy.py     # RSI 策略
│   ├── ma_crossover.py     # 均線交叉策略
│   └── macd_strategy.py    # MACD 策略
├── backtest_engine.py      # 回測引擎
├── risk_manager.py         # 風險管理
├── monitor_alerter.py      # 監控和警報
├── config_settings.py      # 配置管理
├── examples/               # 範例代碼
│   ├── simple_strategy.py
│   └── backtest_example.py
├── docs/                   # 文檔
│   ├── strategies.md
│   └── deployment.md
├── tests/                  # 測試
├── requirements.txt        # Python 依賴
├── BUILD.md               # 構建指南
└── CONTRIBUTING.md        # 貢獻指南
```

## 核心功能

### 1. 策略開發

創建自定義策略非常簡單：

```python
from strategies.base import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, param1, param2):
        super().__init__()
        self.param1 = param1
        self.param2 = param2
    
    def generate_signal(self, data):
        # 實現您的交易邏輯
        if self.should_buy(data):
            return 'BUY'
        elif self.should_sell(data):
            return 'SELL'
        return 'HOLD'
```

### 2. 回測分析

```python
# 運行回測
results = engine.run()

# 查看詳細指標
print(results['metrics'])
# - 總收益率
# - 年化收益率
# - 夏普比率
# - 最大回撤
# - 勝率
# - 盈虧比
```

### 3. 風險管理

```python
from risk_manager import RiskManager

risk_mgr = RiskManager(
    max_position_size=0.1,    # 單筆最大 10%
    stop_loss_pct=0.02,       # 2% 止損
    take_profit_pct=0.05,     # 5% 止盈
    max_daily_loss=0.05       # 單日最大虧損 5%
)
```

### 4. 實時監控

```python
from monitor_alerter import TelegramAlerter

alerter = TelegramAlerter(
    bot_token='YOUR_BOT_TOKEN',
    chat_id='YOUR_CHAT_ID'
)

# 發送交易通知
alerter.send_trade_alert(
    symbol='BTC/USDT',
    action='BUY',
    price=50000,
    quantity=0.1
)
```

## 內建策略

### RSI 策略
- 基於相對強弱指標的超買超賣策略
- 參數：RSI 週期、超買閾值、超賣閾值

### 均線交叉策略
- 快速和慢速移動平均線交叉
- 參數：快線週期、慢線週期

### MACD 策略
- 基於 MACD 指標的趨勢追蹤
- 參數：快線、慢線、訊號線週期

### 布林帶策略
- 價格突破布林帶上下軌
- 參數：週期、標準差倍數

更多策略請參見 [策略文檔](docs/strategies.md)

## 配置說明

### 策略配置

在 `config/strategy_config.yaml` 中設定：

```yaml
strategy:
  name: "RSI_Strategy"
  timeframe: "1h"
  
  parameters:
    rsi_period: 14
    overbought: 70
    oversold: 30
  
  risk_management:
    max_position_size: 0.1
    stop_loss_pct: 0.02
    take_profit_pct: 0.05
```

### 交易對配置

在 `config/pairs.yaml` 中設定：

```yaml
trading_pairs:
  - BTC/USDT
  - ETH/USDT
  - BNB/USDT
```

## 測試

運行測試套件：

```bash
# 運行所有測試
pytest tests/

# 運行特定測試
pytest tests/test_strategies.py -v

# 生成覆蓋率報告
pytest --cov=strategies --cov-report=html
```

## 文檔

- [構建指南](BUILD.md) - 詳細的安裝和設置說明
- [貢獻指南](CONTRIBUTING.md) - 如何為專案做出貢獻
- [策略開發](docs/strategies.md) - 策略開發指南
- [API 文檔](docs/api.md) - API 參考文檔
- [部署指南](docs/deployment.md) - 生產環境部署

## 使用範例

### 範例 1: 簡單回測

```bash
python examples/simple_backtest.py --symbol BTC/USDT --timeframe 1h
```

### 範例 2: 多策略比較

```bash
python examples/strategy_comparison.py
```

### 範例 3: 實時交易（模擬）

```bash
python examples/paper_trading.py --strategy rsi
```

## 效能優化

- **並行處理**: 支援多進程回測多個交易對
- **數據緩存**: 智能緩存歷史數據減少 API 調用
- **增量更新**: 只更新最新的 K 線數據

## 安全注意事項

1. **永遠不要提交 API 密鑰**: 使用 `.env` 文件並加入 `.gitignore`
2. **測試網路優先**: 在實盤前充分測試
3. **小額測試**: 實盤時先用小額資金測試
4. **監控和警報**: 設置止損和實時監控
5. **定期檢查**: 定期檢查策略表現和資金狀況

## 常見問題

### Q: 如何添加新的交易所？

A: CCXT 支援 100+ 交易所，只需在配置中修改交易所名稱即可。

### Q: 可以實盤交易嗎？

A: 可以，但請先在測試網路充分測試，並遵守風險管理原則。

### Q: 如何獲取歷史數據？

A: 框架會自動從交易所 API 獲取歷史數據並緩存。

### Q: 支援哪些技術指標？

A: 透過 `ta` 庫支援 100+ 技術指標，包括 RSI, MACD, BB, SMA, EMA 等。

更多問題請查看 [FAQ](docs/FAQ.md)

## 路線圖

- [x] 基礎回測引擎
- [x] 風險管理系統
- [x] Telegram 通知
- [ ] Web 儀表板
- [ ] 機器學習策略
- [ ] 多交易所套利
- [ ] 實時風險監控
- [ ] Docker 部署支援

## 貢獻

我們歡迎所有形式的貢獻！請閱讀 [貢獻指南](CONTRIBUTING.md) 了解詳情。

### 貢獻者

感謝所有為本專案做出貢獻的開發者！

## 免責聲明

**重要**: 本專案僅供教育和研究目的使用。

- 作者不對任何交易損失負責
- 加密貨幣交易涉及高風險
- 過去的表現不代表未來結果
- 請在充分理解風險後使用
- 建議在投資前諮詢專業財務顧問

**這不是財務建議。請自行承擔風險。**

## 授權

本專案採用雙重授權：

- **AGPLv3** 用於開源使用
- **商業授權** 可用於商業部署

詳見 [LICENSE.txt](LICENSE.txt)

## 聯繫方式

- **Issues**: [GitHub Issues](https://github.com/wenchung/crypto-trading-strategies/issues)
- **Discussions**: [GitHub Discussions](https://github.com/wenchung/crypto-trading-strategies/discussions)
- **Email**: cwthome@gmail.com

## 致謝

本專案使用了以下優秀的開源項目：

- [CCXT](https://github.com/ccxt/ccxt) - 加密貨幣交易所整合
- [Backtrader](https://github.com/mementum/backtrader) - 回測框架
- [TA-Lib](https://github.com/mrjbq7/ta-lib) - 技術分析指標
- [Pandas](https://github.com/pandas-dev/pandas) - 數據處理

---

**Made with ❤️ by the open-source community**

**Star ⭐ this repo if you find it useful!**
