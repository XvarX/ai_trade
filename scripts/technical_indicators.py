"""
技术指标计算模块
实现均线、K线形态、换手率等技术指标
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class TechnicalIndicators:
    """技术指标计算类"""

    @staticmethod
    def calculate_ma(prices: List[float], period: int) -> List[float]:
        """
        计算移动平均线
        prices: 价格列表
        period: 周期（如5, 10, 20, 30, 60）
        返回MA值列表（前面period-1个值为None）
        """
        if len(prices) < period:
            return [None] * len(prices)

        ma_values = []
        for i in range(len(prices)):
            if i < period - 1:
                ma_values.append(None)
            else:
                ma = sum(prices[i-period+1:i+1]) / period
                ma_values.append(round(ma, 2))

        return ma_values

    @staticmethod
    def is_bullish_trend(ma5: float, ma10: float, ma20: float, ma30: float) -> bool:
        """
        判断是否为上升趋势（均线多头排列）
        条件：MA5 > MA10 > MA20 > MA30
        """
        if None in [ma5, ma10, ma20, ma30]:
            return False
        return ma5 > ma10 > ma20 > ma30

    @staticmethod
    def is_bearish_candle(open_price: float, close_price: float, high: float, low: float) -> bool:
        """
        判断是否为阴线
        阴线定义：收盘价低于开盘价
        """
        return close_price < open_price

    @staticmethod
    def is_bullish_candle(open_price: float, close_price: float, high: float, low: float) -> bool:
        """
        判断是否为阳线
        阳线定义：收盘价高于开盘价
        """
        return close_price > open_price

    @staticmethod
    def calculate_turnover_rate(volume: int, circulating_shares: int) -> float:
        """
        计算换手率
        volume: 成交量（手）
        circulating_shares: 流通股本（手）
        返回换手率百分比
        """
        if circulating_shares == 0:
            return 0.0
        return round((volume / circulating_shares) * 100, 2)

    @staticmethod
    def is_high_turnover(turnover_rate: float, threshold: float = 5.0) -> bool:
        """
        判断换手率是否较高
        threshold: 换手率阈值（默认5%）
        """
        return turnover_rate >= threshold

    @staticmethod
    def calculate_body_size(open_price: float, close_price: float) -> float:
        """
        计算K线实体大小（绝对值）
        """
        return abs(close_price - open_price)

    @staticmethod
    def calculate_shadow(open_price: float, close_price: float, high: float, low: float) -> Tuple[float, float]:
        """
        计算上下影线
        返回：(上影线, 下影线)
        """
        upper_shadow = high - max(open_price, close_price)
        lower_shadow = min(open_price, close_price) - low
        return upper_shadow, lower_shadow

    @staticmethod
    def is_doji(open_price: float, close_price: float, threshold: float = 0.01) -> bool:
        """
        判断是否为十字星（开盘价和收盘价几乎相同）
        threshold: 实体大小阈值（相对于价格）
        """
        body = abs(close_price - open_price)
        return body <= (open_price * threshold) if open_price > 0 else False

    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 20) -> float:
        """
        计算波动率（标准差）
        """
        if len(prices) < period:
            return 0.0

        recent_prices = prices[-period:]
        return round(np.std(recent_prices), 2)

    @staticmethod
    def is_price_near_ma(price: float, ma: float, tolerance: float = 0.02) -> bool:
        """
        判断价格是否接近均线
        tolerance: 容差百分比（默认2%）
        """
        if ma is None or ma == 0:
            return False
        ratio = abs(price - ma) / ma
        return ratio <= tolerance


class StockScreener:
    """股票筛选器"""

    def __init__(self):
        self.indicators = TechnicalIndicators()

    def screen_bearish_high_turnover_uptrend(
        self,
        stock_data: Dict,
        ma5: float,
        ma10: float,
        ma20: float,
        ma30: float,
        turnover_rate: float,
        min_turnover: float = 5.0
    ) -> bool:
        """
        筛选：阴线 + 换手率较高 + 上升趋势

        条件：
        1. 今日为阴线
        2. 换手率 >= min_turnover（默认5%）
        3. MA5 > MA10 > MA20 > MA30（均线多头排列）

        stock_data: 包含 open, close, high, low 的字典
        """
        open_price = stock_data.get('open_price', 0)
        close_price = stock_data.get('current_price', 0)
        high = stock_data.get('high_price', 0)
        low = stock_data.get('low_price', 0)

        # 判断是否为阴线
        is_bearish = self.indicators.is_bearish_candle(open_price, close_price, high, low)

        # 判断换手率是否较高
        is_high_turnover = self.indicators.is_high_turnover(turnover_rate, min_turnover)

        # 判断是否为上升趋势
        is_uptrend = self.indicators.is_bullish_trend(ma5, ma10, ma20, ma30)

        return is_bearish and is_high_turnover and is_uptrend

    def screen_golden_cross(self, ma5: float, ma10: float, prev_ma5: float = None, prev_ma10: float = None) -> bool:
        """
        筛选：金叉（短期均线上穿长期均线）
        如果提供前一日数据，则判断是否刚发生金叉
        """
        if ma5 is None or ma10 is None:
            return False

        # 当前MA5 > MA10
        if ma5 <= ma10:
            return False

        # 如果有前一日数据，判断是否刚发生金叉
        if prev_ma5 is not None and prev_ma10 is not None:
            return prev_ma5 <= prev_ma10

        return True

    def screen_death_cross(self, ma5: float, ma10: float, prev_ma5: float = None, prev_ma10: float = None) -> bool:
        """
        筛选：死叉（短期均线下穿长期均线）
        """
        if ma5 is None or ma10 is None:
            return False

        # 当前MA5 < MA10
        if ma5 >= ma10:
            return False

        # 如果有前一日数据，判断是否刚发生死叉
        if prev_ma5 is not None and prev_ma10 is not None:
            return prev_ma5 >= prev_ma10

        return True

    def get_screening_criteria_description(self) -> str:
        """
        获取筛选条件说明
        """
        return """
股票筛选条件说明：

1. 阴线 + 高换手 + 上升趋势
   - 今日K线为阴线（收盘价 < 开盘价）
   - 换手率 >= 5%（可自定义）
   - 均线多头排列：MA5 > MA10 > MA20 > MA30

2. 金叉
   - MA5 上穿 MA10
   - 可检测刚发生的金叉

3. 死叉
   - MA5 下穿 MA10
   - 可检测刚发生的死叉

4. 上升趋势
   - 短期均线在中长期均线之上
   - MA5 > MA10 > MA20 > MA30

5. 下降趋势
   - 短期均线在中长期均线之下
   - MA5 < MA10 < MA20 < MA30
        """.strip()


if __name__ == '__main__':
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    # 测试代码
    indicators = TechnicalIndicators()

    # 测试MA计算
    prices = [10.5, 10.8, 11.2, 11.0, 11.5, 11.8, 12.0, 11.9, 12.2, 12.5]
    print("=== 测试MA计算 ===")
    print(f"价格序列: {prices}")
    print(f"MA5: {indicators.calculate_ma(prices, 5)}")
    print(f"MA10: {indicators.calculate_ma(prices, 10)}")

    # 测试均线多头排列
    print("\n=== 测试均线多头排列 ===")
    print(f"MA5=12.2, MA10=11.8, MA20=11.5, MA30=11.0 是否多头排列: {indicators.is_bullish_trend(12.2, 11.8, 11.5, 11.0)}")

    # 测试阴线判断
    print("\n=== 测试K线形态 ===")
    print(f"开盘=11.5, 收盘=11.2 是否为阴线: {indicators.is_bearish_candle(11.5, 11.2, 11.6, 11.1)}")
    print(f"开盘=11.5, 收盘=11.8 是否为阳线: {indicators.is_bullish_candle(11.5, 11.8, 11.9, 11.4)}")

    # 测试换手率
    print("\n=== 测试换手率 ===")
    turnover = indicators.calculate_turnover_rate(5000000, 100000000)  # 5万手/1亿股
    print(f"成交量=5万手, 流通股本=1亿股, 换手率={turnover}%")
    print(f"换手率是否较高(>5%): {indicators.is_high_turnover(turnover, 5.0)}")

    # 测试筛选器
    print("\n=== 测试股票筛选器 ===")
    screener = StockScreener()
    stock = {
        'open_price': 12.5,
        'current_price': 12.2,
        'high_price': 12.6,
        'low_price': 12.1
    }
    result = screener.screen_bearish_high_turnover_uptrend(
        stock, ma5=12.3, ma10=12.0, ma20=11.8, ma30=11.5,
        turnover_rate=6.5, min_turnover=5.0
    )
    print(f"筛选结果（阴线+高换手+上升趋势）: {result}")
