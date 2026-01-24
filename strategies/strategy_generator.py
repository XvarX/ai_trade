"""
战法生成器 - 从描述自动生成战法代码
"""
from typing import Dict, List
import re


class StrategyGenerator:
    """战法生成器 - 将描述转换为战法代码"""

    def __init__(self):
        self.templates = {
            'basic': self._get_basic_template(),
            'advanced': self._get_advanced_template(),
        }

    def generate_from_description(self, name: str, description: str, author: str = 'AI') -> str:
        """
        从描述生成战法代码

        参数:
            name: 战法名称
            description: 战法描述（自然语言）
            author: 作者

        返回:
            战法代码字符串
        """
        # 解析描述，提取参数
        parsed = self._parse_description(description)

        # 生成代码
        code = self._generate_code(name, description, author, parsed)

        return code

    def _parse_description(self, description: str) -> Dict:
        """
        解析战法描述

        提取:
        - 筛选条件
        - 参数
        - 逻辑
        """
        parsed = {
            'conditions': [],
            'params': {},
            'logic': []
        }

        # 方法1: 解析均线条件 - 使用更可靠的方法
        # 查找 "MA5大于MA10" 或 "MA5>MA10" 等模式
        ma_pattern = r'MA(\d+)([>＜<小于大于]+)MA(\d+)'
        for match in re.finditer(ma_pattern, description):
            ma1 = int(match.group(1))
            operator = match.group(2)
            ma2 = int(match.group(3))

            # 判断是大于还是小于
            if '>' in operator or '大于' in operator or '＞' in operator:
                parsed['conditions'].append({
                    'type': 'ma_above',
                    'ma1': ma1,
                    'ma2': ma2
                })
                parsed['params'][f'ma{ma1}'] = None
                parsed['params'][f'ma{ma2}'] = None
            elif '<' in operator or '小于' in operator or '＜' in operator:
                parsed['conditions'].append({
                    'type': 'ma_below',
                    'ma1': ma1,
                    'ma2': ma2
                })

        # 方法2: 备用解析 - 按关键词拆分
        if '大于' in description or '>' in description:
            parts = re.split(r'[大于>]', description)
            for i, part in enumerate(parts[:-1]):
                # 检查这个部分和下一部分
                current_mas = re.findall(r'MA?(\d+)', part)
                next_mas = re.findall(r'MA?(\d+)', parts[i + 1])

                if current_mas and next_mas:
                    ma1 = int(current_mas[-1])
                    ma2 = int(next_mas[0])

                    # 避免重复添加
                    existing = False
                    for c in parsed['conditions']:
                        if c.get('type') == 'ma_above' and c.get('ma1') == ma1 and c.get('ma2') == ma2:
                            existing = True
                            break

                    if not existing:
                        parsed['conditions'].append({
                            'type': 'ma_above',
                            'ma1': ma1,
                            'ma2': ma2
                        })
                        parsed['params'][f'ma{ma1}'] = None
                        parsed['params'][f'ma{ma2}'] = None

        # 解析K线形态
        if '阴线' in description:
            parsed['conditions'].append({'type': 'bearish'})
        if '阳线' in description:
            parsed['conditions'].append({'type': 'bullish'})
        if '十字星' in description or '星线' in description:
            parsed['conditions'].append({'type': 'doji'})

        # 解析换手率 - 使用字符串拆分方法
        if '换手率' in description:
            # 使用字符串拆分
            parts = description.split('换手率')
            for part in parts[1:]:  # 跳过第一个，因为那是换手率之前的内容
                # 在这部分中查找"大于"或">"
                if '大于' in part:
                    sub_part = part.split('大于')[1]
                    # 提取数字
                    num_match = re.search(r'(\d+\.?\d*)', sub_part)
                    if num_match:
                        value = float(num_match.group(1))
                        parsed['conditions'].append({
                            'type': 'turnover_above',
                            'value': value
                        })
                        parsed['params']['min_turnover'] = value
                        break
                elif '>' in part:
                    sub_part = part.split('>')[1]
                    num_match = re.search(r'(\d+\.?\d*)', sub_part)
                    if num_match:
                        value = float(num_match.group(1))
                        parsed['conditions'].append({
                            'type': 'turnover_above',
                            'value': value
                        })
                        parsed['params']['min_turnover'] = value
                        break

        # 解析成交量 - 使用同样的方法
        if '成交量' in description:
            parts = description.split('成交量')
            for part in parts[1:]:
                if '大于' in part:
                    sub_part = part.split('大于')[1]
                    num_match = re.search(r'(\d+)', sub_part)
                    if num_match:
                        value = int(num_match.group(1))
                        parsed['conditions'].append({
                            'type': 'volume_above',
                            'value': value
                        })
                        parsed['params']['min_volume'] = value
                        break
                elif '>' in part:
                    sub_part = part.split('>')[1]
                    num_match = re.search(r'(\d+)', sub_part)
                    if num_match:
                        value = int(num_match.group(1))
                        parsed['conditions'].append({
                            'type': 'volume_above',
                            'value': value
                        })
                        parsed['params']['min_volume'] = value
                        break

        return parsed

    def _generate_code(self, name: str, description: str, author: str, parsed: Dict) -> str:
        """生成战法代码"""

        # 生成参数
        params_code = self._generate_params(parsed['params'])
        schema_code = self._generate_params_schema(parsed['params'])

        # 生成筛选逻辑
        screen_code = self._generate_screen_logic(parsed)

        # 使用模板
        code = f'''"""
战法名称: {name}
战法描述: {description}
作者: {author}
版本: 1.0.0
"""

# 战法元数据
STRATEGY_NAME = "{name}"
STRATEGY_DESCRIPTION = "{description}"
STRATEGY_AUTHOR = "{author}"
STRATEGY_VERSION = "1.0.0"
STRATEGY_CATEGORY = "custom"
STRATEGY_TAGS = ["筛选", "自定义"]


def get_default_params():
    """获取默认参数"""
    return {{
{params_code}
    }}


def get_params_schema():
    """获取参数模式"""
    return {{
{schema_code}
    }}


def screen(stock_data, **params):
    """
    战法筛选函数

    参数:
        stock_data: 股票数据字典，包含:
            - current_price: 当前价格
            - open_price: 开盘价
            - close_price: 收盘价
            - high_price: 最高价
            - low_price: 最低价
            - volume: 成交量
            - turnover_rate: 换手率
            - ma5, ma10, ma20, ma30: 均线值（如果有）
        **params: 战法参数

    返回:
        True: 符合战法条件
        False: 不符合
    """
    # 提取常用字段
    current_price = stock_data.get('current_price', 0)
    open_price = stock_data.get('open_price', 0)
    close_price = stock_data.get('current_price', 0)  # 实时数据中current即close
    high_price = stock_data.get('high_price', 0)
    low_price = stock_data.get('low_price', 0)
    volume = stock_data.get('volume', 0)
    turnover_rate = params.get('turnover_rate', 0)

{screen_code}

    # 所有条件都满足
    return True
'''
        return code

    def _generate_params(self, params: Dict) -> str:
        """生成参数代码"""
        if not params:
            return "        # 无自定义参数"

        lines = []
        for key, value in params.items():
            if value is None:
                lines.append(f"        '{key}': None,  # 需要提供")
            else:
                lines.append(f"        '{key}': {value},")

        return '\n'.join(lines)

    def _generate_params_schema(self, params: Dict) -> str:
        """生成参数模式"""
        if not params:
            return "        # 无参数定义"

        lines = []
        for key, value in params.items():
            lines.append(f"        '{key}': {{'type': 'float', 'description': '{key}参数'}},")

        return '\n'.join(lines)

    def _generate_screen_logic(self, parsed: Dict) -> str:
        """生成筛选逻辑代码"""
        conditions = parsed.get('conditions', [])
        if not conditions:
            return "    # 未识别到筛选条件\n    pass"

        code_lines = ["    # 筛选条件检查", "    conditions_met = []"]

        for cond in conditions:
            cond_type = cond.get('type')

            if cond_type == 'ma_above':
                ma1 = cond['ma1']
                ma2 = cond['ma2']
                code_lines.append(f"""
    # 均线条件: MA{ma1} > MA{ma2}
    ma{ma1} = params.get('ma{ma1}', 0)
    ma{ma2} = params.get('ma{ma2}', 0)
    conditions_met.append(ma{ma1} > ma{ma2})
""")

            elif cond_type == 'ma_below':
                ma1 = cond['ma1']
                ma2 = cond['ma2']
                code_lines.append(f"""
    # 均线条件: MA{ma1} < MA{ma2}
    ma{ma1} = params.get('ma{ma1}', 0)
    ma{ma2} = params.get('ma{ma2}', 0)
    conditions_met.append(ma{ma1} < ma{ma2})
""")

            elif cond_type == 'bearish':
                code_lines.append("""
    # K线形态: 阴线
    conditions_met.append(close_price < open_price)
""")

            elif cond_type == 'bullish':
                code_lines.append("""
    # K线形态: 阳线
    conditions_met.append(close_price > open_price)
""")

            elif cond_type == 'turnover_above':
                value = cond['value']
                code_lines.append(f"""
    # 换手率条件: 换手率 >= {value}%
    conditions_met.append(turnover_rate >= {value})
""")

            elif cond_type == 'volume_above':
                value = cond['value']
                code_lines.append(f"""
    # 成交量条件: 成交量 >= {value}
    conditions_met.append(volume >= {value})
""")

        code_lines.append("\n    # 返回是否所有条件都满足")
        code_lines.append("    return all(conditions_met)")

        return '\n'.join(code_lines)

    def _get_basic_template(self) -> str:
        """基础战法模板"""
        return '''
def screen(stock_data, **params):
    """基础战法筛选"""
    return True
'''

    def _get_advanced_template(self) -> str:
        """高级战法模板"""
        return '''
def screen(stock_data, **params):
    """高级战法筛选"""
    return True
'''


def generate_strategy(name: str, description: str, author: str = 'AI') -> str:
    """
    便捷函数：从描述生成战法代码

    参数:
        name: 战法名称
        description: 战法描述
        author: 作者

    返回:
        战法代码
    """
    generator = StrategyGenerator()
    return generator.generate_from_description(name, description, author)
