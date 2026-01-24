"""
战法API - 提供给AI和用户调用的战法接口
"""
from typing import Dict, List
from strategies.strategy_manager import get_strategy_manager
from strategies.strategy_generator import generate_strategy


class StrategyAPI:
    """战法API"""

    def __init__(self):
        self.manager = get_strategy_manager()

    def create_strategy(self, input_text: str) -> Dict:
        """
        从输入创建战法

        支持的输入格式:
        - "新增战法-筛选:王子战法" + 描述
        - "新增战法 王子战法 " + 描述
        - "Create strategy PrinceStrategy " + description

        参数:
            input_text: 用户输入

        返回:
            {'success': True/False, 'message': str, 'strategy_file': str}
        """
        try:
            # 解析输入
            parsed = self._parse_input(input_text)
            if not parsed:
                return {
                    'success': False,
                    'error': '无法解析输入格式。请使用：新增战法-筛选:战法名称 描述内容'
                }

            name = parsed['name']
            description = parsed['description']
            author = parsed.get('author', 'AI')

            # 生成代码
            code = generate_strategy(name, description, author)

            # 保存战法
            file_path = self.manager.save_strategy(name, code, category='custom')

            return {
                'success': True,
                'message': f'战法 "{name}" 创建成功！',
                'strategy_name': name,
                'strategy_file': file_path,
                'code_preview': code[:500] + '...' if len(code) > 500 else code
            }

        except FileExistsError as e:
            return {
                'success': False,
                'error': f'战法已存在: {name}。如需覆盖，请使用 overwrite=True'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'创建战法失败: {str(e)}'
            }

    def _parse_input(self, input_text: str) -> Dict:
        """解析用户输入"""
        import re

        # 模式1: 新增战法-筛选:王子战法 描述内容
        pattern1 = r'新增战法[-_]*筛选[:：]\s*(\S+)\s*(.*)'
        match1 = re.match(pattern1, input_text)
        if match1:
            return {
                'name': match1.group(1),
                'description': match1.group(2).strip()
            }

        # 模式2: 新增战法 王子战法 描述内容
        pattern2 = r'新增战法\s+(\S+)\s+(.*)'
        match2 = re.match(pattern2, input_text)
        if match2:
            return {
                'name': match2.group(1),
                'description': match2.group(2).strip()
            }

        # 模式3: Create strategy <name> <description>
        pattern3 = r'[Cc]reate\s+[Ss]trategy\s+(\S+)\s+(.*)'
        match3 = re.match(pattern3, input_text)
        if match3:
            return {
                'name': match3.group(1),
                'description': match3.group(2).strip(),
                'author': 'AI'
            }

        return None

    def execute_strategy(self, strategy_name: str, stock_data: Dict, params: Dict = None) -> Dict:
        """
        执行战法筛选

        参数:
            strategy_name: 战法名称
            stock_data: 股票数据
            params: 战法参数（可选）

        返回:
            {'passed': bool, 'strategy': str, 'message': str}
        """
        try:
            # 先尝试custom，再尝试builtin
            try:
                result = self.manager.execute_strategy(strategy_name, stock_data, params, category='custom')
                category = 'custom'
            except FileNotFoundError:
                result = self.manager.execute_strategy(strategy_name, stock_data, params, category='builtin')
                category = 'builtin'

            strategy_info = self.manager.get_strategy_info(strategy_name, category)

            return {
                'passed': result,
                'strategy': strategy_name,
                'category': category,
                'message': f"{'✓ 通过' if result else '✗ 未通过'} {strategy_name}",
                'description': strategy_info['metadata']['description']
            }

        except FileNotFoundError:
            return {
                'passed': False,
                'strategy': strategy_name,
                'message': f'战法不存在: {strategy_name}'
            }
        except Exception as e:
            return {
                'passed': False,
                'strategy': strategy_name,
                'message': f'执行战法出错: {str(e)}'
            }

    def list_strategies(self, category: str = None) -> Dict:
        """
        列出所有战法

        参数:
            category: 战法类别 ('builtin', 'custom', None=全部)

        返回:
            {'strategies': [...], 'total': int}
        """
        strategies = self.manager.list_strategies(category)

        return {
            'strategies': strategies,
            'total': len(strategies),
            'summary': f"共 {len(strategies)} 个战法"
        }

    def get_strategy_info(self, strategy_name: str) -> Dict:
        """获取战法详细信息"""
        try:
            # 先尝试custom
            try:
                info = self.manager.get_strategy_info(strategy_name, category='custom')
            except FileNotFoundError:
                info = self.manager.get_strategy_info(strategy_name, category='builtin')

            return {
                'success': True,
                'info': info
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': f'战法不存在: {strategy_name}'
            }

    def delete_strategy(self, strategy_name: str) -> Dict:
        """删除战法（仅支持custom）"""
        try:
            result = self.manager.delete_strategy(strategy_name, category='custom')
            return {
                'success': result,
                'message': f'战法 "{strategy_name}" 已删除' if result else f'战法不存在: {strategy_name}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'删除失败: {str(e)}'
            }

    def export_strategy(self, strategy_name: str, output_path: str) -> Dict:
        """导出战法"""
        try:
            result = self.manager.export_strategy(strategy_name, output_path, category='custom')
            return {
                'success': True,
                'message': f'战法已导出到: {result}',
                'file': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'导出失败: {str(e)}'
            }

    def import_strategy(self, file_path: str, name: str = None) -> Dict:
        """导入战法"""
        try:
            result = self.manager.import_strategy(file_path, name, category='custom')
            return {
                'success': True,
                'message': f'战法已导入: {result}',
                'file': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'导入失败: {str(e)}'
            }


# 全局API实例
_strategy_api = None


def get_strategy_api() -> StrategyAPI:
    """获取全局战法API实例"""
    global _strategy_api
    if _strategy_api is None:
        _strategy_api = StrategyAPI()
    return _strategy_api


# 便捷函数
def create_strategy(input_text: str) -> Dict:
    """创建战法"""
    return get_strategy_api().create_strategy(input_text)


def execute_strategy(strategy_name: str, stock_data: Dict, params: Dict = None) -> Dict:
    """执行战法"""
    return get_strategy_api().execute_strategy(strategy_name, stock_data, params)


def list_strategies(category: str = None) -> Dict:
    """列出所有战法"""
    return get_strategy_api().list_strategies(category)


if __name__ == '__main__':
    # 测试
    api = get_strategy_api()

    # 列出内置战法
    print("=== 内置战法 ===")
    result = api.list_strategies('builtin')
    for s in result['strategies']:
        print(f"- {s['metadata']['name']}: {s['metadata']['description'][:50]}")

    # 创建新战法
    print("\n=== 创建新战法 ===")
    result = api.create_strategy("新增战法-筛选:王子战法 阴线且MA5大于MA10且换手率大于5%")
    if result['success']:
        print(f"✓ {result['message']}")
        print(f"文件: {result['strategy_file']}")

    # 再次列出所有战法
    print("\n=== 所有战法 ===")
    result = api.list_strategies()
    print(result['summary'])
