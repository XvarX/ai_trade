"""
战法名称: 王子战法
战法描述: 阴线且MA5大于MA10且换手率大于5%
作者: AI
版本: 1.0.0
"""

# 战法元数据
STRATEGY_NAME = "王子战法"
STRATEGY_DESCRIPTION = "阴线且MA5大于MA10且换手率大于5%"
STRATEGY_AUTHOR = "AI"
STRATEGY_VERSION = "1.0.0"
STRATEGY_CATEGORY = "custom"
STRATEGY_TAGS = ["筛选", "自定义"]


def get_default_params():
    """获取默认参数"""
    return {
        'ma5': None,  # 需要提供
        'ma10': None,  # 需要提供
        'min_turnover': 5.0,
    }


def get_params_schema():
    """获取参数模式"""
    return {
        'ma5': {'type': 'float', 'description': 'ma5参数'},
        'ma10': {'type': 'float', 'description': 'ma10参数'},
        'min_turnover': {'type': 'float', 'description': 'min_turnover参数'},
    }


def screen(stock_data, **params):
    """
    战法筛选函数

    参数:
        stock_data: 股票数据字典，包含:
            - current_price: 当前价格
            - open_price: 开盘价
            - close_price: 收盘价
            - high_price: 最高价
            - low_price: 最低价
            - volume: 成交量
            - turnover_rate: 换手率
            - ma5, ma10, ma20, ma30: 均线值（如果有）
        **params: 战法参数

    返回:
        True: 符合战法条件
        False: 不符合
    """
    # 提取常用字段
    current_price = stock_data.get('current_price', 0)
    open_price = stock_data.get('open_price', 0)
    close_price = stock_data.get('current_price', 0)  # 实时数据中current即close
    high_price = stock_data.get('high_price', 0)
    low_price = stock_data.get('low_price', 0)
    volume = stock_data.get('volume', 0)
    turnover_rate = params.get('turnover_rate', 0)

    # 筛选条件检查
    conditions_met = []

    # 均线条件: MA5 > MA10
    ma5 = params.get('ma5', 0)
    ma10 = params.get('ma10', 0)
    conditions_met.append(ma5 > ma10)


    # K线形态: 阴线
    conditions_met.append(close_price < open_price)


    # 换手率条件: 换手率 >= 5.0%
    conditions_met.append(turnover_rate >= 5.0)


    # 返回是否所有条件都满足
    return all(conditions_met)

    # 所有条件都满足
    return True
