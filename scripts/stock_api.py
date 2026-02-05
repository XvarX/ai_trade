"""
A股行情API客户端
支持腾讯、新浪等多个数据源
"""
import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import time


class StockAPIError(Exception):
    """股票API异常"""
    pass


class StockAPIClient:
    """A股行情API客户端"""

    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_stock_price_tencent(self, stock_code: str) -> Dict:
        """
        使用腾讯API获取股票实时行情
        stock_code: 股票代码，如 '000001' (平安银行), '601318' (中国平安)
        返回格式化的股票信息字典
        """
        # 腾讯API格式：sh600000 或 sz000001
        if stock_code.startswith('6'):
            market = 'sh'
        else:
            market = 'sz'

        url = f"http://qt.gtimg.cn/q={market}{stock_code}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.encoding = 'gbk'

            # 腾讯返回格式: v_sh600000="1~平安银行~..."
            content = response.text
            if '~' not in content:
                raise StockAPIError(f"无法解析股票数据: {stock_code}")

            # 解析返回数据
            data_str = content.split('"')[1]
            fields = data_str.split('~')

            result = {
                'stock_code': stock_code,
                'stock_name': fields[1],
                'current_price': float(fields[3]) if fields[3] else 0,
                'yesterday_close': float(fields[4]) if fields[4] else 0,
                'open_price': float(fields[5]) if fields[5] else 0,
                'volume': int(float(fields[6])) if fields[6] else 0,  # 成交量（手）
                'turnover': float(fields[37]) if fields[37] else 0,   # 成交额
                'high_price': float(fields[33]) if fields[33] else 0,
                'low_price': float(fields[34]) if fields[34] else 0,
                'buy1_price': float(fields[9]) if fields[9] else 0,
                'sell1_price': float(fields[19]) if fields[19] else 0,
                'date': fields[30],
                'time': fields[31],
                'change_percent': ((float(fields[3]) - float(fields[4])) / float(fields[4]) * 100) if fields[3] and fields[4] else 0
            }

            return result

        except Exception as e:
            raise StockAPIError(f"获取股票行情失败: {str(e)}")

    def get_stock_price_sina(self, stock_code: str) -> Dict:
        """
        使用新浪API获取股票实时行情
        stock_code: 股票代码，如 'sh600000' 或 'sz000001'
        """
        # 新浪API格式：sh600000 或 sz000001
        if stock_code.startswith('6'):
            symbol = f'sh{stock_code}'
        else:
            symbol = f'sz{stock_code}'

        url = f"http://hq.sinajs.cn/list={symbol}"
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.encoding = 'gbk'

            content = response.text
            if '=' not in content:
                raise StockAPIError(f"无法解析股票数据: {stock_code}")

            # 解析返回数据
            data_str = content.split('"')[1]
            fields = data_str.split(',')

            result = {
                'stock_code': stock_code,
                'stock_name': fields[0],
                'open_price': float(fields[1]) if fields[1] else 0,
                'yesterday_close': float(fields[2]) if fields[2] else 0,
                'current_price': float(fields[3]) if fields[3] else 0,
                'high_price': float(fields[4]) if fields[4] else 0,
                'low_price': float(fields[5]) if fields[5] else 0,
                'buy1_price': float(fields[6]) if fields[6] else 0,
                'sell1_price': float(fields[7]) if fields[7] else 0,
                'volume': int(float(fields[8])) if fields[8] else 0,  # 成交量
                'turnover': float(fields[9]) if fields[9] else 0,      # 成交额
                'date': fields[30] if len(fields) > 30 else '',
                'time': fields[31] if len(fields) > 31 else '',
                'change_percent': ((float(fields[3]) - float(fields[2])) / float(fields[2]) * 100) if fields[3] and fields[2] else 0
            }

            return result

        except Exception as e:
            raise StockAPIError(f"获取股票行情失败: {str(e)}")

    def get_stock_price(self, stock_code: str, source: str = 'tencent') -> Dict:
        """
        获取股票实时行情（自动选择数据源）
        stock_code: 股票代码
        source: 数据源 'tencent' 或 'sina'
        """
        # 标准化股票代码
        stock_code = stock_code.replace('sh', '').replace('sz', '').replace('.', '')

        if source == 'tencent':
            return self.get_stock_price_tencent(stock_code)
        elif source == 'sina':
            return self.get_stock_price_sina(stock_code)
        else:
            raise StockAPIError(f"不支持的数据源: {source}")

    def format_stock_info(self, stock_data: Dict) -> str:
        """格式化股票信息为易读文本"""
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

        # 涨跌标记
        mark = "📈" if change > 0 else "📉" if change < 0 else "➡️"

        return f"""
📊 {name} ({code})
{mark} 当前价格: ¥{current:.2f}
📈 涨跌幅: {change:+.2f}%
🔼 今日最高: ¥{high:.2f}
🔽 今日最低: ¥{low:.2f}
📍 开盘价: ¥{open_price:.2f}
📊 成交量: {volume:,} 手
🕐 更新时间: {stock_data.get('date', '')} {stock_data.get('time', '')}
        """.strip()

    def get_stock_list(self) -> List[str]:
        """
        获取A股主要股票列表（简化版）
        实际应用中可以从文件或数据库读取完整列表
        这里返回一些常见股票代码用于演示
        """
        # 上证50部分成分股
        sh50 = [
            '600000',  # 浦发银行
            '600036',  # 招商银行
            '601318',  # 中国平安
            '601328',  # 交通银行
            '600519',  # 贵州茅台
            '600887',  # 伊利股份
            '601012',  # 隆基绿能
            '601888',  # 中国中免
            '600276',  # 恒瑞医药
            '601166',  # 兴业银行
        ]

        # 深圳成指部分成分股
        sz_components = [
            '000001',  # 平安银行
            '000002',  # 万科A
            '000858',  # 五粮液
            '002594',  # 比亚迪
            '300059',  # 东方财富
            '300750',  # 宁德时代
            '000333',  # 美的集团
            '002415',  # 海康威视
            '300015',  # 爱尔眼科
            '002304',  # 洋河股份
        ]

        return sh50 + sz_components


if __name__ == '__main__':
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    # 测试代码
    client = StockAPIClient()

    # 测试获取中国平安
    print("=== 测试获取中国平安 ===")
    try:
        data = client.get_stock_price('601318')
        print(client.format_stock_info(data))
    except StockAPIError as e:
        print(f"错误: {e}")

    print("\n=== 测试获取比亚迪 ===")
    try:
        data = client.get_stock_price('002594')
        print(client.format_stock_info(data))
    except StockAPIError as e:
        print(f"错误: {e}")
