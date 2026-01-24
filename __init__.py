"""
根目录快捷导入 - Claude使用
"""
import sys
import os

# 确保可以导入所有模块
sys.path.insert(0, os.path.dirname(__file__))

from scripts.stock_api import StockAPIClient
from scripts.stock_api_enhanced import EnhancedStockAPI
from scripts.stock_scanner import StockScanner, get_all_stocks
from scripts.stock_ma_data import MADataAPI, get_stock_ma, batch_get_stock_ma
from assistant import AIStockAssistant, get_stock_info, analyze_stock
from strategies import get_strategy_api, StrategyManager, StrategyGenerator

__all__ = [
    # Core
    'StockAPIClient',
    'EnhancedStockAPI',
    'StockScanner',
    'get_all_stocks',
    # MA Data
    'MADataAPI',
    'get_stock_ma',
    'batch_get_stock_ma',
    # Assistant
    'AIStockAssistant',
    'get_stock_info',
    'analyze_stock',
    # Strategies
    'get_strategy_api',
    'StrategyManager',
    'StrategyGenerator',
]
