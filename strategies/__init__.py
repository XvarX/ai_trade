"""
战法系统模块 - 独立的战法管理框架
"""
from .strategy_manager import StrategyManager, get_strategy_manager
from .strategy_generator import StrategyGenerator, generate_strategy
from .strategy_api import StrategyAPI, get_strategy_api

__all__ = [
    'StrategyManager',
    'get_strategy_manager',
    'StrategyGenerator',
    'generate_strategy',
    'StrategyAPI',
    'get_strategy_api',
]
