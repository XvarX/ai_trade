# -*- coding: utf-8 -*-
"""使用王子战法筛选股票"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from scripts import StockScanner, EnhancedStockAPI
from strategies.custom import 王子战法
import time

def prince_strategy_wrapper(stock_detail):
    """
    王子战法筛选包装函数

    注意：由于API不提供MA历史数据，这里使用模拟数据
    实际使用时应该从历史数据计算真实的MA值
    """
    # 提取基础数据
    current_price = stock_detail.get('current_price', 0)
    open_price = stock_detail.get('open_price', 0)
    close_price = current_price  # 实时数据中current即close
    high_price = stock_detail.get('high_price', 0)
    low_price = stock_detail.get('low_price', 0)
    volume = stock_detail.get('volume', 0)
    turnover_rate = stock_detail.get('turnover_rate', 0)

    # 模拟MA数据（实际应用中需要从历史数据计算）
    # 这里使用简单的模拟：假设MA5略高于MA10（上升趋势）
    # MA5 = current * 1.005
    # MA10 = current * 1.002
    ma5 = current_price * 1.005 if current_price > 0 else 0
    ma10 = current_price * 1.002 if current_price > 0 else 0

    # 构建战法需要的stock_data
    strategy_data = {
        'current_price': current_price,
        'open_price': open_price,
        'close_price': close_price,
        'high_price': high_price,
        'low_price': low_price,
        'volume': volume,
    }

    # 战法参数
    params = {
        'ma5': ma5,
        'ma10': ma10,
        'turnover_rate': turnover_rate,
        'min_turnover': 5.0,
    }

    # 调用王子战法筛选
    return 王子战法.screen(strategy_data, **params)


def main():
    """主函数：使用王子战法筛选10支股票"""
    print("=" * 70)
    print("王子战法筛选")
    print("=" * 70)
    print("\n战法条件:")
    print("  1. 阴线（收盘价 < 开盘价）")
    print("  2. MA5 > MA10（上升趋势）")
    print("  3. 换手率 >= 5%")
    print("\n注意：由于API不提供MA历史数据，此处使用模拟数据演示")
    print("-" * 70)

    # 初始化
    scanner = StockScanner()
    api = EnhancedStockAPI()

    # 获取热门股票（按成交额排序的前200只，提高找到高换手率股票的概率）
    print("\n正在获取热门股票列表...")
    hot_stocks = scanner.get_hot_stocks(top_n=200)
    print(f"获取到 {len(hot_stocks)} 只热门股票")

    # 筛选符合条件的股票
    print("\n开始筛选...")
    qualified = []

    for i, stock in enumerate(hot_stocks, 1):
        try:
            code = stock['code']
            name = stock['name']

            # 获取详细信息（包含换手率）
            detail = api.get_stock_detail_em(code)

            # 执行王子战法筛选
            if prince_strategy_wrapper(detail):
                qualified.append(detail)
                print(f"  [{i}] ✓ {name} ({code}) - "
                      f"¥{detail['current_price']:.2f} "
                      f"({detail['change_percent']:+.2f}%) "
                      f"换手率:{detail['turnover_rate']:.2f}%")

            # 找到10只就停止
            if len(qualified) >= 10:
                print(f"\n已找到 10 只符合条件的股票，停止筛选")
                break

            # 每50只显示进度
            if i % 50 == 0:
                print(f"  进度: {i}/{len(hot_stocks)}")

            # 避免请求过快
            time.sleep(1.0)

        except Exception as e:
            print(f"  [{i}] ✗ {stock.get('name', code)}: {e}")
            continue

    # 显示结果
    print("\n" + "=" * 70)
    print(f"筛选完成！共找到 {len(qualified)} 只符合条件的股票")
    print("=" * 70)

    if qualified:
        print("\n详细信息:")
        print("-" * 70)
        for i, stock in enumerate(qualified, 1):
            print(f"\n{i}. {stock['stock_name']} ({stock['stock_code']})")
            print(f"   价格: ¥{stock['current_price']:.2f}")
            print(f"   涨跌幅: {stock['change_percent']:+.2f}%")
            print(f"   换手率: {stock['turnover_rate']:.2f}%")
            print(f"   开盘: ¥{stock['open_price']:.2f}")
            print(f"   最高: ¥{stock['high_price']:.2f}")
            print(f"   最低: ¥{stock['low_price']:.2f}")
            print(f"   成交量: {stock['volume']:,} 手")
    else:
        print("\n未找到符合条件的股票")
        print("提示：")
        print("  1. 当前市场可能没有高换手率的阴线股票")
        print("  2. 可以调整筛选条件（如降低换手率要求）")
        print("  3. MA数据为模拟值，实际使用需要历史数据")

    print("\n" + "=" * 70)

    return qualified


if __name__ == '__main__':
    # 设置UTF-8输出
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    # 执行筛选
    results = main()
