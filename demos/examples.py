"""
使用示例 - 展示如何使用A股查询框架
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistant import AIStockAssistant, get_stock_info, analyze_stock
from scripts.technical_indicators import TechnicalIndicators, StockScreener


def example_1_basic_query():
    """示例1: 基础查询 - 查询单个股票价格"""
    print("=" * 60)
    print("示例1: 查询中国平安价格")
    print("=" * 60)

    # 方式1: 使用快捷函数
    result = get_stock_info('601318')
    print(result)
    print()

    # 方式2: 使用AI助手对象
    assistant = AIStockAssistant()
    result = assistant.query_stock('601318')
    if result['success']:
        print(result['formatted'])
    print()


def example_2_analyze_stock():
    """示例2: 分析股票详细信息"""
    print("=" * 60)
    print("示例2: 分析股票详细信息")
    print("=" * 60)

    assistant = AIStockAssistant()
    result = assistant.analyze_stock('600519')  # 贵州茅台

    if result['success']:
        print(result['formatted_summary'])
    print()


def example_3_batch_query():
    """示例3: 批量查询多只股票"""
    print("=" * 60)
    print("示例3: 批量查询股票")
    print("=" * 60)

    assistant = AIStockAssistant()

    # 知名股票列表
    famous_stocks = {
        '601318': '中国平安',
        '600519': '贵州茅台',
        '000858': '五粮液',
        '002594': '比亚迪',
        '300750': '宁德时代',
        '000001': '平安银行',
        '600036': '招商银行'
    }

    results = assistant.query_multiple_stocks(list(famous_stocks.keys()))

    print(f"{'股票名称':<10} {'代码':<10} {'价格':<10} {'涨跌幅':<10}")
    print("-" * 60)

    for result in results:
        if result['success']:
            data = result['data']
            name = data['stock_name']
            code = data['stock_code']
            price = f"¥{data['current_price']:.2f}"
            change = f"{data['change_percent']:+.2f}%"
            print(f"{name:<10} {code:<10} {price:<10} {change:<10}")
    print()


def example_4_market_summary():
    """示例4: 市场概览"""
    print("=" * 60)
    print("示例4: 市场概览")
    print("=" * 60)

    assistant = AIStockAssistant()

    # 银行股
    bank_stocks = ['600000', '600036', '601318', '601328', '601166', '000001']
    summary = assistant.get_market_summary(bank_stocks)

    print(summary['summary'])
    print()


def example_5_technical_indicators():
    """示例5: 技术指标计算"""
    print("=" * 60)
    print("示例5: 技术指标演示")
    print("=" * 60)

    indicators = TechnicalIndicators()

    # 模拟价格序列
    prices = [45.0, 45.5, 46.0, 45.8, 46.5, 47.0, 47.5, 47.2, 47.8, 48.5]

    print(f"价格序列: {prices}")
    print()

    # 计算均线
    ma5 = indicators.calculate_ma(prices, 5)
    ma10 = indicators.calculate_ma(prices, 10)
    ma20 = indicators.calculate_ma(prices, 20)

    print(f"MA5: {ma5[-1] if ma5[-1] else 'N/A'}")
    print(f"MA10: {ma10[-1] if ma10[-1] else 'N/A'}")
    print(f"MA20: {ma20[-1] if ma20[-1] else 'N/A'}")
    print()

    # 判断趋势
    latest = {
        'ma5': ma5[-1],
        'ma10': ma10[-1],
        'ma20': ma20[-1]
    }

    if all(v is not None for v in latest.values()):
        if latest['ma5'] > latest['ma10'] > latest['ma20']:
            print("趋势判断: 多头排列（上升趋势）")
        elif latest['ma5'] < latest['ma10'] < latest['ma20']:
            print("趋势判断: 空头排列（下降趋势）")
        else:
            print("趋势判断: 震荡走势")
    print()


def example_6_candle_analysis():
    """示例6: K线形态分析"""
    print("=" * 60)
    print("示例6: K线形态分析")
    print("=" * 60)

    assistant = AIStockAssistant()
    indicators = TechnicalIndicators()

    # 查询股票并分析K线
    result = assistant.query_stock('601318')

    if result['success']:
        data = result['data']
        open_price = data['open_price']
        close = data['current_price']
        high = data['high_price']
        low = data['low_price']

        print(f"股票: {data['stock_name']} ({data['stock_code']})")
        print(f"开盘: ¥{open_price:.2f}")
        print(f"收盘: ¥{close:.2f}")
        print(f"最高: ¥{high:.2f}")
        print(f"最低: ¥{low:.2f}")
        print()

        # 判断K线类型
        if indicators.is_bearish_candle(open_price, close, high, low):
            print("K线类型: 阴线 📉")
        elif indicators.is_bullish_candle(open_price, close, high, low):
            print("K线类型: 阳线 📈")
        else:
            print("K线类型: 十字星或平盘 ➡️")

        # 计算实体大小
        body = indicators.calculate_body_size(open_price, close)
        upper_shadow, lower_shadow = indicators.calculate_shadow(open_price, close, high, low)

        print(f"实体大小: ¥{body:.2f}")
        print(f"上影线: ¥{upper_shadow:.2f}")
        print(f"下影线: ¥{lower_shadow:.2f}")
    print()


def example_7_screener_demo():
    """示例7: 股票筛选器演示"""
    print("=" * 60)
    print("示例7: 股票筛选器")
    print("=" * 60)

    screener = StockScreener()

    # 模拟一只符合筛选条件的股票
    mock_stock = {
        'stock_code': '600XXX',
        'stock_name': '测试股票',
        'open_price': 50.0,
        'current_price': 49.2,  # 阴线（收盘 < 开盘）
        'high_price': 50.5,
        'low_price': 49.0
    }

    # 模拟均线数据（多头排列）
    ma5 = 49.5
    ma10 = 49.0
    ma20 = 48.5
    ma30 = 48.0

    # 模拟换手率
    turnover_rate = 6.5  # 高于5%

    # 执行筛选
    is_qualified = screener.screen_bearish_high_turnover_uptrend(
        mock_stock,
        ma5=ma5,
        ma10=ma10,
        ma20=ma20,
        ma30=ma30,
        turnover_rate=turnover_rate,
        min_turnover=5.0
    )

    print(f"股票: {mock_stock['stock_name']}")
    print(f"当前价格: ¥{mock_stock['current_price']:.2f}")
    print(f"换手率: {turnover_rate}%")
    print(f"均线: MA5={ma5}, MA10={ma10}, MA20={ma20}, MA30={ma30}")
    print()

    if is_qualified:
        print("✓ 符合条件: 阴线 + 高换手 + 上升趋势")
        print("  - 今日收阴线")
        print("  - 换手率 >= 5%")
        print("  - MA5 > MA10 > MA20 > MA30（多头排列）")
    else:
        print("✗ 不符合筛选条件")
    print()


def example_8_ai_conversation():
    """示例8: 模拟AI对话场景"""
    print("=" * 60)
    print("示例8: AI对话场景")
    print("=" * 60)

    assistant = AIStockAssistant()

    # 场景1: 用户问股票价格
    print("用户: 现在中国平安什么价格？")
    print(f"AI: {get_stock_info('601318')}")
    print()

    # 场景2: 用户要求分析
    print("用户: 帮我分析一下贵州茅台")
    print(f"AI: {analyze_stock('600519')}")
    print()

    # 场景3: 用户要求筛选
    print("用户: 找几只涨幅不错的银行股")
    assistant2 = AIStockAssistant()
    bank_stocks = ['600000', '600036', '601318', '601166', '000001']
    results = assistant2.query_multiple_stocks(bank_stocks)

    rising_stocks = [
        r for r in results
        if r['success'] and r['data']['change_percent'] > 0
    ]

    if rising_stocks:
        print("AI: 以下银行股今日上涨：")
        for r in rising_stocks[:3]:
            d = r['data']
            print(f"  - {d['stock_name']}: ¥{d['current_price']:.2f} ({d['change_percent']:+.2f}%)")
    print()


def main():
    """运行所有示例"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "A股查询框架使用示例" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    examples = [
        example_1_basic_query,
        example_2_analyze_stock,
        example_3_batch_query,
        example_4_market_summary,
        example_5_technical_indicators,
        example_6_candle_analysis,
        example_7_screener_demo,
        example_8_ai_conversation
    ]

    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"示例 {i} 执行出错: {e}")
            print()

        if i < len(examples):
            input("按回车继续下一个示例...")

    print("=" * 60)
    print("所有示例运行完毕！")
    print("=" * 60)


if __name__ == '__main__':
    main()
