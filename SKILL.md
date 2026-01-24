---
name: a-stock-query
description: Chinese A-share stock market query and analysis framework with AI-powered strategy system. Provides real-time stock quotes (Tencent/Sina/Eastmoney APIs), technical indicators (MA, candlestick, turnover rate), full market scanner (5506 A-shares), and unique strategy system that generates code from natural language descriptions. Use when: (1) User asks about current stock prices or market data for Chinese A-shares (e.g., "现在中国平安什么价格", "查询贵州茅台"), (2) User wants to create custom stock screening strategies from natural language (e.g., "新增战法-筛选:王子战法 阴线且MA5大于MA10且换手率大于5%"), (3) User requests technical analysis like moving averages, trends, candlestick patterns, (4) User wants to scan the entire A-share market for specific conditions, (5) Any query involving Chinese stock codes (601318, 600519, 000001, 002594, etc.). Features: AI-generated strategies from descriptions, real market data with turnover rates, strategy import/export for sharing, batch querying, comprehensive technical analysis.
---

# A股查询与战法系统

Complete Chinese A-share market analysis framework with AI-powered strategy generation.

## 🚀 Quick Start for Claude

### Query Stock Prices
```python
from a_stock_query_v2 import get_stock_info
print(get_stock_info('601318'))  # 中国平安
```

### Get MA (Moving Average) Data
```python
from a_stock_query_v2 import get_stock_ma

ma_data = get_stock_ma('601318')
# Returns: {'MA5': 65.49, 'MA10': 66.39, 'MA20': 68.62, 'current_price': 63.9}
```

### Create Strategies from Natural Language
```python
from a_stock_query_v2 import get_strategy_api

api = get_strategy_api()
api.create_strategy('新增战法-筛选:王子战法 阴线且MA5大于MA10且换手率大于5%')
# Automatically generates Python code for the strategy
```

### Scan Entire Market
```python
from a_stock_query_v2 import StockScanner, EnhancedStockAPI

scanner = StockScanner()
api = EnhancedStockAPI()

# Get all 5506 A-shares
all_stocks = scanner.get_all_stocks()

# Filter with real data
results = [s for s in all_stocks if s['change_percent'] > 5.0]
```

## 📦 Module Structure

```
scripts/              # Core functionality
├── stock_api.py         # Basic API (Tencent, Sina)
├── stock_api_enhanced.py # Enhanced API (Eastmoney with turnover rate)
├── stock_scanner.py     # Market scanner (5506 A-shares)
├── stock_ma_data.py     # MA historical data (AKShare integration)
└── technical_indicators.py # Technical indicators

strategies/           # Strategy system (standalone)
├── strategy_api.py     # Strategy API
├── strategy_manager.py # Strategy manager
├── strategy_generator.py # Code generator
├── builtin/           # Built-in strategies
└── custom/            # User strategies

assistant/            # AI assistant
└── ai_stock_assistant.py

demos/               # Demo scripts
docs/                # Documentation
├── USER_GUIDE.md       # User manual
└── STRATEGY_GUIDE.md  # Strategy system guide
```

## 💡 Common Use Cases

### Query Stock Price
User: "现在中国平安什么价格？"
```python
from quick_import import get_stock_info
get_stock_info('601318')
# Returns: 中国平安(601318) 当前价格: ¥63.90, 涨跌幅: -1.39%
```

### Create Strategy
User: "帮我创建一个战法：阴线且换手率大于3%"
```python
from strategies import get_strategy_api
api = get_strategy_api()
api.create_strategy('新增战法-筛选:回调战法 阴线且换手率大于3%')
```

### Scan Market
User: "找出所有涨幅超过5%且换手率大于3%的股票"
```python
from a_stock_query_v2 import StockScanner, EnhancedStockAPI
scanner = StockScanner()
api = EnhancedStockAPI()

stocks = scanner.get_all_stocks()
qualified = []
for stock in stocks[:500]:  # Scan in batches
    detail = api.get_stock_detail_em(stock['code'])
    if detail['change_percent'] > 5 and detail['turnover_rate'] > 3:
        qualified.append(detail)
```

## 🔑 Strategy System

### Creating Strategies

**Format**: `新增战法-筛选:战法名称 描述`

**Supported Syntax**:
- MA conditions: `MA5大于MA10`, `MA20<MA30`
- Candlestick: `阴线`, `阳线`, `十字星`
- Turnover: `换手率大于5%`, `换手率>10`
- Volume: `成交量大于10000`
- Combine: use `且` to connect conditions

**Example Strategies**:
1. **王子战法** - 阴线且MA5大于MA10且换手率大于5%
2. **活跃股回调** - 阴线且MA5大于MA10且换手率大于2%

### Managing Strategies

```python
from strategies import get_strategy_api
api = get_strategy_api()

# List all strategies
api.list_strategies()

# Get strategy info
api.get_strategy_info('王子战法')

# Delete strategy
api.delete_strategy('旧战法')

# Export strategy (for sharing)
api.export_strategy('王子战法', './my_strategy.py')

# Import strategy
api.import_strategy('./shared.py', '新战法')
```

## 📊 Data Sources

| Data | Source | Status |
|------|--------|--------|
| Price, Change | Tencent/Sina APIs | ✅ Real-time |
| Turnover Rate | Eastmoney API (f168 field) | ✅ Real-time |
| Volume | Eastmoney API | ✅ Real-time |
| Market Cap | Eastmoney API | ✅ Real-time |
| MA values | AKShare (historical data) | ✅ Available |

**Important**: Turnover rate is REAL data from Eastmoney API. MA values are calculated from AKShare historical data.

## 📋 Stock Codes

- Shanghai: 6xxxxx (e.g., 601318 = 中国平安, 600519 = 贵州茅台)
- Shenzhen: 000xxx, 002xxx, 300xxx (e.g., 000001 = 平安银行, 002594 = 比亚迪, 300750 = 宁德时代)

No prefix needed - auto-detects market.

## 🎯 Strategy Format & Export

Strategies are saved as standalone Python files:

```python
"""
战法名称: 我的战法
战法描述: 阴线且换手率大于5%
作者: AI
"""
STRATEGY_NAME = "我的战法"
STRATEGY_DESCRIPTION = "阴线且换手率大于5%"
STRATEGY_AUTHOR = "AI"
STRATEGY_VERSION = "1.0.0"

def screen(stock_data, **params):
    # Screening logic
    return True
```

**Export/Import** for sharing:
```python
# Export
api.export_strategy('我的战法', './my_strategy.py')

# Import
api.import_strategy('./friend_strategy.py', '朋友战法')
```

## ⚙️ Quick Import for Claude

```python
# Single line import for all functionality
from quick_import import (
    get_stock_info,
    analyze_stock,
    get_strategy_api,
    EnhancedStockAPI,
    StockScanner
)
```

## 📚 Documentation

- [user_guide.md](docs/user_guide.md) - Complete user manual
- [strategy_guide.md](docs/strategy_guide.md) - Strategy system guide

## 🔧 Technical Details

### Turnover Rate Data
- **Source**: Eastmoney API field f168
- **Format**: Needs division by 100 (e.g., 57 → 0.57%)
- **Verified**: ✅ Tested against calculated values

### Market Scanner
- **Total A-shares**: 5506 stocks
- **API**: Eastmoney market list
- **Batch processing**: Supports concurrent scanning

## ⚠️ Important Notes

1. **MA Values**: Currently simulated (need historical data API)
2. **Request Limits**: Avoid excessive requests to prevent rate limiting
3. **Trading Hours**: Data only available during market hours
4. **Strategy Parameters**: MA values must be provided externally (not in real-time data)

## 🎯 Best Practices for Claude

1. **For Simple Queries**: Use `get_stock_info(code)` - fastest
2. **For Analysis**: Use `analyze_stock(code)` - detailed insights
3. **For Screening**: Use strategies with `get_strategy_api()`
4. **For Market Scan**: Use `StockScanner` with filters
5. **For Custom Strategies**: Use natural language description

## 🔄 Version

**v2.0.0** - Current
- Refactored module structure
- Real turnover rate data
- Full market scanning
- Strategy system standalone

## 📞 Example Session

```
User: 现在贵州茅台什么价格？
Claude: [Uses get_stock_info('600519')]
Claude: 贵州茅台(600519) 当前价格: ¥1337.00, 涨跌幅: -0.23%

User: 创建一个战法：阳线且换手率大于10%
Claude: [Uses get_strategy_api().create_strategy(...)]
Claude: ✓ 战法 "阳线高换手" 创建成功

User: 筛选换手率大于5%的所有股票
Claude: [Uses StockScanner + EnhancedStockAPI]
Claude: 找到 15 只符合条件的股票...
```
