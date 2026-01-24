"""
全市场股票扫描器
支持获取A股完整列表并批量筛选
"""
import requests
import time
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from typing import List, Dict, Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


class StockScanner:
    """全市场股票扫描器"""

    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_all_stocks(self, limit: Optional[int] = None, use_pagination: bool = True) -> List[Dict]:
        """
        获取所有A股列表

        参数:
            limit: 限制返回数量，None表示全部
            use_pagination: 是否使用分页（默认True，可获取完整数据）

        返回:
            股票列表，每个元素包含 {code, name, market}
        """
        url = 'http://80.push2.eastmoney.com/api/qt/clist/get'

        # A股市场代码
        # m:0+t:6 - 深市主板
        # m:0+t:80 - 深市中小板
        # m:0+t:81 - 深市创业板
        # m:1+t:2 - 沪市主板
        # m:1+t:23 - 沪市科创板
        fs = 'm:0+t:6,m:0+t:80,m:0+t:81,m:1+t:2,m:1+t:23'

        # 如果不使用分页，使用单次请求
        if not use_pagination:
            page_size = limit if limit else 100
            params = {
                'pn': '1',
                'pz': str(page_size),
                'po': '1',
                'np': '1',
                'fltt': '2',
                'invt': '2',
                'fid': 'f62',
                'fs': fs,
                'fields': 'f12,f13,f14,f2,f3,f4,f5,f6',
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b'
            }

            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                data = response.json()

                if not data.get('data'):
                    return []

                stocks = []
                for item in data['data']['diff']:
                    stocks.append({
                        'code': item.get('f12', ''),
                        'name': item.get('f14', ''),
                        'market': item.get('f13', ''),
                        'current': item.get('f2', 0) / 100,
                        'change_percent': item.get('f3', 0) / 100,
                        'change_amount': item.get('f4', 0) / 100,
                        'volume': item.get('f5', 0),
                        'turnover': item.get('f6', 0),
                    })

                return stocks

            except Exception as e:
                print(f"获取股票列表失败: {e}")
                return []

        # 使用分页获取完整数据
        all_stocks = []
        page = 1
        page_size = 500  # 每页请求500条（但API最多返回100条）

        while True:
            params = {
                'pn': str(page),
                'pz': str(page_size),
                'po': '1',
                'np': '1',
                'fltt': '2',
                'invt': '2',
                'fid': 'f62',
                'fs': fs,
                'fields': 'f12,f13,f14,f2,f3,f4,f5,f6',
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b'
            }

            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                data = response.json()

                if not data.get('data') or not data['data'].get('diff'):
                    break

                items = data['data']['diff']
                if not items:
                    break

                for item in items:
                    all_stocks.append({
                        'code': item.get('f12', ''),
                        'name': item.get('f14', ''),
                        'market': item.get('f13', ''),
                        'current': item.get('f2', 0) / 100,
                        'change_percent': item.get('f3', 0) / 100,
                        'change_amount': item.get('f4', 0) / 100,
                        'volume': item.get('f5', 0),
                        'turnover': item.get('f6', 0),
                    })

                # API限制：每次最多返回100条
                # 如果返回少于100条，说明已经是最后一页
                if len(items) < 100:
                    break

                # 如果设置了limit且已获取足够数量
                if limit and len(all_stocks) >= limit:
                    all_stocks = all_stocks[:limit]
                    break

                page += 1

                # 避免请求过快
                time.sleep(1.0)

            except Exception as e:
                print(f"获取第{page}页失败: {e}")
                break

        return all_stocks

    def scan_market(self,
                   screen_func: Callable[[Dict], bool],
                   limit: Optional[int] = None,
                   max_workers: int = 10) -> List[Dict]:
        """
        全市场扫描

        参数:
            screen_func: 筛选函数，接收股票数据，返回True/False
            limit: 限制扫描数量，None表示全部
            max_workers: 并发线程数

        返回:
            符合条件的股票列表
        """
        # 1. 获取股票列表
        print(f"正在获取A股列表...")
        stocks = self.get_all_stocks(limit=limit)
        print(f"获取到 {len(stocks)} 只股票")

        if not stocks:
            return []

        # 2. 批量扫描
        print(f"开始扫描（并发数: {max_workers}）...")
        qualified = []
        total = len(stocks)

        for i, stock in enumerate(stocks, 1):
            try:
                # 执行筛选
                if screen_func(stock):
                    qualified.append(stock)
                    print(f"  [{i}/{total}] ✓ {stock['name']} ({stock['code']})")

                if i % 100 == 0:
                    print(f"  进度: {i}/{total} ({i/total*100:.1f}%)")
            except Exception as e:
                print(f"  [{i}/{total}] ✗ {stock.get('code', 'Unknown')}: {e}")

        return qualified

    def scan_market_with_details(self,
                                 screen_func: Callable[[Dict], bool],
                                 limit: Optional[int] = None) -> List[Dict]:
        """
        全市场扫描（获取详细信息后筛选）

        注意：速度较慢，因为需要获取每只股票的详细信息

        参数:
            screen_func: 筛选函数，接收详细股票数据，返回True/False
            limit: 限制扫描数量

        返回:
            符合条件的股票详细列表
        """
        from stock_api_enhanced import EnhancedStockAPI

        # 1. 获取股票列表
        print(f"正在获取A股列表...")
        stocks = self.get_all_stocks(limit=limit)
        print(f"获取到 {len(stocks)} 只股票")

        if not stocks:
            return []

        # 2. 逐个获取详细信息并筛选
        print(f"开始扫描（获取详细信息）...")
        qualified = []
        api = EnhancedStockAPI()

        for i, stock in enumerate(stocks, 1):
            try:
                # 获取详细信息
                detail = api.get_stock_detail_em(stock['code'])

                # 执行筛选
                if screen_func(detail):
                    qualified.append(detail)
                    print(f"  [{i}/{len(stocks)}] ✓ {detail['stock_name']} ({detail['stock_code']}) - "
                          f"¥{detail['current_price']:.2f} ({detail['change_percent']:+.2f}%)")

                if i % 50 == 0:
                    print(f"  进度: {i}/{len(stocks)}")
                    time.sleep(1.0)  # 避免请求过快

            except Exception as e:
                print(f"  [{i}/{len(stocks)}] ✗ {stock['code']}: {e}")

        return qualified

    def get_hot_stocks(self, top_n: int = 100) -> List[Dict]:
        """
        获取热门股票（按成交额排序）

        参数:
            top_n: 返回前N只

        返回:
            热门股票列表
        """
        params = {
            'pn': '1',
            'pz': str(top_n),
            'po': '1',
            'np': '1',
            'fltt': '2',
            'invt': '2',
            'fid': 'f6',  # 按成交额排序
            'fs': 'm:0+t:6,m:0+t:80,m:0+t:81,m:1+t:2,m:1+t:23',
            'fields': 'f12,f13,f14,f2,f3,f4,f5,f6',
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b'
        }

        url = 'http://80.push2.eastmoney.com/api/qt/clist/get'

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            data = response.json()

            if not data.get('data'):
                return []

            stocks = []
            for item in data['data']['diff']:
                stocks.append({
                    'code': item.get('f12', ''),
                    'name': item.get('f14', ''),
                    'current': item.get('f2', 0) / 100,
                    'change_percent': item.get('f3', 0) / 100,
                    'turnover': item.get('f6', 0),  # 成交额
                })

            return stocks

        except Exception as e:
            print(f"获取热门股票失败: {e}")
            return []

    def format_scan_result(self, stocks: List[Dict]) -> str:
        """格式化扫描结果"""
        if not stocks:
            return "未找到符合条件的股票"

        output = f"\n找到 {len(stocks)} 只符合条件的股票:\n"
        output += "-" * 80 + "\n"

        for stock in stocks[:20]:  # 最多显示20只
            name = stock.get('stock_name', stock.get('name', ''))
            code = stock.get('stock_code', stock.get('code', ''))
            price = stock.get('current_price', stock.get('current', 0))
            change = stock.get('change_percent', 0)
            turnover = stock.get('turnover_rate', 0)

            output += f"{name} ({code}) - ¥{price:.2f} ({change:+.2f}%) 换手率:{turnover:.2f}%\n"

        if len(stocks) > 20:
            output += f"\n... 还有 {len(stocks) - 20} 只股票\n"

        return output


# 便捷函数
def get_all_stocks(limit: Optional[int] = None, use_pagination: bool = True) -> List[Dict]:
    """获取所有A股列表"""
    scanner = StockScanner()
    return scanner.get_all_stocks(limit=limit, use_pagination=use_pagination)


def scan_market(screen_func: Callable[[Dict], bool],
                limit: Optional[int] = None) -> List[Dict]:
    """扫描全市场"""
    scanner = StockScanner()
    return scanner.scan_market(screen_func, limit=limit)


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    scanner = StockScanner()

    # 测试1: 获取所有股票
    print("=== 测试1: 获取A股列表 ===")
    stocks = scanner.get_all_stocks(limit=10)
    print(f"获取到 {len(stocks)} 只股票（测试模式，仅10只）")
    for s in stocks[:5]:
        print(f"  {s['name']} ({s['code']})")
    print()

    # 测试2: 获取热门股票
    print("=== 测试2: 获取热门股票 ===")
    hot = scanner.get_hot_stocks(20)
    print(f"前 {len(hot)} 只热门股票（按成交额）:")
    for s in hot[:10]:
        print(f"  {s['name']}: ¥{s['turnover']/100000000:.2f} 亿")
    print()

    # 测试3: 简单筛选
    print("=== 测试3: 简单筛选 ===")
    def my_screen(stock):
        # 涨幅>3%的股票
        return stock.get('change_percent', 0) > 3

    result = scanner.scan_market(my_screen, limit=1000)
    print(f"\n涨幅>3%的股票: {len(result)} 只")
    for s in result[:10]:
        print(f"  {s['name']}: {s['change_percent']:.2f}%")
