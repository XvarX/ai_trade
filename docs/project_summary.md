# A股查询框架 - 完整总结

## 项目概述

完整的A股市场信息查询和分析框架，包含：
- ✅ 实时股票行情查询（腾讯、新浪双API）
- ✅ 技术指标计算（均线、K线、换手率等）
- ✅ **战法系统** - 从自然语言自动生成筛选策略
- ✅ 战法分享和导入导出
- ✅ 完整的Python API和AI调用接口

## 战法系统 - 核心功能

### 1. 创建战法

从自然语言描述自动生成代码：

```python
from strategy_api import get_strategy_api

api = get_strategy_api()

# 输入格式
api.create_strategy('新增战法-筛选:王子战法 阴线且MA5大于MA10且换手率大于5%')

# 自动生成的代码包含：
# - 完整的战法元数据
# - 参数定义和模式
# - 筛选逻辑函数
```

### 2. 执行战法

```python
from ai_stock_assistant import AIStockAssistant

assistant = AIStockAssistant()
stock_data = assistant.query_stock('003007')['data']

# 准备参数（MA值需要从历史数据计算）
params = {
    'ma5': 44.0,
    'ma10': 43.5,
    'turnover_rate': 6.0
}

# 执行筛选
result = api.execute_strategy('王子战法', stock_data, params)
# 返回: {'passed': True/False, 'message': '✓ 通过 王子战法'}
```

### 3. 战法分享

**导出:**
```python
api.export_strategy('王子战法', './王子战法.py')
```

**导入:**
```python
api.import_strategy('./朋友分享的战法.py', '朋友战法')
```

文件可以直接复制分享，即插即用！

### 4. 支持的描述语法

| 类型 | 语法示例 | 说明 |
|------|----------|------|
| 均线 | `MA5大于MA10` | MA5 > MA10 |
| 均线 | `MA20<MA30` | MA20 < MA30 |
| K线 | `阴线` | 收盘价 < 开盘价 |
| K线 | `阳线` | 收盘价 > 开盘价 |
| 换手率 | `换手率大于5%` | 换手率 >= 5% |
| 成交量 | `成交量大于10000` | 成交量条件 |
| 组合 | `阴线且MA5大于MA10且换手率大于5%` | 所有条件同时满足 |

## 项目结构

```
ai_trade/
├── stock_api.py                  # API客户端（腾讯、新浪）
├── technical_indicators.py       # 技术指标计算
├── ai_stock_assistant.py         # AI调用主接口
├── strategy_api.py               # 战法API
├── strategies/                   # 战法系统
│   ├── __init__.py
│   ├── strategy_manager.py       # 战法管理器
│   ├── strategy_generator.py     # 战法生成器
│   ├── builtin/                  # 内置战法
│   │   ├── bearish_uptrend.py   # 阴线高换手上升趋势
│   │   └── golden_cross.py      # 金叉战法
│   └── custom/                   # 用户战法
│       └── 王子战法.py
├── examples.py                   # 8个使用示例
├── demo.py                       # 快速演示
├── STRATEGY_GUIDE.md            # 战法系统文档
└── README.md                     # 用户手册
```

## 使用示例

### 基础查询

```python
from ai_stock_assistant import get_stock_info

# 查询价格
print(get_stock_info('601318'))  # 中国平安
# 输出: 中国平安(601318) 当前价格: ¥63.90, 涨跌幅: -1.39%
```

### 战法创建和使用

```python
from strategy_api import get_strategy_api
from ai_stock_assistant import AIStockAssistant

api = get_strategy_api()
assistant = AIStockAssistant()

# 1. 创建战法
api.create_strategy('新增战法-筛选:我的战法 阳线且换手率大于3%')

# 2. 批量筛选
stocks = ['601318', '600519', '000858', '002594']
results = assistant.query_multiple_stocks(stocks)

qualified = []
for r in results:
    if r['success']:
        data = r['data']
        params = {'turnover_rate': 5.0}
        screen_result = api.execute_strategy('我的战法', data, params)
        if screen_result['passed']:
            qualified.append(data['stock_name'])

print(f"符合战法的股票: {', '.join(qualified)}")
```

## Skill打包

已打包成可分享的Skill文件：

**文件**: [a-stock-query-with-strategies.skill](d:/space/labspace/a-stock-query-with-strategies.skill) (31KB)

**包含内容**:
- 核心查询框架
- 完整战法系统
- 2个内置战法
- 完整文档和示例

**安装方法**:
1. 将 `.skill` 文件复制到 `~/.claude/skills/` 目录
2. AI会自动识别并调用

## 实测结果

**查询003007（直真科技）:**
- ✅ 实时价格: ¥45.40
- ✅ 涨跌幅: +4.27%
- ✅ K线类型: 阳线
- ✅ 成交量: 119,849手

**王子战法测试:**
- ✅ 成功创建
- ✅ 解析出3个条件（阴线、MA5>MA10、换手率>=5%）
- ✅ 正确执行筛选逻辑
- ✅ 成功导出可分享文件

## 技术亮点

1. **AI驱动的代码生成**: 从自然语言自动生成Python代码
2. **即插即用**: 战法文件可直接复制分享
3. **规范格式**: 统一的战法文件格式和元数据
4. **动态加载**: 运行时动态加载战法模块
5. **参数化**: 支持灵活的参数配置

## 下一步可扩展功能

1. **历史数据获取**: 集成历史K线数据API，自动计算MA值
2. **更多战法类型**: 支持MACD、KDJ、RSI等技术指标
3. **回测系统**: 测试战法历史表现
4. **战法市场**: 战法分享和交易平台
5. **预警系统**: 价格突破、战法触发提醒

## 依赖

```
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
```

## 文档

- [README.md](README.md) - 完整使用手册
- [STRATEGY_GUIDE.md](STRATEGY_GUIDE.md) - 战法系统详细指南
- [examples.py](examples.py) - 8个实用示例
- [demo.py](demo.py) - 快速演示

---

**作者**: AI
**版本**: 1.0.0
**日期**: 2026-01-24
