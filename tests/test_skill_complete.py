# -*- coding: utf-8 -*-
"""
完整Skill功能验证 - 确认所有功能都已集成
"""
import sys
import os
import io

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 从__init__导入所有功能
from __init__ import (
    # Core
    StockAPIClient,
    EnhancedStockAPI,
    StockScanner,
    get_all_stocks,
    # MA Data (AKShare)
    MADataAPI,
    get_stock_ma,
    batch_get_stock_ma,
    # Assistant
    AIStockAssistant,
    get_stock_info,
    analyze_stock,
    # Strategies
    get_strategy_api,
    StrategyManager,
    StrategyGenerator,
)

print("=" * 70)
print("Skill完整功能验证")
print("=" * 70)

print("\n[1] 核心功能导入:")
print("  - StockAPIClient ✓")
print("  - EnhancedStockAPI ✓")
print("  - StockScanner ✓")
print("  - get_all_stocks ✓")

print("\n[2] MA数据功能导入 (AKShare):")
print("  - MADataAPI ✓")
print("  - get_stock_ma ✓")
print("  - batch_get_stock_ma ✓")

print("\n[3] AI助手功能导入:")
print("  - AIStockAssistant ✓")
print("  - get_stock_info ✓")
print("  - analyze_stock ✓")

print("\n[4] 战法系统功能导入:")
print("  - get_strategy_api ✓")
print("  - StrategyManager ✓")
print("  - StrategyGenerator ✓")

print("\n[5] 快速测试:")
print("  获取股票列表...")
stocks = get_all_stocks(limit=3)
print(f"  ✓ 成功获取 {len(stocks)} 只股票")

print("\n  列出战法...")
api = get_strategy_api()
result = api.list_strategies()
print(f"  ✓ 共有 {result['total']} 个战法")

print("\n" + "=" * 70)
print("验证结果: 所有功能已正确集成到Skill中 ✓")
print("=" * 70)

print("\n用户可以这样使用:")
print("  from a_stock_query_v2 import get_stock_info, get_stock_ma")
print("  get_stock_info('601318')")
print("  get_stock_ma('601318')")
print("  get_strategy_api()")
print("\n" + "=" * 70)
