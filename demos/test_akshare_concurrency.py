# -*- coding: utf-8 -*-
"""测试AKShare并发限制

测试不同并发级别下的请求成功率
"""
import sys
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from scripts.stock_ma_data import MADataAPI


def test_single_stock(code: str, api: MADataAPI) -> dict:
    """测试单个股票"""
    start_time = time.time()
    try:
        result = api.get_current_ma(code)
        elapsed = time.time() - start_time
        if result and result.get('MA5'):
            return {
                'code': code,
                'success': True,
                'time': elapsed,
                'ma5': result.get('MA5')
            }
        else:
            return {
                'code': code,
                'success': False,
                'time': elapsed,
                'error': 'No data returned'
            }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            'code': code,
            'success': False,
            'time': elapsed,
            'error': str(e)[:50]
        }


def test_concurrency_level(stock_codes: list, concurrency: int, api: MADataAPI) -> dict:
    """测试特定并发级别"""
    print(f"\n{'='*60}")
    print(f"测试并发级别: {concurrency}")
    print(f"测试股票数: {len(stock_codes)}")
    print(f"{'='*60}")

    start_time = time.time()
    results = []
    failed = []

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(test_single_stock, code, api): code for code in stock_codes}

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

            if not result['success']:
                failed.append(result)

    total_time = time.time() - start_time
    success_count = sum(1 for r in results if r['success'])
    success_rate = (success_count / len(results)) * 100
    avg_time = sum(r['time'] for r in results) / len(results)

    print(f"\n结果:")
    print(f"  总耗时: {total_time:.2f}秒")
    print(f"  成功: {success_count}/{len(results)} ({success_rate:.1f}%)")
    print(f"  失败: {len(failed)}")
    print(f"  平均响应时间: {avg_time:.2f}秒")

    if failed:
        print(f"\n失败示例 (前5个):")
        for f in failed[:5]:
            print(f"  {f['code']}: {f.get('error', 'Unknown')}")

    return {
        'concurrency': concurrency,
        'total_time': total_time,
        'success_rate': success_rate,
        'avg_time': avg_time,
        'failed_count': len(failed)
    }


def main():
    """主测试函数"""
    print("="*60)
    print("AKShare 并发限制测试")
    print("="*60)

    # 初始化API
    api = MADataAPI()

    # 测试股票列表（热门股票）
    test_codes = [
        '600519', '601318', '000001', '002594', '300750',
        '600036', '601328', '000858', '002475', '600276',
        '601166', '000002', '600000', '601398', '601939',
        '600887', '002236', '300059', '601888', '000333'
    ]

    print(f"\n测试股票列表 (共{len(test_codes)}只):")
    print(f"{test_codes[:10]}...")

    # 测试不同并发级别
    concurrency_levels = [1, 3, 5, 10, 15, 20]
    all_results = []

    for level in concurrency_levels:
        result = test_concurrency_level(test_codes, level, api)
        all_results.append(result)

        # 如果成功率太低，就不继续测试更高的并发了
        if result['success_rate'] < 50:
            print(f"\n⚠️  成功率低于50%，停止测试更高并发级别")
            break

        # 等待一段时间，避免连续测试影响结果
        time.sleep(2)

    # 汇总结果
    print(f"\n{'='*60}")
    print("测试结果汇总")
    print(f"{'='*60}")
    print(f"\n{'并发数':<8} {'成功率':<10} {'平均响应':<12} {'总耗时':<10}")
    print("-" * 50)

    for r in all_results:
        print(f"{r['concurrency']:<8} {r['success_rate']:>6.1f}%    "
              f"{r['avg_time']:>6.2f}s       {r['total_time']:>5.2f}s")

    # 推荐最佳并发数
    print("\n" + "="*60)
    print("建议:")
    best = max(all_results, key=lambda x: x['success_rate'] * x['concurrency'])
    print(f"  最佳并发数: {best['concurrency']} (成功率: {best['success_rate']:.1f}%)")
    print(f"  建议在生产环境中使用并发数 ≤ {int(best['concurrency'] * 0.8)}")
    print("="*60)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    main()
