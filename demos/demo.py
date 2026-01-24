# -*- coding: utf-8 -*-
"""
演示脚本 - 展示框架功能
"""
import sys
import io

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 导入assistant模块
sys.path.insert(0, '..')
from assistant import AIStockAssistant, get_stock_info, analyze_stock


def demo():
    print("=" * 70)
    print("A股查询框架 - 功能演示")
    print("=" * 70)
    print()

    # 演示1: 查询单个股票
    print("[演示1] 查询中国平安当前价格")
    print("-" * 70)
    info = get_stock_info('601318')
    print(info)
    print()

    # 演示2: 查询多只股票
    print("[演示2] 批量查询知名股票")
    print("-" * 70)
    assistant = AIStockAssistant()
    stocks = ['601318', '600519', '000858', '002594']
    results = assistant.query_multiple_stocks(stocks)

    print(f"{'股票名称':<12} {'代码':<10} {'价格':<12} {'涨跌幅':<10}")
    print("-" * 70)
    for r in results:
        if r['success']:
            d = r['data']
            print(f"{d['stock_name']:<12} {d['stock_code']:<10} {d['current_price']:<12.2f} {d['change_percent']:+.2f}%")
    print()

    # 演示3: 分析股票
    print("[演示3] 分析贵州茅台")
    print("-" * 70)
    analysis = analyze_stock('600519')
    print(analysis)
    print()

    print("=" * 70)
    print("演示完成！")
    print("=" * 70)


if __name__ == '__main__':
    demo()
