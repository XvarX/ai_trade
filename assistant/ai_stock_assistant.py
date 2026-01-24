"""
AI股票助手主程序
用于让AI调用查询A股信息
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.stock_api import StockAPIClient, StockAPIError
from scripts.technical_indicators import TechnicalIndicators, StockScreener
import json
from typing import Dict, List


class AIStockAssistant:
    """AI股票助手 - 提供给AI调用的接口"""

    def __init__(self, api_source: str = 'tencent'):
        """
        初始化
        api_source: API数据源 ('tencent' 或 'sina')
        """
        self.api_client = StockAPIClient()
        self.api_source = api_source
        self.screener = StockScreener()
        self.indicators = TechnicalIndicators()

    def query_stock(self, stock_code: str) -> Dict:
        """
        查询单个股票信息
        stock_code: 股票代码，如 '601318' (中国平安)
        返回股票信息字典
        """
        try:
            stock_data = self.api_client.get_stock_price(stock_code, self.api_source)
            return {
                'success': True,
                'data': stock_data,
                'formatted': self.api_client.format_stock_info(stock_data)
            }
        except StockAPIError as e:
            return {
                'success': False,
                'error': str(e),
                'stock_code': stock_code
            }

    def query_multiple_stocks(self, stock_codes: List[str]) -> List[Dict]:
        """
        批量查询股票信息
        stock_codes: 股票代码列表
        返回股票信息列表
        """
        results = []
        for code in stock_codes:
            result = self.query_stock(code)
            results.append(result)
        return results

    def get_stock_price_simple(self, stock_code: str) -> str:
        """
        快速获取股票价格（简化接口）
        返回易于理解的字符串
        """
        result = self.query_stock(stock_code)
        if result['success']:
            data = result['data']
            name = data['stock_name']
            price = data['current_price']
            change = data['change_percent']
            return f"{name}({stock_code}) 当前价格: ¥{price:.2f}, 涨跌幅: {change:+.2f}%"
        else:
            return f"查询失败: {result['error']}"

    def screen_stocks_bearish_high_turnover(
        self,
        stock_codes: List[str] = None,
        min_turnover: float = 5.0
    ) -> List[Dict]:
        """
        筛选阴线+高换手+上升趋势的股票
        stock_codes: 要筛选的股票代码列表，None则使用默认列表
        min_turnover: 最低换手率（默认5%）

        注意：由于实时API不提供历史数据，此方法需要配合历史数据使用
        这里仅展示框架逻辑
        """
        if stock_codes is None:
            stock_codes = self.api_client.get_stock_list()

        qualified_stocks = []

        # 注意：实际应用中需要获取历史数据计算MA值
        # 这里仅展示筛选逻辑框架
        for code in stock_codes:
            try:
                stock_data = self.api_client.get_stock_price(code, self.api_source)

                # 假设已经有了MA数据（实际需要从历史数据计算）
                # 这里使用模拟数据展示筛选逻辑
                ma5 = stock_data['current_price'] * 1.01  # 模拟数据
                ma10 = stock_data['current_price'] * 1.005
                ma20 = stock_data['current_price'] * 0.995
                ma30 = stock_data['current_price'] * 0.99

                # 模拟换手率（实际需要流通股本数据）
                turnover_rate = 3.0  # 模拟数据

                # 执行筛选
                is_qualified = self.screener.screen_bearish_high_turnover_uptrend(
                    stock_data,
                    ma5=ma5,
                    ma10=ma10,
                    ma20=ma20,
                    ma30=ma30,
                    turnover_rate=turnover_rate,
                    min_turnover=min_turnover
                )

                if is_qualified:
                    qualified_stocks.append({
                        'stock_code': code,
                        'stock_name': stock_data['stock_name'],
                        'current_price': stock_data['current_price'],
                        'change_percent': stock_data['change_percent'],
                        'turnover_rate': turnover_rate,
                        'ma5': ma5,
                        'ma10': ma10,
                        'ma20': ma20,
                        'ma30': ma30
                    })

            except StockAPIError as e:
                print(f"获取 {code} 数据失败: {e}")
                continue

        return qualified_stocks

    def analyze_stock(self, stock_code: str) -> Dict:
        """
        分析股票基本信息
        返回包含价格、涨跌、基本信息等的分析报告
        """
        result = self.query_stock(stock_code)
        if not result['success']:
            return result

        data = result['data']

        analysis = {
            'stock_code': stock_code,
            'stock_name': data['stock_name'],
            'price_info': {
                'current': data['current_price'],
                'yesterday_close': data['yesterday_close'],
                'open': data['open_price'],
                'high': data['high_price'],
                'low': data['low_price']
            },
            'change_info': {
                'change_amount': data['current_price'] - data['yesterday_close'],
                'change_percent': data['change_percent']
            },
            'volume_info': {
                'volume': data['volume'],
                'turnover': data['turnover']
            },
            'candle_type': self._determine_candle_type(data),
            'time': f"{data.get('date', '')} {data.get('time', '')}"
        }

        return {
            'success': True,
            'data': analysis,
            'formatted_summary': self._format_analysis(analysis)
        }

    def _determine_candle_type(self, stock_data: Dict) -> str:
        """判断K线类型"""
        open_price = stock_data['open_price']
        close = stock_data['current_price']
        high = stock_data['high_price']
        low = stock_data['low_price']

        if self.indicators.is_bearish_candle(open_price, close, high, low):
            return '阴线'
        elif self.indicators.is_bullish_candle(open_price, close, high, low):
            return '阳线'
        else:
            return '平盘'

    def _format_analysis(self, analysis: Dict) -> str:
        """格式化分析报告"""
        name = analysis['stock_name']
        code = analysis['stock_code']
        price = analysis['price_info']['current']
        change = analysis['change_info']['change_percent']
        candle = analysis['candle_type']
        volume = analysis['volume_info']['volume']

        trend = "📈 上涨" if change > 0 else "📉 下跌" if change < 0 else "➡️ 平盘"

        return f"""
📊 {name} ({code})
━━━━━━━━━━━━━━━━━━━━━
💰 价格: ¥{price:.2f}
📊 {trend} {change:+.2f}%
🕯️ K线: {candle}
📦 成交量: {volume:,} 手
━━━━━━━━━━━━━━━━━━━━━
        """.strip()

    def get_market_summary(self, stock_codes: List[str] = None) -> Dict:
        """
        获取市场概览
        stock_codes: 要统计的股票列表
        """
        if stock_codes is None:
            stock_codes = self.api_client.get_stock_list()[:20]  # 取前20只

        results = self.query_multiple_stocks(stock_codes)

        rising_count = sum(1 for r in results if r['success'] and r['data']['change_percent'] > 0)
        falling_count = sum(1 for r in results if r['success'] and r['data']['change_percent'] < 0)
        flat_count = sum(1 for r in results if r['success'] and r['data']['change_percent'] == 0)

        return {
            'total': len(results),
            'rising': rising_count,
            'falling': falling_count,
            'flat': flat_count,
            'summary': f"统计 {len(results)} 只股票: 上涨 {rising_count}, 下跌 {falling_count}, 平盘 {flat_count}"
        }


# 便捷函数，供AI快速调用
def get_stock_info(stock_code: str) -> str:
    """
    快速查询股票信息
    用法: get_stock_info('601318')
    """
    assistant = AIStockAssistant()
    return assistant.get_stock_price_simple(stock_code)


def analyze_stock(stock_code: str) -> str:
    """
    分析股票
    用法: analyze_stock('601318')
    """
    assistant = AIStockAssistant()
    result = assistant.analyze_stock(stock_code)
    if result['success']:
        return result['formatted_summary']
    else:
        return f"分析失败: {result['error']}"


if __name__ == '__main__':
    # 测试代码
    print("=" * 50)
    print("测试AI股票助手")
    print("=" * 50)

    # 测试1: 查询中国平安
    print("\n【测试1】查询中国平安价格")
    print(get_stock_info('601318'))

    # 测试2: 分析股票
    print("\n【测试2】分析中国平安")
    print(analyze_stock('601318'))

    # 测试3: 批量查询
    print("\n【测试3】批量查询")
    assistant = AIStockAssistant()
    results = assistant.query_multiple_stocks(['601318', '000001', '600519'])
    for result in results:
        if result['success']:
            print(f"✓ {result['data']['stock_name']}: ¥{result['data']['current_price']:.2f}")
        else:
            print(f"✗ {result['stock_code']}: 查询失败")

    # 测试4: 市场概览
    print("\n【测试4】市场概览")
    summary = assistant.get_market_summary(['601318', '000001', '600519', '000858'])
    print(summary['summary'])
