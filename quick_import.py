"""
快捷导入模块 - 方便使用
从各模块导入常用功能
"""
# 从核心模块导入
from scripts.stock_api import StockAPIClient, StockAPIError
from scripts.stock_api_enhanced import EnhancedStockAPI
from scripts.stock_scanner import StockScanner, get_all_stocks
from scripts.technical_indicators import TechnicalIndicators, StockScreener

# 从助手模块导入
from assistant import AIStockAssistant, get_stock_info, analyze_stock

# 从战法模块导入
from strategies import get_strategy_api, StrategyManager, StrategyGenerator

__all__ = [
    # Core
    'StockAPIClient',
    'StockAPIError',
    'EnhancedStockAPI',
    'StockScanner',
    'get_all_stocks',
    'TechnicalIndicators',
    'StockScreener',
    # Assistant
    'AIStockAssistant',
    'get_stock_info',
    'analyze_stock',
    # Strategies
    'get_strategy_api',
    'StrategyManager',
    'StrategyGenerator',
]
