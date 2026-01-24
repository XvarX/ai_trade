# -*- coding: utf-8 -*-
"""
MA数据使用示例 - 展示如何获取和使用MA均线数据
"""
import sys
import os
import io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from a_stock_query_v2 import get_stock_ma, MADataAPI, batch_get_stock_ma, EnhancedStockAPI


def example_1_get_single_stock_ma():
    """示例1: 获取单只股票的MA数据"""
    print("=" * 70)
    print("示例1: 获取中国平安(601318)的MA数据")
    print("=" * 70)

    ma_data = get_stock_ma('601318')

    if ma_data:
        print(f"日期: {ma_data['date']}")
        print(f"当前价: ¥{ma_data['current_price']}")
        print(f"MA5: ¥{ma_data['MA5']}")
        print(f"MA10: ¥{ma_data['MA10']}")
        print(f"MA20: ¥{ma_data['MA20']}")
        print(f"MA30: ¥{ma_data['MA30']}")

        # 判断趋势
        if ma_data['MA5'] and ma_data['MA10'] and ma_data['MA20']:
            if ma_data['MA5'] > ma_data['MA10'] > ma_data['MA20']:
                print("\n趋势: 多头排列（上升趋势）")
            elif ma_data['MA5'] < ma_data['MA10'] < ma_data['MA20']:
                print("\n趋势: 空头排列（下降趋势）")
            else:
                print("\n趋势: 震荡走势")
    else:
        print("获取MA数据失败")

    print()


def example_2_batch_get_ma():
    """示例2: 批量获取多只股票的MA数据"""
    print("=" * 70)
    print("示例2: 批量获取知名股票的MA数据")
    print("=" * 70)

    symbols = ['601318', '600519', '000001', '002594']
    names = ['中国平安', '贵州茅台', '平安银行', '比亚迪']

    results = batch_get_stock_ma(symbols, delay=0.5)

    print(f"{'股票名称':<12} {'代码':<10} {'MA5':<10} {'MA10':<10} {'MA20':<10}")
    print("-" * 70)

    for symbol, name in zip(symbols, names):
        if symbol in results:
            ma = results[symbol]
            print(f"{name:<12} {symbol:<10} "
                  f"¥{ma['MA5'] or 0:<9.2f} "
                  f"¥{ma['MA10'] or 0:<9.2f} "
                  f"¥{ma['MA20'] or 0:<9.2f}")

    print()


def example_3_combine_realtime_and_ma():
    """示例3: 结合实时行情和MA数据进行战法筛选"""
    print("=" * 70)
    print("示例3: 结合实时行情和MA数据（王子战法）")
    print("=" * 70)

    # 获取实时行情
    realtime_api = EnhancedStockAPI()
    stock = realtime_api.get_stock_detail_em('601318')

    print(f"股票: {stock['stock_name']} ({stock['stock_code']})")
    print(f"实时价格: ¥{stock['current_price']:.2f}")
    print(f"涨跌幅: {stock['change_percent']:+.2f}%")
    print(f"换手率: {stock['turnover_rate']:.2f}%")
    print()

    # 获取MA数据
    ma_data = get_stock_ma('601318')

    if ma_data:
        print("MA数据:")
        print(f"  MA5: ¥{ma_data['MA5']:.2f}")
        print(f"  MA10: ¥{ma_data['MA10']:.2f}")
        print(f"  MA20: ¥{ma_data['MA20']:.2f}")
        print()

        # 王子战法筛选
        is_bearish = stock['current_price'] < stock['open_price']  # 阴线
        is_uptrend = ma_data['MA5'] > ma_data['MA10']  # MA5 > MA10
        is_high_turnover = stock['turnover_rate'] >= 5.0  # 换手率 >= 5%

        print("王子战法筛选:")
        print(f"  阴线: {'✓' if is_bearish else '✗'} "
              f"(开盘: ¥{stock['open_price']:.2f}, 收盘: ¥{stock['current_price']:.2f})")
        print(f"  MA5 > MA10: {'✓' if is_uptrend else '✗'} "
              f"(MA5-MA10: {ma_data['MA5'] - ma_data['MA10']:+.2f})")
        print(f"  换手率 >= 5%: {'✓' if is_high_turnover else '✗'} "
              f"(换手率: {stock['turnover_rate']:.2f}%)")
        print()

        if is_bearish and is_uptrend and is_high_turnover:
            print("✓ 符合王子战法条件！")
        else:
            print("✗ 不符合王子战法条件")

    print()


def example_4_use_ma_api_class():
    """示例4: 使用MADataAPI类的高级功能"""
    print("=" * 70)
    print("示例4: 使用MADataAPI获取完整数据（实时+MA）")
    print("=" * 70)

    ma_api = MADataAPI()

    # 获取含MA的完整数据
    full_data = ma_api.get_stock_with_ma_enhanced('601318')

    if full_data:
        print(f"股票: {full_data['stock_name']} ({full_data['stock_code']})")
        print()
        print("实时行情:")
        print(f"  价格: ¥{full_data['current_price']:.2f}")
        print(f"  涨跌幅: {full_data['change_percent']:+.2f}%")
        print(f"  换手率: {full_data['turnover_rate']:.2f}%")
        print()
        print("MA均线:")
        print(f"  MA5: ¥{full_data['MA5']}")
        print(f"  MA10: ¥{full_data['MA10']}")
        print(f"  MA20: ¥{full_data['MA20']}")
        print(f"  MA30: ¥{full_data['MA30']}")
        print(f"  (数据日期: {full_data.get('ma_date', 'N/A')})")

    print()


def main():
    """运行所有示例"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "MA数据使用示例" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print("注意: MA数据需要AKShare库，首次运行会自动安装")
    print()

    examples = [
        example_1_get_single_stock_ma,
        example_2_batch_get_ma,
        example_3_combine_realtime_and_ma,
        example_4_use_ma_api_class,
    ]

    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"示例 {i} 执行出错: {e}")
            import traceback
            traceback.print_exc()
            print()

        if i < len(examples):
            input("按回车继续下一个示例...")

    print("=" * 70)
    print("所有示例运行完毕！")
    print("=" * 70)


if __name__ == '__main__':
    main()
