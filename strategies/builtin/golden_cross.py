"""
战法名称: 金叉战法
战法描述: MA5上穿MA10形成金叉，短期趋势转强
作者: System
版本: 1.0.0
"""

# 战法元数据
STRATEGY_NAME = "金叉战法"
STRATEGY_DESCRIPTION = "MA5上穿MA10形成金叉，短期趋势转强买入信号"
STRATEGY_AUTHOR = "System"
STRATEGY_VERSION = "1.0.0"
STRATEGY_CATEGORY = "builtin"
STRATEGY_TAGS = ["金叉", "均线", "买入信号"]


def get_default_params():
    """获取默认参数"""
    return {
        'ma5': 0,
        'ma10': 0,
        'prev_ma5': 0,
        'prev_ma10': 0
    }


def get_params_schema():
    """获取参数模式"""
    return {
        'ma5': {'type': 'float', 'description': '当日MA5'},
        'ma10': {'type': 'float', 'description': '当日MA10'},
        'prev_ma5': {'type': 'float', 'description': '前一日MA5（可选，用于判断刚发生金叉）'},
        'prev_ma10': {'type': 'float', 'description': '前一日MA10（可选，用于判断刚发生金叉）'}
    }


def screen(stock_data, **params):
    """
    战法筛选函数

    筛选条件:
    1. MA5 > MA10（金叉）
    2. 如果提供前一日数据，则判断是否刚发生金叉

    参数:
        stock_data: 股票数据
        **params: 战法参数

    返回:
        True: 符合金叉条件
        False: 不符合
    """
    # 获取参数
    ma5 = params.get('ma5', 0)
    ma10 = params.get('ma10', 0)
    prev_ma5 = params.get('prev_ma5', None)
    prev_ma10 = params.get('prev_ma10', None)

    # 基本金叉条件：MA5 > MA10
    if ma5 <= ma10:
        return False

    # 如果有前一日数据，判断是否刚发生金叉
    if prev_ma5 is not None and prev_ma10 is not None:
        # 前一天MA5 <= MA10，今天MA5 > MA10，说明刚发生金叉
        if prev_ma5 > prev_ma10:
            return False  # 之前就是金叉，不是刚发生

    return True
