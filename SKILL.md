---
name: a-stock-query
description: Chinese A-share stock market query and analysis framework with AI-powered strategy system. Provides real-time stock quotes (Tencent/Sina/Eastmoney APIs), technical indicators (MA, candlestick, turnover rate), full market scanner (5506 A-shares), and flexible strategy system that generates code from natural language descriptions. Use when: (1) User asks about current stock prices or market data for Chinese A-shares, (2) User wants to create custom stock screening strategies from natural language descriptions, (3) User requests technical analysis like moving averages, trends, candlestick patterns, (4) User wants to scan the A-share market with custom filters, (5) Any query involving Chinese stock codes. Features: AI-generated strategies from descriptions, real market data with turnover rates, strategy import/export for sharing, batch querying, comprehensive technical analysis.
---

# A股查询与战法系统

Chinese A-share market analysis framework with flexible AI-powered strategy generation.

## Overview

This is a **generic framework** for querying Chinese A-share stock data and creating custom screening strategies. It does NOT contain pre-built strategies or fixed screening patterns - all strategies are dynamically generated based on user descriptions.

## Quick Start

```python
# Basic stock query
from ai_trade import get_stock_info
stock_info = get_stock_info('STOCK_CODE')  # e.g., '601318', '600519', etc.

# Get MA (Moving Average) data
from ai_trade import get_stock_ma
ma_data = get_stock_ma('STOCK_CODE')
# Returns: {'MA5': value, 'MA10': value, 'MA20': value, ...}

# Create custom strategy from natural language
from ai_trade import get_strategy_api
api = get_strategy_api()
api.create_strategy('新增战法-筛选:YOUR_STRATEGY_NAME YOUR_DESCRIPTION')
# Replace YOUR_STRATEGY_NAME and YOUR_DESCRIPTION

# Scan entire market
from ai_trade import StockScanner
scanner = StockScanner()
all_stocks = scanner.get_all_stocks()  # All 5506 A-shares
```

## Module Structure

```
scripts/              # Core functionality
├── stock_api.py         # Basic API (Tencent, Sina)
├── stock_api_enhanced.py # Enhanced API (Eastmoney with turnover rate)
├── stock_scanner.py     # Market scanner (5506 A-shares)
├── stock_ma_data.py     # MA historical data (AKShare integration)
├── technical_indicators.py # Technical indicators
└── encoding_helper.py   # UTF-8 encoding support for Windows

strategies/           # Strategy system (standalone)
├── strategy_api.py     # Strategy API
├── strategy_manager.py # Strategy manager
├── strategy_generator.py # Code generator from natural language
├── builtin/           # Built-in strategies
└── custom/            # User-created strategies

assistant/            # AI assistant
└── ai_stock_assistant.py

demos/               # Demo scripts
tests/               # Test scripts
docs/                # Documentation
```

## Stock Query APIs

### Single Stock Query
```python
from ai_trade import get_stock_info, analyze_stock

# Get basic info
info = get_stock_info('STOCK_CODE')

# Get detailed analysis
analysis = analyze_stock('STOCK_CODE')
```

### Batch Query
```python
from ai_trade import StockScanner, EnhancedStockAPI

scanner = StockScanner()
api = EnhancedStockAPI()

# Get all stocks
all_stocks = scanner.get_all_stocks()

# Filter with custom conditions
results = [s for s in all_stocks if YOUR_CONDITION_HERE]
```

## Strategy System

The strategy system is **completely flexible** - create any screening criteria from natural language.

### Create Strategy Format

**Pattern**: `新增战法-筛选:STRATEGY_NAME DESCRIPTION`

**Supported Syntax Components**:
- MA conditions: `MA5大于MA10`, `MA20<MA30`, `MA5>MA20`, etc.
- Candlestick patterns: `阴线`, `阳线`, `十字星`
- Turnover rate: `换手率大于N%`, `换手率>N`, `换手率<N`
- Volume: `成交量大于N`
- Logical connectors: `且` (AND) to combine conditions

### Strategy Creation Examples

```python
from ai_trade import get_strategy_api
api = get_strategy_api()

# Example 1: Simple strategy
api.create_strategy('新增战法-筛选:MY_STRATEGY 阴线且换手率大于5%')

# Example 2: Complex strategy
api.create_strategy('新增战法-筛选:ANOTHER_STRATEGY MA5大于MA20且阳线且成交量大于10000')

# Example 3: Any combination
api.create_strategy('新增战法-筛选:CUSTOM_NAME CONDITION1且CONDITION2且CONDITION3')
```

**IMPORTANT**: Replace strategy names and conditions with your actual requirements. The system will generate appropriate Python code.

### Strategy Management

```python
from ai_trade import get_strategy_api
api = get_strategy_api()

# List all strategies
api.list_strategies()

# Get strategy details
api.get_strategy_info('STRATEGY_NAME')

# Delete strategy
api.delete_strategy('STRATEGY_NAME')

# Export strategy for sharing
api.export_strategy('STRATEGY_NAME', './path/to/export.py')

# Import strategy from file
api.import_strategy('./path/to/strategy.py', 'STRATEGY_NAME')
```

### Use Strategy for Screening

```python
from ai_trade import get_strategy_api, StockScanner, batch_get_stock_ma

api = get_strategy_api()
scanner = StockScanner()

# Get all stocks
all_stocks = scanner.get_all_stocks(limit=100)  # Adjust limit as needed

# Get MA data for stocks
ma_data = batch_get_stock_ma([s['code'] for s in all_stocks])

# Apply strategy
strategy = api.get_strategy('STRATEGY_NAME')
results = []
for stock in all_stocks:
    ma = ma_data.get(stock['code'], {})
    if strategy.screen(stock, ma5=ma.get('MA5'), ma20=ma.get('MA20'),
                      turnover_rate=stock.get('turnover_rate', 0)):
        results.append(stock)
```

## Data Sources

| Data Type | Source | API | Availability |
|-----------|--------|-----|--------------|
| Price, Change % | Tencent/Sina | stock_api.py | Real-time |
| Turnover Rate | Eastmoney | stock_api_enhanced.py (f168) | Real-time |
| Volume | Eastmoney | stock_api_enhanced.py | Real-time |
| Market Cap | Eastmoney | stock_api_enhanced.py | Real-time |
| MA Values | AKShare | stock_ma_data.py | Historical (calculated) |

**Note**: MA values are calculated from historical data fetched via AKShare, with 1-second delay between requests to avoid rate limiting.

## Stock Code Format

- Shanghai: 6xxxxx (e.g., 601318, 600519)
- Shenzhen: 000xxx, 002xxx, 300xxx (e.g., 000001, 002594, 300750)

No prefix needed - system auto-detects market.

## Strategy File Format

Generated strategies are standalone Python files:

```python
"""
战法名称: STRATEGY_NAME
战法描述: DESCRIPTION
作者: AI
版本: 1.0.0
"""

STRATEGY_NAME = "STRATEGY_NAME"
STRATEGY_DESCRIPTION = "DESCRIPTION"
STRATEGY_AUTHOR = "AI"
STRATEGY_VERSION = "1.0.0"

def get_default_params():
    return {
        # Strategy parameters
    }

def get_params_schema():
    return {
        # Parameter schema
    }

def screen(stock_data, **params):
    # Screening logic
    return all(conditions_met)
```

## Important Notes

1. **Flexible System**: This framework does NOT impose fixed strategies or patterns. All strategies are user-defined.
2. **MA Data Delay**: AKShare requests have 1-second delays to comply with data source policies.
3. **Request Limits**: Avoid excessive rapid requests to prevent rate limiting.
4. **Market Hours**: Real-time data only available during Chinese market hours.
5. **Strategy Parameters**: MA values must be obtained separately via `get_stock_ma()` or `batch_get_stock_ma()`.
6. **Encoding**: When running scripts directly on Windows, Chinese characters are handled automatically via encoding_helper.

## Best Practices

1. **Simple Query**: Use `get_stock_info(code)` for basic price info
2. **Analysis**: Use `analyze_stock(code)` for detailed technical analysis
3. **Custom Screening**: Create strategies with natural language, then apply to market scan
4. **Batch Operations**: Use `batch_get_stock_ma()` for multiple stocks to minimize API calls
5. **Export/Import**: Use strategy export/import to share custom strategies

## Creating Your Own Scripts

When creating standalone scripts that use this framework:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup UTF-8 encoding (important for Windows)
from scripts.encoding_helper import auto_setup
auto_setup()

# Now import and use the framework
from assistant import get_stock_info, analyze_stock
from scripts.stock_ma_data import get_stock_ma

# Your code here...
print(get_stock_info('601318'))
```

## Technical Details

### Turnover Rate
- **Source**: Eastmoney API field f168
- **Format**: Raw value divided by 100 (e.g., 57 → 0.57%)
- **Verification**: Tested against calculated values with < 0.1% error

### Market Scanner
- **Coverage**: All 5506 Chinese A-share stocks
- **API**: Eastmoney market list API with pagination
- **Pagination**: Automatically handles API's 100-record limit

### MA Calculation
- **Source**: AKShare `stock_zh_a_hist()` for historical K-line data
- **Method**: Pandas rolling window calculation
- **Delay**: 1 second between requests (configurable via `delay` parameter)

## Version

**Current**: v2.1.0
- ✅ Added encoding_helper for automatic UTF-8 support on Windows
- ✅ Cleaned up project structure (removed temporary files)
- ✅ Updated all scripts to use unified encoding handling
- ✅ Refactored module structure
- ✅ Real turnover rate integration
- ✅ Full market scanning capability
- ✅ Standalone strategy system
- ✅ AKShare integration for MA data

## Troubleshooting

### Chinese characters display as garbled text
**Solution**: The encoding_helper module handles this automatically. If you still have issues:
```python
from scripts.encoding_helper import auto_setup
auto_setup()
```

### MA data returns None
**Causes**:
- Stock suspended or newly listed (insufficient trading days)
- Network issues with AKShare
**Solution**: Use try-except and check if MA values exist before using them

### Strategy creation fails
**Common issues**:
- Invalid strategy name (use only letters, numbers, underscores)
- Incompatible conditions (e.g., conflicting MA requirements)
**Solution**: Check strategy syntax against supported patterns in Strategy System section
