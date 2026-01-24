"""
增强版股票API客户端 - 支持换手率等更多数据
"""
import requests
from typing import Dict, Optional


class EnhancedStockAPI:
    """增强版API - 支持换手率、市值等更多字段"""

    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_stock_detail_em(self, stock_code: str) -> Dict:
        """
        使用东方财富API获取详细数据（包含换手率）

        参数:
            stock_code: 股票代码，如 '000001' 或 '601318'

        返回:
            包含换手率等详细数据的字典
        """
        # 确定市场前缀
        if stock_code.startswith('6'):
            secid = f'1.{stock_code}'  # 1. 表示沪市
        else:
            secid = f'0.{stock_code}'  # 0. 表示深市

        url = 'http://push2.eastmoney.com/api/qt/stock/get'
        params = {
            'secid': secid,
            'fields': 'f43,f44,f45,f46,f47,f48,f49,f50,f57,f58,f60,f107,f116,f117,f127,f168',
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b'
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)

            if response.status_code != 200:
                raise Exception(f"HTTP错误: {response.status_code}")

            data = response.json()

            if not data.get('data'):
                raise Exception("未获取到数据")

            d = data['data']

            # 解析字段（东方财富字段说明）
            current = d.get('f43', 0) / 100  # 最新价（分转元）
            yesterday = d.get('f60', 0) / 100 if d.get('f60') else 0  # f60是昨收价（分转元）

            # 如果f60没有，尝试用f49
            if yesterday == 0:
                yesterday = d.get('f49', 0) / 100

            result = {
                'stock_code': stock_code,
                'stock_name': d.get('f58', ''),
                'current_price': current,
                'open_price': d.get('f46', 0) / 100,    # 开盘价（分转元）
                'yesterday_close': yesterday,         # 昨收（分转元）
                'high_price': d.get('f44', 0) / 100,     # 最高价（分转元）
                'low_price': d.get('f45', 0) / 100,      # 最低价（分转元）
                'volume': d.get('f47', 0),                # 成交量（手）
                'turnover_amount': d.get('f48', 0),       # 成交额（元）
                'change_percent': ((current - yesterday) / yesterday * 100) if yesterday > 0 else 0,
                'total_market_cap': d.get('f116', 0),    # 总市值（元）
                'circulating_market_cap': d.get('f117', 0),  # 流通市值（元）
                'turnover_rate': d.get('f168', 0) / 100,  # 换手率（需要除以100）
                'industry': d.get('f127', ''),            # 行业
                'timestamp': d.get('f107', 0),            # 时间戳
            }

            # 计算涨跌额
            result['change_amount'] = current - yesterday

            return result

        except Exception as e:
            raise Exception(f"获取股票详情失败: {str(e)}")

    def format_enhanced_info(self, stock_data: Dict) -> str:
        """格式化增强版股票信息"""
        if not stock_data:
            return "无数据"

        name = stock_data.get('stock_name', '未知')
        code = stock_data.get('stock_code', '')
        current = stock_data.get('current_price', 0)
        change = stock_data.get('change_percent', 0)
        high = stock_data.get('high_price', 0)
        low = stock_data.get('low_price', 0)
        open_price = stock_data.get('open_price', 0)
        volume = stock_data.get('volume', 0)
        turnover_rate = stock_data.get('turnover_rate', 0)
        market_cap = stock_data.get('total_market_cap', 0)

        # 涨跌标记
        mark = "📈" if change > 0 else "📉" if change < 0 else "➡️"

        return f"""
📊 {name} ({code})
{mark} 当前价格: ¥{current:.2f}
📊 涨跌幅: {change:+.2f}% (¥{stock_data.get('change_amount', 0):+.2f})
🔼 最高: ¥{high:.2f}
🔽 最低: ¥{low:.2f}
📍 开盘: ¥{open_price:.2f}
📦 成交量: {volume:,} 手
🔄 换手率: {turnover_rate:.2f}%
💰 总市值: ¥{market_cap/100000000:.2f} 亿
        """.strip()


# 测试代码
if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    api = EnhancedStockAPI()

    print("测试东方财富增强API\n")
    print("=" * 60)

    test_stocks = ['601318', '000001', '002594']

    for code in test_stocks:
        try:
            data = api.get_stock_detail_em(code)
            print(api.format_enhanced_info(data))
            print()
        except Exception as e:
            print(f"错误: {e}")
            print()
