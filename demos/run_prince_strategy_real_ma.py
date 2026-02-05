# -*- coding: utf-8 -*-
"""使用王子战法筛选股票（含真实MA数据）

使用方法：
    python run_prince_strategy_real_ma.py --count 5  # 筛选5只股票
    python run_prince_strategy_real_ma.py            # 默认筛选10只股票
"""
import sys
import os

# 修复：添加父目录到sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# 设置UTF-8编码
from scripts.encoding_helper import auto_setup
auto_setup()

from scripts.stock_scanner import StockScanner
from scripts.stock_api_enhanced import EnhancedStockAPI
from scripts.stock_ma_data import MADataAPI
from strategies.custom import 王子战法
import time
import argparse


def prince_strategy_with_real_ma(stock_detail):
    """
    王子战法筛选函数（使用真实MA数据）

    战法条件：
    1. 阴线（收盘价 < 开盘价）
    2. MA5 > MA20（上升趋势）
    3. 换手率 >= 5%
    """
    # 提取基础数据
    current_price = stock_detail.get('current_price', 0)
    open_price = stock_detail.get('open_price', 0)
    close_price = current_price
    high_price = stock_detail.get('high_price', 0)
    low_price = stock_detail.get('low_price', 0)
    volume = stock_detail.get('volume', 0)

    # 获取真实MA数据
    ma5 = stock_detail.get('MA5')
    ma20 = stock_detail.get('MA20')  # 修复：使用MA20而不是MA10
    turnover_rate = stock_detail.get('turnover_rate', 0)

    # 如果MA数据缺失，跳过
    if ma5 is None or ma20 is None:
        return False

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
        'ma20': ma20,  # 修复：传入ma20而不是ma10
        'turnover_rate': turnover_rate,
        'min_turnover': 5.0,
    }

    # 调用王子战法筛选
    return 王子战法.screen(strategy_data, **params)


def main(target_count=10):
    """
    主函数：使用王子战法筛选指定数量的股票（含真实MA数据）

    参数:
        target_count: 目标筛选数量，默认10只
    """
    print("=" * 70)
    print(f"王子战法筛选（真实MA数据）- 目标: {target_count}只")
    print("=" * 70)
    print("\n战法条件:")
    print("  1. 阴线（收盘价 < 开盘价）")
    print("  2. MA5 > MA20（上升趋势）")  # 修复：统一为MA20
    print("  3. 换手率 >= 5%")
    print("\n数据来源: AKShare历史数据 + 东方财富实时行情")
    print("-" * 70)

    # 初始化
    scanner = StockScanner()
    realtime_api = EnhancedStockAPI()
    ma_api = MADataAPI()

    # 获取热门股票（按成交额排序的前300只）
    print("\n正在获取热门股票列表...")
    hot_stocks = scanner.get_hot_stocks(top_n=300)
    print(f"获取到 {len(hot_stocks)} 只热门股票")

    # 筛选符合条件的股票
    print(f"\n开始筛选（目标: {target_count}只）...")
    qualified = []
    failed = []  # 记录失败的股票

    for i, stock in enumerate(hot_stocks, 1):
        try:
            code = stock['code']
            name = stock['name']

            # 获取实时数据
            detail = realtime_api.get_stock_detail_em(code)

            # 获取MA数据
            ma_data = ma_api.get_current_ma(code)

            if ma_data and ma_data.get('MA5') and ma_data.get('MA20'):  # 修复：检查MA20
                # 合并数据
                detail['MA5'] = ma_data['MA5']
                detail['MA10'] = ma_data.get('MA10')
                detail['MA20'] = ma_data['MA20']  # 修复：使用MA20
                detail['MA30'] = ma_data.get('MA30')
                detail['ma_date'] = ma_data['date']

                # 执行王子战法筛选
                if prince_strategy_with_real_ma(detail):
                    qualified.append(detail)
                    print(f"  [{i}] ✓ {name} ({code}) - "
                          f"¥{detail['current_price']:.2f} "
                          f"({detail['change_percent']:+.2f}%) "
                          f"换手率:{detail['turnover_rate']:.2f}% "
                          f"MA5:{detail['MA5']:.2f} MA20:{detail['MA20']:.2f}")  # 修复：显示MA20

            # 找到目标数量就停止
            if len(qualified) >= target_count:
                print(f"\n已找到 {target_count} 只符合条件的股票，停止筛选")
                break

            # 每30只显示进度
            if i % 30 == 0:
                print(f"  进度: {i}/{len(hot_stocks)} - 已找到 {len(qualified)} 只")
                time.sleep(1.0)  # 避免请求过快
            else:
                time.sleep(1.0)  # 基本延迟

        except Exception as e:
            # 修复：添加错误日志
            failed.append({'code': stock.get('code'), 'name': stock.get('name'), 'error': str(e)})
            print(f"  [{i}] ✗ {stock.get('name')} ({stock.get('code')}) - 错误: {str(e)[:50]}")
            continue

    # 显示结果
    print("\n" + "=" * 70)
    print(f"筛选完成！共找到 {len(qualified)} 只符合条件的股票")
    if failed:
        print(f"失败: {len(failed)} 只股票")
    print("=" * 70)

    if qualified:
        print("\n详细信息:")
        print("-" * 70)
        for i, stock in enumerate(qualified, 1):
            print(f"\n{i}. {stock['stock_name']} ({stock['stock_code']})")
            print(f"   价格: ¥{stock['current_price']:.2f}")
            print(f"   涨跌幅: {stock['change_percent']:+.2f}%")
            print(f"   换手率: {stock['turnover_rate']:.2f}%")
            print(f"   MA5: ¥{stock['MA5']:.2f}")
            print(f"   MA20: ¥{stock['MA20']:.2f}")  # 修复：显示MA20
            print(f"   MA30: ¥{stock['MA30']}" if stock.get('MA30') else "   MA30: 暂无")
            print(f"   开盘: ¥{stock['open_price']:.2f}")
            print(f"   最高: ¥{stock['high_price']:.2f}")
            print(f"   最低: ¥{stock['low_price']:.2f}")
            print(f"   MA趋势: {'上升' if stock['MA5'] > stock['MA20'] else '下降'} "  # 修复：比较MA5和MA20
                  f"(MA5-MA20: {stock['MA5'] - stock['MA20']:+.2f})")
    else:
        print("\n未找到符合条件的股票")
        print("提示：当前市场可能没有同时满足以下条件的股票：")
        print("  1. 阴线（下跌）")
        print("  2. MA5 > MA20（短期均线在长期均线之上，上升趋势）")  # 修复：统一为MA20
        print("  3. 换手率 >= 5%")

    print("\n" + "=" * 70)

    return qualified


if __name__ == '__main__':
    # 设置UTF-8输出
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    # 解析命令行参数
    parser = argparse.ArgumentParser(description='使用王子战法筛选股票')
    parser.add_argument('--count', type=int, default=10, help='筛选股票数量（默认10只）')
    args = parser.parse_args()

    # 执行筛选
    results = main(target_count=args.count)
