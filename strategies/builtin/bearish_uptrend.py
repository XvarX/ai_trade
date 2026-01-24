"""
战法名称: 阴线高换手上升趋势
战法描述: 今日收阴线但换手率较高，且均线呈多头排列（MA5>MA10>MA20>MA30），可能是上升趋势中的回调机会
作者: System
版本: 1.0.0
"""

# 战法元数据
STRATEGY_NAME = "阴线高换手上升趋势"
STRATEGY_DESCRIPTION = "今日收阴线但换手率较高，且均线呈多头排列，可能是上升趋势中的回调机会"
STRATEGY_AUTHOR = "System"
STRATEGY_VERSION = "1.0.0"
STRATEGY_CATEGORY = "builtin"
STRATEGY_TAGS = ["阴线", "高换手", "上升趋势", "回调"]


def get_default_params():
    """获取默认参数"""
    return {
        'min_turnover': 5.0,  # 最低换手率（%）
        'ma5': 0,
        'ma10': 0,
        'ma20': 0,
        'ma30': 0,
        'turnover_rate': 0
    }


def get_params_schema():
    """获取参数模式"""
    return {
        'min_turnover': {'type': 'float', 'description': '最低换手率（百分比），默认5%'},
        'ma5': {'type': 'float', 'description': '5日均线值'},
        'ma10': {'type': 'float', 'description': '10日均线值'},
        'ma20': {'type': 'float', 'description': '20日均线值'},
        'ma30': {'type': 'float', 'description': '30日均线值'},
        'turnover_rate': {'type': 'float', 'description': '实际换手率'}
    }


def screen(stock_data, **params):
    """
    战法筛选函数

    筛选条件:
    1. 今日收阴线（收盘价 < 开盘价）
    2. 换手率 >= min_turnover（默认5%）
    3. 均线多头排列：MA5 > MA10 > MA20 > MA30

    参数:
        stock_data: 股票数据
        **params: 战法参数

    返回:
        True: 符合战法条件
        False: 不符合
    """
    # 提取常用字段
    current_price = stock_data.get('current_price', 0)
    open_price = stock_data.get('open_price', 0)
    close_price = current_price
    high_price = stock_data.get('high_price', 0)
    low_price = stock_data.get('low_price', 0)
    volume = stock_data.get('volume', 0)

    # 获取参数
    min_turnover = params.get('min_turnover', 5.0)
    ma5 = params.get('ma5', 0)
    ma10 = params.get('ma10', 0)
    ma20 = params.get('ma20', 0)
    ma30 = params.get('ma30', 0)
    turnover_rate = params.get('turnover_rate', 0)

    # 条件1: 阴线
    is_bearish = close_price < open_price
    if not is_bearish:
        return False

    # 条件2: 换手率足够高
    has_high_turnover = turnover_rate >= min_turnover
    if not has_high_turnover:
        return False

    # 条件3: 均线多头排列
    is_uptrend = ma5 > ma10 > ma20 > ma30
    if not is_uptrend:
        return False

    # 所有条件都满足
    return True
