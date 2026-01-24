# AI_Trade Skill 问题报告

**报告时间**: 2025-01-24
**测试任务**: 使用王子战法筛选5个股票
**测试环境**: Windows, Python 3.x

---

## 一、导入路径问题

### 问题描述
`demos/run_prince_strategy_real_ma.py` 脚本中的模块导入路径不正确，导致无法运行。

### 错误信息
```
ModuleNotFoundError: No module named 'scripts'
```

### 原始代码
```python
from scripts import StockScanner, EnhancedStockAPI
from scripts.stock_ma_data import MADataAPI
```

### 修复方案
需要添加父目录到sys.path：
```python
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from scripts.stock_scanner import StockScanner
from scripts.stock_api_enhanced import EnhancedStockAPI
from scripts.stock_ma_data import MADataAPI
```

### 建议
- 修复 `demos/` 目录下所有脚本的导入路径
- 或者提供一个统一的初始化脚本供demos使用

---

## 二、网络连接问题

### 问题描述
在获取股票历史数据时，大量股票出现连接中断错误。

### 错误信息
```
获取 600879 历史数据失败: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

### 影响范围
- 测试300只股票，约70%+的数据获取失败
- 导致筛选效率大幅降低

### 可能原因
1. AKShare API的并发限制
2. 网络请求频率过快被服务器拒绝
3. 请求超时设置过短

### 建议
- 增加重试机制（指数退避）
- 增加请求超时时间
- 添加并发控制（如使用Semaphore限制并发数）
- 考虑使用代理池或备用数据源
- 添加更详细的错误日志（记录哪些股票失败、失败原因）

---

## 三、战法逻辑Bug（严重）

### 问题描述
第5只股票（香农芯创 300475）不符合王子战法的MA5 > MA10条件，但仍被筛选出来。

### 数据分析
```
香农芯创 (300475)
MA5: 162.19
MA10: 166.50
MA趋势: 下降 (MA5-MA10: -4.31)  # MA5 < MA10，不符合条件！
```

### 根本原因
检查 `strategies/custom/王子战法.py` 发现：

1. **战法定义不一致**：
   - 文件描述：`MA5大于MA20` (第10行)
   - demo脚本注释：`MA5 > MA10` (第18行)
   - 实际代码：使用 `ma20` 参数，但传入的是 `ma10`

2. **参数传递错误** (`demos/run_prince_strategy_real_ma.py`):
```python
# 第50-51行：传入的是MA10
params = {
    'ma5': ma5,
    'ma10': ma10,  # 参数名是 ma10
    ...
}
```

但战法函数期望的是 `ma20`：
```python
# 王子战法.py 第68-69行
ma5 = params.get('ma5', 0)
ma20 = params.get('ma20', 0)  # 期望的是 ma20！
```

### 建议
- **立即修复**：统一战法定义，明确使用MA5 > MA10还是MA5 > MA20
- **添加参数验证**：在 `screen()` 函数开头检查必需参数是否存在
- **添加单元测试**：确保战法逻辑与描述一致
- **战法描述模板化**：使用配置文件定义战法，避免硬编码不一致

---

## 四、数据获取效率问题

### 问题描述
获取MA数据速度较慢，每只股票需要单独请求，且有延迟。

### 现状
```python
# MADataAPI 中有1秒延迟
time.sleep(1)  # 避免请求过快
```

### 性能影响
- 筛选300只股票理论上需要5分钟（300秒）
- 加上网络错误重试，实际耗时更长

### 建议
- 实现批量API调用（如果数据源支持）
- 使用缓存机制（Redis/本地文件）缓存历史数据
- 异步请求（asyncio/aiohttp）
- 分时段预加载热门股票数据

---

## 五、战法文件代码冗余

### 问题描述
`strategies/custom/王子战法.py` 存在冗余代码。

### 问题代码
```python
# 第82-85行
return all(conditions_met)

# 所有条件都满足
return True  # 这行永远不会执行！
```

### 建议
- 清理无用代码
- 添加代码质量检查工具（pylint/flake8）

---

## 六、错误处理不足

### 问题描述
网络错误被静默忽略，缺乏详细日志。

### 当前代码
```python
except Exception as e:
    continue  # 直接跳过，没有任何日志
```

### 建议
```python
except Exception as e:
    logger.warning(f"股票 {code} 筛选失败: {str(e)}")
    failed_stocks.append({'code': code, 'error': str(e)})
    continue
```

- 添加logging模块
- 记录失败股票列表
- 最终报告失败统计

---

## 七、参数不一致问题

### 问题描述
王子战法在不同地方的描述不一致：

| 位置 | 描述 |
|------|------|
| 战法文件 (第10行) | `MA5大于MA20` |
| Demo注释 (第18行) | `MA5 > MA10` |
| Demo注释 (第67行) | `MA5 > MA10` |

### 建议
- 统一战法描述来源（从战法文件读取）
- Demo中的注释动态生成，不硬编码

---

## 八、功能建议

### 8.1 进度显示优化
- 当前每30只显示一次进度，建议改为每10只
- 添加预计剩余时间

### 8.2 结果导出
- 支持导出为CSV/Excel
- 支持导出为JSON供后续分析

### 8.3 参数可配置
- 筛选数量、超时时间、重试次数等应可配置
- 支持命令行参数

### 8.4 数据验证
- 添加数据完整性检查（MA数据是否为None/0）
- 添加异常值检测

---

## 优先级建议

### P0（紧急修复）
1. **战法逻辑Bug** - 导致筛选结果错误
2. **导入路径问题** - 导致脚本无法运行

### P1（重要优化）
3. 网络连接稳定性 - 添加重试机制
4. 错误处理和日志 - 便于问题排查

### P2（性能优化）
5. 数据获取效率 - 批量请求/缓存
6. 参数不一致 - 统一战法定义

### P3（体验改进）
7. 进度显示优化
8. 结果导出功能
9. 代码清理

---

## 测试环境信息

```
Python: 3.x
OS: Windows
工作目录: C:\Users\admin\.claude\skills\ai_trade
数据源: AKShare (历史数据) + 东方财富 (实时数据)
```

---

## 总结

该Skill框架设计良好，功能完整，但存在以下关键问题需要修复：

1. **战法逻辑与实现不一致** - 最严重，影响筛选结果准确性
2. **导入路径问题** - 影响开箱即用体验
3. **网络稳定性** - 影响实际使用效果
4. **错误处理缺失** - 影响问题排查

建议优先修复P0和P1级别问题后再推广使用。

---

**报告人**: Claude (AI Assistant)
**联系方式**: 通过GitHub Issues反馈
