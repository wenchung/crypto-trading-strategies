# 構建指南 (Build Guide)

本文檔提供完整的專案構建、安裝和開發環境設置說明。

## 目錄

- [系統需求](#系統需求)
- [快速開始](#快速開始)
- [詳細安裝步驟](#詳細安裝步驟)
- [配置設定](#配置設定)
- [運行測試](#運行測試)
- [常見問題](#常見問題)

## 系統需求

### 必要條件

- **Python**: 3.8 或更高版本
- **pip**: 最新版本 (建議 >= 21.0)
- **Git**: 用於版本控制
- **虛擬環境**: 推薦使用 venv 或 conda

### 推薦配置

- **作業系統**: Linux, macOS, 或 Windows 10/11
- **RAM**: 至少 4GB (推薦 8GB+)
- **磁碟空間**: 至少 1GB 可用空間
- **網路**: 穩定的網際網路連接（用於 API 調用）

## 快速開始

對於有經驗的開發者，以下是快速設置步驟：

```bash
# 1. 克隆倉庫
git clone https://github.com/wenchung/crypto-trading-strategies.git
cd crypto-trading-strategies

# 2. 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 配置環境變數
cp .env.example .env
# 編輯 .env 文件添加您的 API 密鑰

# 5. 運行範例
python examples/simple_strategy.py
```

## 詳細安裝步驟

### 1. 克隆倉庫

```bash
git clone https://github.com/wenchung/crypto-trading-strategies.git
cd crypto-trading-strategies
```

### 2. 設置 Python 虛擬環境

#### 使用 venv (推薦)

```bash
# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
# Linux/macOS:
source venv/bin/activate

# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Windows (CMD):
venv\Scripts\activate.bat
```

#### 使用 conda

```bash
# 創建 conda 環境
conda create -n crypto-trading python=3.10

# 啟動環境
conda activate crypto-trading
```

### 3. 安裝依賴套件

```bash
# 升級 pip
pip install --upgrade pip

# 安裝所有依賴
pip install -r requirements.txt
```

#### 依賴說明

核心依賴包括：

- **ccxt** (>=4.0.0): 加密貨幣交易所整合
- **pandas** (>=2.0.0): 數據處理和分析
- **numpy** (>=1.24.0): 數值計算
- **ta** (>=0.11.0): 技術分析指標
- **backtrader** (>=1.9.78): 回測框架
- **python-telegram-bot** (>=20.0): Telegram 通知（可選）
- **matplotlib** (>=3.7.0): 數據視覺化
- **plotly** (>=5.14.0): 互動式圖表

### 4. 驗證安裝

運行以下命令確認安裝成功：

```bash
python -c "import ccxt, pandas, numpy, ta, backtrader; print('所有依賴已成功安裝！')"
```

## 配置設定

### 1. 環境變數配置

創建 `.env` 文件來存儲敏感信息：

```bash
# 複製範例配置文件
cp .env.example .env
```

編輯 `.env` 文件並添加您的配置：

```bash
# 交易所 API 密鑰
EXCHANGE_API_KEY=your_api_key_here
EXCHANGE_API_SECRET=your_api_secret_here

# Telegram 通知 (可選)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# 交易配置
TRADING_MODE=testnet  # 或 production
DEFAULT_EXCHANGE=binance
```

### 2. 策略配置

配置文件位於 `config/` 目錄：

```yaml
# config/strategy_config.yaml
strategy:
  name: "RSI_MA_Strategy"
  timeframe: "1h"
  
  parameters:
    rsi_period: 14
    rsi_overbought: 70
    rsi_oversold: 30
    ma_period: 20
    
  risk_management:
    max_position_size: 0.1  # 10% 的資金
    stop_loss_pct: 0.02      # 2% 止損
    take_profit_pct: 0.05    # 5% 止盈
```

### 3. 交易對配置

在 `config/pairs.yaml` 中設定交易對：

```yaml
trading_pairs:
  - BTC/USDT
  - ETH/USDT
  - BNB/USDT
```

## 運行測試

### 單元測試

```bash
# 運行所有測試
python -m pytest tests/

# 運行特定測試文件
python -m pytest tests/test_strategies.py

# 運行並顯示詳細輸出
python -m pytest -v tests/
```

### 回測測試

```bash
# 運行回測範例
python examples/backtest_example.py

# 使用自定義時間範圍
python backtest_engine.py --start 2023-01-01 --end 2023-12-31
```

### 策略驗證

```bash
# 驗證策略配置
python -m strategies.validate_strategy

# 乾跑模式（不實際交易）
python main.py --dry-run
```

## 開發環境設置

### 安裝開發依賴

```bash
pip install -r requirements-dev.txt
```

開發依賴包括：

- **pytest**: 測試框架
- **black**: 代碼格式化
- **flake8**: 代碼檢查
- **mypy**: 類型檢查
- **pre-commit**: Git hooks

### 代碼格式化

```bash
# 格式化所有 Python 文件
black .

# 檢查代碼風格
flake8 .

# 類型檢查
mypy .
```

### 設置 Pre-commit Hooks

```bash
# 安裝 pre-commit hooks
pre-commit install

# 手動運行所有 hooks
pre-commit run --all-files
```

## 構建部署

### 1. 創建可執行檔案

```bash
# 使用 PyInstaller
pip install pyinstaller
pyinstaller --onefile main.py
```

### 2. Docker 部署

```bash
# 構建 Docker 映像
docker build -t crypto-trading-bot .

# 運行容器
docker run -d --env-file .env crypto-trading-bot
```

### 3. 雲端部署

詳見 `docs/deployment.md`

## 常見問題

### Q1: 安裝依賴時出現錯誤

**A**: 確保您使用的是最新版本的 pip：

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Q2: ccxt 安裝失敗

**A**: 某些系統可能需要額外的編譯工具：

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev build-essential

# macOS
xcode-select --install

# 然後重新安裝
pip install ccxt
```

### Q3: backtrader 與 matplotlib 版本衝突

**A**: 使用指定版本：

```bash
pip install matplotlib==3.7.0 backtrader==1.9.78
```

### Q4: 無法連接到交易所 API

**A**: 檢查以下項目：

1. 確認 API 密鑰正確
2. 檢查網路連接
3. 驗證交易所是否支援您的地區
4. 確認 API 權限設定正確

### Q5: 權限錯誤

**A**: 在 Linux/macOS 上，確保腳本有執行權限：

```bash
chmod +x main.py
chmod +x scripts/*.py
```

## 效能優化

### 1. 使用編譯版本的依賴

```bash
# 安裝 Cython 加速版本
pip install cython
pip install numpy --no-binary numpy
```

### 2. 資料庫優化

使用 SQLite 或 PostgreSQL 來存儲歷史數據：

```bash
pip install sqlalchemy psycopg2-binary
```

### 3. 平行處理

對於多交易對策略，啟用多進程：

```python
# 在配置文件中
parallel_processing: true
max_workers: 4
```

## 更新專案

```bash
# 拉取最新代碼
git pull origin main

# 更新依賴
pip install -r requirements.txt --upgrade

# 運行遷移腳本（如果有）
python scripts/migrate.py
```

## 獲取幫助

- **文檔**: 查看 `docs/` 目錄
- **範例**: 查看 `examples/` 目錄
- **問題追蹤**: [GitHub Issues](https://github.com/wenchung/crypto-trading-strategies/issues)
- **討論**: [GitHub Discussions](https://github.com/wenchung/crypto-trading-strategies/discussions)

## 下一步

安裝完成後，您可以：

1. 閱讀 [README.md](README.md) 了解專案概述
2. 查看 [CONTRIBUTING.md](CONTRIBUTING.md) 學習如何貢獻
3. 探索 `examples/` 目錄中的範例代碼
4. 運行您的第一個回測：`python examples/backtest_example.py`

---

**注意**: 本專案僅供教育和研究目的。實際交易涉及金融風險，請謹慎操作。
