"""
测试脚本 - 验证框架功能
"""
import sys
import io

# 设置UTF-8编码输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 导入路径
sys.path.insert(0, '..')


def test_dependencies():
    """测试依赖是否安装"""
    print("测试依赖...")
    try:
        import requests
        import pandas
        import numpy
        print("[OK] 基础依赖已安装")
        return True
    except ImportError as e:
        print(f"[FAIL] 缺少依赖: {e}")
        print("请运行: pip install requests pandas numpy")
        return False


def test_stock_api():
    """测试股票API"""
    print("\n测试股票API...")
    from scripts.stock_api import StockAPIClient, StockAPIError

    client = StockAPIClient()

    # 测试腾讯API
    try:
        data = client.get_stock_price_tencent('601318')
        print(f"[OK] 腾讯API: {data['stock_name']} - ¥{data['current_price']:.2f}")
    except StockAPIError as e:
        print(f"[FAIL] 腾讯API: {e}")

    # 测试新浪API
    try:
        data = client.get_stock_price_sina('000001')
        print(f"[OK] 新浪API: {data['stock_name']} - ¥{data['current_price']:.2f}")
    except StockAPIError as e:
        print(f"[FAIL] 新浪API: {e}")


def test_enhanced_api():
    """测试增强API（换手率）"""
    print("\n测试增强API...")
    from scripts.stock_api_enhanced import EnhancedStockAPI

    api = EnhancedStockAPI()
    try:
        data = api.get_stock_detail_em('601318')
        print(f"[OK] 东方财富API: {data['stock_name']} - 换手率{data['turnover_rate']:.2f}%")
    except Exception as e:
        print(f"[FAIL] 东方财富API: {e}")


def test_technical_indicators():
    """测试技术指标"""
    print("\n测试技术指标...")
    from scripts.technical_indicators import TechnicalIndicators

    indicators = TechnicalIndicators()

    # 测试MA计算
    prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    ma5 = indicators.calculate_ma(prices, 5)
    if ma5[-1] == 17.0:
        print("[OK] MA计算正确")
    else:
        print(f"[FAIL] MA计算错误: {ma5[-1]}")

    # 测试K线判断
    if indicators.is_bearish_candle(10, 9, 10.5, 8.5):
        print("[OK] 阴线判断正确")
    else:
        print("[FAIL] 阴线判断错误")

    if indicators.is_bullish_candle(10, 11, 11.5, 9.5):
        print("[OK] 阳线判断正确")
    else:
        print("[FAIL] 阳线判断错误")

    # 测试趋势判断
    if indicators.is_bullish_trend(12, 11, 10, 9):
        print("[OK] 多头排列判断正确")
    else:
        print("[FAIL] 多头排列判断错误")


def test_screener():
    """测试筛选器"""
    print("\n测试筛选器...")
    from scripts.technical_indicators import StockScreener

    screener = StockScreener()

    stock = {
        'open_price': 50,
        'current_price': 49,
        'high_price': 51,
        'low_price': 48
    }

    # 测试阴线+高换手+上升趋势筛选
    result = screener.screen_bearish_high_turnover_uptrend(
        stock,
        ma5=49.5,
        ma10=49,
        ma20=48.5,
        ma30=48,
        turnover_rate=6,
        min_turnover=5
    )

    if result:
        print("[OK] 筛选器逻辑正确")
    else:
        print("[FAIL] 筛选器逻辑错误")


def test_ai_assistant():
    """测试AI助手"""
    print("\n测试AI助手...")
    from assistant import AIStockAssistant

    assistant = AIStockAssistant()

    # 测试查询
    result = assistant.query_stock('601318')
    if result['success']:
        print(f"[OK] 查询功能: {result['data']['stock_name']}")
    else:
        print(f"[FAIL] 查询失败: {result.get('error')}")

    # 测试快捷函数
    from assistant import get_stock_info
    info = get_stock_info('601318')
    if '当前价格' in info:
        print("[OK] 快捷函数正常")
    else:
        print("[FAIL] 快捷函数异常")


def test_market_scanner():
    """测试市场扫描器"""
    print("\n测试市场扫描器...")
    from scripts import StockScanner

    scanner = StockScanner()
    stocks = scanner.get_all_stocks(limit=5)

    if len(stocks) > 0:
        print(f"[OK] 市场扫描: 获取了 {len(stocks)} 只股票")
        print(f"  示例: {stocks[0]['name']} ({stocks[0]['code']})")
    else:
        print("[FAIL] 市场扫描失败")


def test_strategy_system():
    """测试战法系统"""
    print("\n测试战法系统...")
    from strategies import get_strategy_api

    api = get_strategy_api()
    result = api.list_strategies()

    if result['total'] > 0:
        print(f"[OK] 战法系统: 共有 {result['total']} 个战法")
        print(f"  示例: {result['strategies'][0].get('name', 'Unknown')}")
    else:
        print("[FAIL] 战法系统失败")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("A股查询框架 - 功能测试")
    print("=" * 60)

    if not test_dependencies():
        print("\n请先安装依赖后再运行测试")
        sys.exit(1)

    try:
        test_stock_api()
        test_enhanced_api()
        test_technical_indicators()
        test_screener()
        test_ai_assistant()
        test_market_scanner()
        test_strategy_system()

        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
