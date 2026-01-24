"""
MA均线数据获取模块
使用AKShare获取历史数据并计算MA
"""
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List


class MADataAPI:
    """MA均线数据API"""

    def __init__(self):
        self.akshare = None
        self._init_akshare()

    def _init_akshare(self):
        """初始化akshare"""
        try:
            import akshare as ak
            self.akshare = ak
            print("✓ AKShare 初始化成功")
        except ImportError:
            print("✗ AKShare 未安装，正在安装...")
            import subprocess
            subprocess.check_call(['pip', 'install', 'akshare'])
            import akshare as ak
            self.akshare = ak
            print("✓ AKShare 安装成功")

    def get_stock_history(self, symbol: str, days: int = 60) -> Optional[pd.DataFrame]:
        """
        获取股票历史数据

        参数:
            symbol: 股票代码（如 '601318' 或 '000001'）
            days: 获取最近多少天的数据

        返回:
            DataFrame with columns: 日期, 开盘, 收盘, 最高, 最低, 成交量, etc.
        """
        try:
            # 计算日期范围
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

            # 获取历史数据
            df = self.akshare.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust=""
            )

            if df is None or df.empty:
                return None

            # 重命名列（AKShare返回的是中文列名）
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '涨跌幅': 'change_percent',
                '涨跌额': 'change_amount',
                '换手率': 'turnover_rate'
            })

            # 计算MA均线
            df['MA5'] = df['close'].rolling(window=5).mean()
            df['MA10'] = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA30'] = df['close'].rolling(window=30).mean()

            return df

        except Exception as e:
            print(f"获取 {symbol} 历史数据失败: {e}")
            return None

    def get_current_ma(self, symbol: str) -> Optional[Dict]:
        """
        获取当前MA数据

        参数:
            symbol: 股票代码

        返回:
            {
                'MA5': value,
                'MA10': value,
                'MA20': value,
                'MA30': value,
                'current_price': value,
                'date': 'YYYY-MM-DD'
            }
        """
        df = self.get_stock_history(symbol, days=40)

        if df is None or df.empty:
            return None

        # 获取最新一行
        latest = df.iloc[-1]

        return {
            'MA5': round(latest['MA5'], 2) if pd.notna(latest['MA5']) else None,
            'MA10': round(latest['MA10'], 2) if pd.notna(latest['MA10']) else None,
            'MA20': round(latest['MA20'], 2) if pd.notna(latest['MA20']) else None,
            'MA30': round(latest['MA30'], 2) if pd.notna(latest['MA30']) else None,
            'current_price': round(latest['close'], 2),
            'date': latest['date'],
        }

    def batch_get_ma(self, symbols: List[str], delay: float = 1.0) -> Dict[str, Dict]:
        """
        批量获取MA数据

        参数:
            symbols: 股票代码列表
            delay: 请求延迟（秒）

        返回:
            {symbol: ma_data}
        """
        results = {}

        for i, symbol in enumerate(symbols, 1):
            print(f"  [{i}/{len(symbols)}] 获取 {symbol} MA数据...")
            ma_data = self.get_current_ma(symbol)

            if ma_data:
                results[symbol] = ma_data
                print(f"    ✓ MA5={ma_data['MA5']}, MA10={ma_data['MA10']}, "
                      f"MA20={ma_data['MA20']}, MA30={ma_data['MA30']}")
            else:
                print(f"    ✗ 获取失败")

            # 避免请求过快
            time.sleep(delay)

        return results

    def get_stock_with_ma_enhanced(self, symbol: str) -> Optional[Dict]:
        """
        获取股票详细信息（含MA数据）

        结合实时行情API和历史数据API

        返回:
            完整的股票数据字典（包含MA）
        """
        from stock_api_enhanced import EnhancedStockAPI

        # 获取实时数据
        realtime_api = EnhancedStockAPI()
        realtime_data = realtime_api.get_stock_detail_em(symbol)

        if not realtime_data:
            return None

        # 获取MA数据
        ma_data = self.get_current_ma(symbol)

        if ma_data:
            # 合并数据
            realtime_data.update({
                'MA5': ma_data['MA5'],
                'MA10': ma_data['MA10'],
                'MA20': ma_data['MA20'],
                'MA30': ma_data['MA30'],
                'ma_date': ma_data['date']
            })
        else:
            realtime_data.update({
                'MA5': None,
                'MA10': None,
                'MA20': None,
                'MA30': None,
                'ma_date': None
            })

        return realtime_data


# 便捷函数
def get_stock_ma(symbol: str) -> Optional[Dict]:
    """获取股票MA数据"""
    api = MADataAPI()
    return api.get_current_ma(symbol)


def batch_get_stock_ma(symbols: List[str]) -> Dict[str, Dict]:
    """批量获取股票MA数据"""
    api = MADataAPI()
    return api.batch_get_ma(symbols)


if __name__ == '__main__':
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("测试MA数据获取")
    print("=" * 70)

    # 测试1: 获取单只股票MA
    print("\n【测试1】获取中国平安(601318) MA数据")
    api = MADataAPI()
    ma_data = api.get_current_ma('601318')

    if ma_data:
        print(f"日期: {ma_data['date']}")
        print(f"当前价: ¥{ma_data['current_price']}")
        print(f"MA5: ¥{ma_data['MA5']}")
        print(f"MA10: ¥{ma_data['MA10']}")
        print(f"MA20: ¥{ma_data['MA20']}")
        print(f"MA30: ¥{ma_data['MA30']}")

    # 测试2: 获取含MA的完整数据
    print("\n【测试2】获取含MA的完整数据")
    full_data = api.get_stock_with_ma_enhanced('601318')

    if full_data:
        print(f"股票: {full_data['stock_name']} ({full_data['stock_code']})")
        print(f"价格: ¥{full_data['current_price']}")
        print(f"涨跌幅: {full_data['change_percent']:+.2f}%")
        print(f"换手率: {full_data['turnover_rate']:.2f}%")
        print(f"MA5: ¥{full_data['MA5']}")
        print(f"MA10: ¥{full_data['MA10']}")
        print(f"MA20: ¥{full_data['MA20']}")
        print(f"MA30: ¥{full_data['MA30']}")

    # 测试3: 批量获取
    print("\n【测试3】批量获取MA数据")
    symbols = ['601318', '600519', '000001', '002594']
    results = api.batch_get_ma(symbols, delay=1.0)

    print(f"\n成功获取 {len(results)} 只股票的MA数据")
    for symbol, data in results.items():
        print(f"  {symbol}: MA5={data['MA5']}, MA10={data['MA10']}, "
              f"MA20={data['MA20']}, MA30={data['MA30']}")

    print("\n" + "=" * 70)
