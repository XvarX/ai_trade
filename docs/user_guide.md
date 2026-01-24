# A股市场信息查询框架

这是一个用于获取A股市场实时行情和技术分析的Python框架，专为AI调用设计。

## 功能特性

- ✅ 实时股票行情查询（腾讯API、新浪API）
- ✅ 技术指标计算（均线、K线形态、换手率等）
- ✅ 股票筛选器（阴线、高换手、趋势判断等）
- ✅ 批量查询和市场概览
- ✅ 简单易用的AI调用接口

## 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

## 快速开始

### 1. 基础用法 - 查询股票价格

```python
from ai_stock_assistant import get_stock_info, analyze_stock

# 快速查询股票价格
print(get_stock_info('601318'))  # 中国平安
# 输出: 中国平安(601318) 当前价格: ¥45.23, 涨跌幅: +2.35%

# 详细分析
print(analyze_stock('000001'))  # 平安银行
```

### 2. AI调用示例

当你问AI："现在中国平安什么价格？"

AI会自动转换成以下代码调用：

```python
from ai_stock_assistant import AIStockAssistant

assistant = AIStockAssistant()
result = assistant.query_stock('601318')

if result['success']:
    data = result['data']
    print(f"{data['stock_name']} 当前价格: ¥{data['current_price']:.2f}")
    print(f"涨跌幅: {data['change_percent']:+.2f}%")
```

### 3. 股票筛选示例

筛选阴线+高换手+上升趋势的股票：

```python
from ai_stock_assistant import AIStockAssistant

assistant = AIStockAssistant()

# 筛选条件：
# - 今日为阴线
# - 换手率 >= 5%
# - MA5 > MA10 > MA20 > MA30（上升趋势）
stocks = assistant.screen_stocks_bearish_high_turnover(
    stock_codes=['601318', '000001', '600519'],
    min_turnover=5.0
)

for stock in stocks:
    print(f"{stock['stock_name']}: ¥{stock['current_price']:.2f}")
```

## API文档

### AIStockAssistant类

#### `query_stock(stock_code: str) -> Dict`
查询单个股票信息

**参数：**
- `stock_code`: 股票代码，如 '601318'（中国平安）

**返回：**
```python
{
    'success': True,
    'data': {
        'stock_code': '601318',
        'stock_name': '中国平安',
        'current_price': 45.23,
        'yesterday_close': 44.20,
        'open_price': 44.50,
        'high_price': 45.50,
        'low_price': 44.30,
        'volume': 150000,  # 成交量（手）
        'turnover': 680000000.0,  # 成交额
        'change_percent': 2.35
    },
    'formatted': '...'  # 格式化的字符串
}
```

#### `analyze_stock(stock_code: str) -> Dict`
分析股票基本信息和技术指标

**返回包含：**
- 价格信息（当前、昨收、开盘、最高、最低）
- 涨跌信息（涨跌额、涨跌幅）
- K线类型（阴线/阳线/平盘）
- 成交量和成交额

#### `query_multiple_stocks(stock_codes: List[str]) -> List[Dict]`
批量查询股票

#### `screen_stocks_bearish_high_turnover(...) -> List[Dict]`
筛选阴线+高换手+上升趋势的股票

#### `get_market_summary(stock_codes: List[str]) -> Dict`
获取市场概览（上涨/下跌/平盘统计）

## 快捷函数

```python
from ai_stock_assistant import get_stock_info, analyze_stock

# 快速查询
get_stock_info('601318')  # 返回格式化字符串

# 快速分析
analyze_stock('601318')   # 返回分析报告
```

## 股票代码说明

- 上海证券交易所：6开头，如 `600000`（浦发银行）
- 深圳证券交易所：000/002/300开头，如 `000001`（平安银行）

## 筛选条件说明

### 阴线 + 高换手 + 上升趋势

**条件：**
1. **阴线**：收盘价 < 开盘价
2. **高换手**：换手率 >= 5%（可自定义）
3. **上升趋势**：MA5 > MA10 > MA20 > MA30

**含义：**
- 虽然今日下跌，但处于上升趋势中
- 换手率高说明交投活跃
- 可能是上升趋势中的回调机会

### 常见技术指标

| 指标 | 说明 | 计算方法 |
|------|------|----------|
| MA5 | 5日均线 | 最近5日收盘价平均值 |
| MA10 | 10日均线 | 最近10日收盘价平均值 |
| MA20 | 20日均线 | 最近20日收盘价平均值 |
| MA30 | 30日均线 | 最近30日收盘价平均值 |
| 换手率 | 交易活跃度 | 成交量 / 流通股本 × 100% |

## 数据源

框架支持多个数据源：
- **腾讯API**（默认）：`http://qt.gtimg.cn`
- **新浪API**：`http://hq.sinajs.cn`

切换数据源：
```python
assistant = AIStockAssistant(api_source='sina')
```

## 注意事项

1. **实时性**：数据来自公开API，可能有几十秒延迟
2. **历史数据**：当前版本主要提供实时行情，历史MA数据需要额外处理
3. **使用限制**：频繁查询可能被限制，建议合理控制请求频率
4. **股票代码**：不需要带交易所前缀，自动识别

## 测试

```bash
# 测试基础功能
python stock_api.py

# 测试技术指标
python technical_indicators.py

# 测试AI助手
python ai_stock_assistant.py
```

## 扩展开发

### 添加自定义筛选器

```python
from technical_indicators import StockScreener

screener = StockScreener()

# 自定义筛选条件
def my_custom_screen(stock_data, **kwargs):
    # 你的筛选逻辑
    return True  # 或 False

# 在主程序中调用
```

### 添加新的数据源

在 `stock_api.py` 中添加新方法：
```python
def get_stock_price_custom(self, stock_code: str) -> Dict:
    # 实现新的数据源
    pass
```

## 许可

MIT License

## 贡献

欢迎提交Issue和Pull Request！
