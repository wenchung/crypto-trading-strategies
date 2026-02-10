# 貢獻指南 (Contributing Guide)

感謝您對本專案的興趣！我們歡迎所有形式的貢獻，無論是報告錯誤、提出新功能、改進文檔還是提交代碼。

## 目錄

- [行為準則](#行為準則)
- [如何貢獻](#如何貢獻)
- [開發流程](#開發流程)
- [代碼規範](#代碼規範)
- [提交規範](#提交規範)
- [測試要求](#測試要求)
- [文檔規範](#文檔規範)

## 行為準則

### 我們的承諾

為了營造一個開放和友善的環境，我們承諾：

- 尊重不同的觀點和經驗
- 優雅地接受建設性批評
- 專注於對社群最有利的事情
- 對其他社群成員表現同理心

### 不可接受的行為

- 使用性化語言或圖像
- 挑釁、侮辱性評論或人身攻擊
- 公開或私下騷擾
- 未經許可發布他人的私人信息
- 其他在專業環境中不適當的行為

## 如何貢獻

### 報告錯誤 (Bug Reports)

在提交錯誤報告前：

1. 檢查 [現有的 Issues](https://github.com/wenchung/crypto-trading-strategies/issues) 確認問題是否已被報告
2. 確保您使用的是最新版本
3. 收集相關的錯誤信息和日誌

提交錯誤報告時請包含：

- **清晰的標題**: 簡潔描述問題
- **環境信息**: Python 版本、作業系統、依賴版本
- **重現步驟**: 詳細的步驟說明
- **預期行為**: 您期望發生什麼
- **實際行為**: 實際發生了什麼
- **錯誤日誌**: 完整的錯誤訊息和堆疊追蹤
- **截圖**: 如果適用

**範例模板**:

```markdown
## 問題描述
簡要描述問題

## 環境
- Python 版本: 3.10.5
- OS: Ubuntu 22.04
- ccxt 版本: 4.0.0

## 重現步驟
1. 運行 `python main.py`
2. 執行策略 X
3. 觀察到錯誤

## 預期行為
應該正常執行策略

## 實際行為
拋出 KeyError 異常

## 錯誤日誌
```
[粘貼錯誤日誌]
```
```

### 提出新功能 (Feature Requests)

提出新功能建議時：

1. 檢查是否已有類似的功能請求
2. 清楚說明功能的用途和價值
3. 提供使用案例和範例
4. 考慮實現的可行性

**範例模板**:

```markdown
## 功能描述
清晰描述您想要的功能

## 動機
為什麼需要這個功能？解決什麼問題？

## 建議的解決方案
您認為應該如何實現？

## 替代方案
考慮過哪些其他方法？

## 額外說明
任何其他相關信息、截圖或參考資料
```

### 改進文檔

文檔改進也是重要的貢獻：

- 修正拼寫或語法錯誤
- 改善現有文檔的清晰度
- 添加缺失的文檔
- 翻譯文檔到其他語言
- 添加或改進代碼範例

## 開發流程

### 1. Fork 倉庫

點擊 GitHub 頁面右上角的 "Fork" 按鈕

### 2. 克隆您的 Fork

```bash
git clone https://github.com/YOUR-USERNAME/crypto-trading-strategies.git
cd crypto-trading-strategies
```

### 3. 添加上游遠端

```bash
git remote add upstream https://github.com/wenchung/crypto-trading-strategies.git
```

### 4. 創建分支

```bash
# 更新您的 main 分支
git checkout main
git pull upstream main

# 創建新的功能分支
git checkout -b feature/your-feature-name
# 或修復分支
git checkout -b fix/bug-description
```

分支命名規範：
- `feature/` - 新功能
- `fix/` - 錯誤修復
- `docs/` - 文檔更新
- `refactor/` - 代碼重構
- `test/` - 測試相關

### 5. 設置開發環境

```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴（包括開發依賴）
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 安裝 pre-commit hooks
pre-commit install
```

### 6. 進行更改

- 編寫清晰、可讀的代碼
- 遵循專案的代碼規範
- 添加必要的測試
- 更新相關文檔

### 7. 測試您的更改

```bash
# 運行所有測試
pytest tests/

# 運行代碼格式檢查
black --check .
flake8 .

# 運行類型檢查
mypy .
```

### 8. 提交更改

```bash
# 添加更改的文件
git add .

# 提交（會自動運行 pre-commit hooks）
git commit -m "feat: add new trading strategy"
```

### 9. 推送到您的 Fork

```bash
git push origin feature/your-feature-name
```

### 10. 創建 Pull Request

1. 前往您的 Fork 在 GitHub 上的頁面
2. 點擊 "New Pull Request"
3. 選擇您的分支
4. 填寫 PR 描述（見下方模板）
5. 提交 Pull Request

**Pull Request 模板**:

```markdown
## 描述
簡要描述您的更改

## 相關 Issue
關閉 #123 (如果適用)

## 更改類型
- [ ] Bug 修復
- [ ] 新功能
- [ ] 文檔更新
- [ ] 代碼重構
- [ ] 效能改進
- [ ] 測試添加/修改

## 更改內容
- 添加了 X 功能
- 修復了 Y 問題
- 改進了 Z 的效能

## 測試
- [ ] 所有現有測試通過
- [ ] 添加了新的測試
- [ ] 手動測試通過

## 截圖（如適用）
添加相關截圖

## 檢查清單
- [ ] 代碼遵循專案的代碼規範
- [ ] 已進行自我審查
- [ ] 代碼已添加註釋（特別是複雜部分）
- [ ] 已更新相關文檔
- [ ] 更改不會產生新的警告
- [ ] 已添加測試證明修復有效或功能正常
- [ ] 新舊測試都通過
```

## 代碼規範

### Python 代碼風格

我們遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 規範：

```python
# 好的範例
def calculate_moving_average(prices: list[float], period: int) -> float:
    """
    計算簡單移動平均線。
    
    Args:
        prices: 價格列表
        period: 計算週期
        
    Returns:
        移動平均值
    """
    if len(prices) < period:
        raise ValueError("價格數據不足")
    
    return sum(prices[-period:]) / period


# 避免的範例
def calcMA(p, n):  # 不清晰的命名
    return sum(p[-n:])/n  # 缺少錯誤處理和文檔
```

### 命名規範

- **類名**: `PascalCase` (例如: `TradingStrategy`)
- **函數名**: `snake_case` (例如: `calculate_rsi`)
- **變數名**: `snake_case` (例如: `current_price`)
- **常數**: `UPPER_SNAKE_CASE` (例如: `MAX_POSITION_SIZE`)
- **私有成員**: 前綴 `_` (例如: `_internal_method`)

### 文檔字串

使用 Google 風格的文檔字串：

```python
def execute_trade(symbol: str, amount: float, side: str) -> dict:
    """
    執行交易訂單。
    
    這個函數會驗證參數並向交易所發送訂單。
    
    Args:
        symbol: 交易對符號，例如 'BTC/USDT'
        amount: 交易數量
        side: 交易方向，'buy' 或 'sell'
        
    Returns:
        包含訂單信息的字典，包括:
            - order_id: 訂單ID
            - status: 訂單狀態
            - filled: 已成交數量
            
    Raises:
        ValueError: 如果參數無效
        ExchangeError: 如果交易所返回錯誤
        
    Example:
        >>> result = execute_trade('BTC/USDT', 0.1, 'buy')
        >>> print(result['order_id'])
        '12345678'
    """
    pass
```

### 代碼格式化

使用 Black 進行自動格式化：

```bash
# 格式化所有文件
black .

# 格式化特定文件
black strategies/rsi_strategy.py

# 檢查但不修改
black --check .
```

### 導入順序

```python
# 1. 標準庫
import os
import sys
from datetime import datetime

# 2. 第三方庫
import pandas as pd
import numpy as np
from ccxt import Exchange

# 3. 本地導入
from strategies.base import BaseStrategy
from utils.logger import setup_logger
```

## 提交規範

我們使用 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

### 提交訊息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 類型 (Type)

- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文檔更新
- `style`: 代碼格式（不影響功能）
- `refactor`: 代碼重構
- `perf`: 效能改進
- `test`: 測試相關
- `chore`: 構建過程或輔助工具的變動

### 範例

```bash
# 好的提交訊息
git commit -m "feat(strategies): add RSI crossover strategy"
git commit -m "fix(backtest): correct profit calculation error"
git commit -m "docs(readme): update installation instructions"

# 避免的提交訊息
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

### 詳細範例

```
feat(risk-manager): add position sizing based on Kelly criterion

Implement Kelly criterion for optimal position sizing:
- Calculate win rate from historical trades
- Compute optimal fraction of capital to risk
- Add configuration options for Kelly multiplier
- Include unit tests for edge cases

Closes #42
```

## 測試要求

### 編寫測試

所有新代碼都應該包含測試：

```python
# tests/test_strategies.py
import pytest
from strategies.rsi_strategy import RSIStrategy


class TestRSIStrategy:
    """測試 RSI 策略"""
    
    def setup_method(self):
        """每個測試方法前執行"""
        self.strategy = RSIStrategy(
            rsi_period=14,
            overbought=70,
            oversold=30
        )
    
    def test_calculate_rsi(self):
        """測試 RSI 計算"""
        prices = [100, 102, 101, 103, 105, 104, 106]
        rsi = self.strategy.calculate_rsi(prices)
        
        assert isinstance(rsi, float)
        assert 0 <= rsi <= 100
    
    def test_generate_signal_buy(self):
        """測試買入信號生成"""
        rsi = 25  # 超賣
        signal = self.strategy.generate_signal(rsi)
        
        assert signal == 'BUY'
    
    def test_generate_signal_sell(self):
        """測試賣出信號生成"""
        rsi = 75  # 超買
        signal = self.strategy.generate_signal(rsi)
        
        assert signal == 'SELL'
    
    @pytest.mark.parametrize("rsi,expected", [
        (25, 'BUY'),
        (50, 'HOLD'),
        (75, 'SELL'),
    ])
    def test_multiple_scenarios(self, rsi, expected):
        """測試多種情景"""
        signal = self.strategy.generate_signal(rsi)
        assert signal == expected
```

### 運行測試

```bash
# 運行所有測試
pytest

# 運行特定測試文件
pytest tests/test_strategies.py

# 運行特定測試方法
pytest tests/test_strategies.py::TestRSIStrategy::test_calculate_rsi

# 顯示詳細輸出
pytest -v

# 顯示代碼覆蓋率
pytest --cov=strategies --cov-report=html
```

### 測試覆蓋率

我們要求：
- 新代碼的測試覆蓋率至少 80%
- 關鍵功能（策略、風險管理）覆蓋率至少 90%

## 文檔規範

### 代碼文檔

- 所有公開函數和類都必須有文檔字串
- 複雜的演算法需要解釋性註釋
- 使用清晰的變數名減少需要的註釋

### README 和指南

- 保持文檔更新和準確
- 提供實用的範例
- 使用清晰的語言
- 包含必要的截圖和圖表

### API 文檔

使用 Sphinx 生成 API 文檔：

```bash
# 生成文檔
cd docs
make html

# 查看文檔
open _build/html/index.html
```

## Pull Request 審查流程

### 審查標準

PR 將根據以下標準審查：

1. **代碼品質**: 遵循代碼規範，清晰易讀
2. **功能性**: 實現承諾的功能
3. **測試**: 包含充分的測試
4. **文檔**: 更新相關文檔
5. **效能**: 不會顯著降低效能
6. **安全性**: 不引入安全漏洞

### 審查時間

- 小型 PR（< 100 行）: 通常 1-2 天
- 中型 PR（100-500 行）: 通常 3-5 天
- 大型 PR（> 500 行）: 可能需要一週或更長

### 回應審查意見

- 禮貌、建設性地回應所有評論
- 解釋您的設計決策
- 如果不同意，提供理由
- 及時進行要求的更改

## 版本發布

我們使用 [Semantic Versioning](https://semver.org/)：

- **MAJOR** (1.0.0): 不兼容的 API 變更
- **MINOR** (0.1.0): 向後兼容的功能添加
- **PATCH** (0.0.1): 向後兼容的錯誤修復

## 獲取幫助

如有疑問：

- 查看 [FAQ](docs/FAQ.md)
- 查看 [討論區](https://github.com/wenchung/crypto-trading-strategies/discussions)
- 在 Issue 中提問
- 聯繫維護者

## 致謝

感謝所有為本專案做出貢獻的人！您的努力讓這個專案變得更好。

---

**記住**: 無論大小，每個貢獻都很重要！我們感謝您的參與。
