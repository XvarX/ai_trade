# 战法系统使用指南

## 战法系统简介

战法系统允许你通过自然语言描述自动生成股票筛选策略，支持：
- ✅ 从描述自动生成战法代码
- ✅ 战法保存和加载
- ✅ 战法分享（导入/导出）
- ✅ 通过战法名称直接调用

## 快速开始

### 1. 创建战法

```python
from strategy_api import get_strategy_api

api = get_strategy_api()

# 方式1: 使用标准格式
result = api.create_strategy('新增战法-筛选:王子战法 阴线且MA5大于MA10且换手率大于5%')

# 方式2: 简化格式
result = api.create_strategy('新增战法 王子战法 阴线且MA5大于MA10且换手率大于5%')
```

### 2. 查看所有战法

```python
result = api.list_strategies()
print(result['summary'])  # 共 X 个战法

for s in result['strategies']:
    print(f"- [{s['category']}] {s['metadata']['name']}: {s['metadata']['description']}")
```

### 3. 执行战法

```python
from ai_stock_assistant import AIStockAssistant

assistant = AIStockAssistant()

# 获取股票数据
stock_data = assistant.query_stock('003007')['data']

# 准备参数
params = {
    'ma5': 44.0,
    'ma10': 43.5,
    'turnover_rate': 6.0
}

# 执行战法
result = api.execute_strategy('王子战法', stock_data, params)
print(result['message'])  # ✓ 通过 战法名 or ✗ 未通过 战法名
```

### 4. 导出/导入战法（分享）

```python
# 导出战法
api.export_strategy('王子战法', './my_strategy.py')

# 导入战法
api.import_strategy('./shared_strategy.py', '共享战法')
```

## 支持的描述语法

### 均线条件

- `MA5大于MA10` - MA5上穿MA10
- `MA5<MA20` - MA5下穿MA20
- `MA30大于MA60` - 长期均线条件

### K线形态

- `阴线` - 收盘价 < 开盘价
- `阳线` - 收盘价 > 开盘价
- `十字星` - 收盘价 ≈ 开盘价

### 换手率和成交量

- `换手率大于5%` - 换手率 >= 5%
- `换手率>10` - 换手率 >= 10%
- `成交量大于10000` - 成交量条件

### 组合条件

可以用"且"、"和"等连接词组合多个条件：

```
阴线且MA5大于MA10且换手率大于5%
阳线且成交量大于50000且价格高于MA20
```

## 战法文件格式

每个战法都是一个独立的Python文件：

```python
"""
战法名称: 我的战法
战法描述: 战法描述
作者: 作者名
版本: 1.0.0
"""

# 战法元数据
STRATEGY_NAME = "我的战法"
STRATEGY_DESCRIPTION = "战法描述"
STRATEGY_AUTHOR = "作者名"
STRATEGY_VERSION = "1.0.0"
STRATEGY_CATEGORY = "custom"
STRATEGY_TAGS = ["筛选", "自定义"]


def get_default_params():
    """获取默认参数"""
    return {
        'param1': value1,
        'param2': value2,
    }


def get_params_schema():
    """获取参数模式"""
    return {
        'param1': {'type': 'float', 'description': '参数1说明'},
        'param2': {'type': 'float', 'description': '参数2说明'},
    }


def screen(stock_data, **params):
    """
    战法筛选函数

    参数:
        stock_data: 股票数据字典
        **params: 战法参数

    返回:
        True: 符合战法条件
        False: 不符合
    """
    # 筛选逻辑
    return True
```

## 战法目录结构

```
strategies/
├── builtin/           # 内置战法（不可删除）
│   ├── bearish_uptrend.py    # 阴线高换手上升趋势
│   └── golden_cross.py       # 金叉战法
└── custom/            # 用户自定义战法
    └── 王子战法.py            # 你的战法
```

## 高级用法

### 批量筛选

```python
from strategy_api import get_strategy_api
from ai_stock_assistant import AIStockAssistant

api = get_strategy_api()
assistant = AIStockAssistant()

# 获取多只股票
stock_codes = ['601318', '000001', '600519', '000858']
stocks = assistant.query_multiple_stocks(stock_codes)

# 筛选符合条件的股票
qualified = []

for result in stocks:
    if result['success']:
        stock_data = result['data']

        # 准备参数（需要从历史数据计算）
        params = calculate_params(stock_data)

        # 执行战法
        screen_result = api.execute_strategy('王子战法', stock_data, params)

        if screen_result['passed']:
            qualified.append({
                'code': stock_data['stock_code'],
                'name': stock_data['stock_name'],
                'price': stock_data['current_price']
            })

print(f"找到 {len(qualified)} 只符合条件的股票")
```

### 修改战法参数

```python
# 获取战法信息
info = api.get_strategy_info('王子战法')

# 修改默认参数
params = info['info']['default_params'].copy()
params['min_turnover'] = 8.0  # 提高换手率要求到8%

# 使用新参数执行
result = api.execute_strategy('王子战法', stock_data, params)
```

## 内置战法

### 1. 阴线高换手上升趋势

**描述**: 今日收阴线但换手率较高，且均线呈多头排列

**条件**:
- 阴线（收盘价 < 开盘价）
- 换手率 >= 5%
- MA5 > MA10 > MA20 > MA30

**用法**:
```python
params = {
    'ma5': 44.0,
    'ma10': 43.5,
    'ma20': 43.0,
    'ma30': 42.5,
    'turnover_rate': 6.0,
    'min_turnover': 5.0
}
result = api.execute_strategy('阴线高换手上升趋势', stock_data, params)
```

### 2. 金叉战法

**描述**: MA5上穿MA10形成金叉，短期趋势转强

**条件**:
- MA5 > MA10
- 可选：检查是否刚发生金叉（需要前一日数据）

**用法**:
```python
params = {
    'ma5': 44.0,
    'ma10': 43.5,
    'prev_ma5': 43.0,  # 可选
    'prev_ma10': 43.8   # 可选
}
result = api.execute_strategy('金叉战法', stock_data, params)
```

## 注意事项

1. **参数提供**: MA值需要从历史数据计算，框架不提供历史数据获取
2. **战法名称**: 使用中文或英文，避免特殊字符
3. **覆盖保护**: 默认不允许覆盖同名战法，需要先删除
4. **分类**: builtin战法不可删除，custom战法可以自由管理

## 完整示例

```python
import sys
sys.stdout.reconfigure(encoding='utf-8')

from strategy_api import get_strategy_api
from ai_stock_assistant import AIStockAssistant

# 初始化
api = get_strategy_api()
assistant = AIStockAssistant()

# 1. 创建战法
print("创建战法...")
result = api.create_strategy('新增战法-筛选:我的战法 阳线且换手率大于3%')
if result['success']:
    print(f"✓ {result['message']}")

# 2. 列出所有战法
print("\n所有战法:")
result = api.list_strategies()
for s in result['strategies']:
    print(f"  - {s['metadata']['name']}")

# 3. 查询股票并筛选
print("\n筛选股票:")
stock_codes = ['601318', '600519', '000858']
results = assistant.query_multiple_stocks(stock_codes)

for r in results:
    if r['success']:
        data = r['data']
        params = {'turnover_rate': 5.0}  # 示例参数
        screen_result = api.execute_strategy('我的战法', data, params)
        if screen_result['passed']:
            print(f"  ✓ {data['stock_name']}: ¥{data['current_price']}")

# 4. 导出战法
print("\n导出战法...")
api.export_strategy('我的战法', './my_strategy.py')
print("✓ 战法已导出到 my_strategy.py")
```

## 常见问题

**Q: 如何查看战法的详细参数？**
```python
info = api.get_strategy_info('战法名称')
print(info['info']['default_params'])
print(info['info']['params_schema'])
```

**Q: 如何删除战法？**
```python
result = api.delete_strategy('战法名称')
```

**Q: 战法支持什么条件？**
- 均线关系（MA5 > MA10）
- K线形态（阴线、阳线、十字星）
- 换手率（换手率 > 5%）
- 成交量（成交量 > 10000）

**Q: 如何分享战法？**
1. 导出战法：`api.export_strategy('战法名', './file.py')`
2. 分享.py文件
3. 对方导入：`api.import_strategy('./file.py', '新战法名')`
