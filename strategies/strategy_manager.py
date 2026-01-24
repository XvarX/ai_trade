"""
战法管理器 - 管理战法的加载、保存、执行
"""
import os
import importlib.util
import json
from typing import Dict, List, Callable, Any, Optional
from pathlib import Path


class StrategyManager:
    """战法管理器"""

    def __init__(self, strategy_dir: str = None):
        """
        初始化战法管理器
        strategy_dir: 战法目录，默认为当前strategies目录
        """
        if strategy_dir is None:
            # 使用当前文件的父目录作为战法根目录
            strategy_dir = os.path.dirname(__file__)

        self.strategy_dir = Path(strategy_dir)
        self.builtin_dir = self.strategy_dir / 'builtin'
        self.custom_dir = self.strategy_dir / 'custom'

        # 确保目录存在
        self.builtin_dir.mkdir(parents=True, exist_ok=True)
        self.custom_dir.mkdir(parents=True, exist_ok=True)

        # 战法缓存 {name: {'module': module, 'metadata': metadata}}
        self._strategies = {}

    def load_strategy(self, name: str, category: str = 'custom') -> Dict:
        """
        加载战法

        参数:
            name: 战法名称（文件名，不含.py）
            category: 战法类别 'builtin' 或 'custom'

        返回:
            {'screen_func': Callable, 'metadata': Dict, 'params': Dict}
        """
        cache_key = f"{category}.{name}"

        # 检查缓存
        if cache_key in self._strategies:
            return self._strategies[cache_key]

        # 确定文件路径
        strategy_dir = self.builtin_dir if category == 'builtin' else self.custom_dir
        strategy_file = strategy_dir / f"{name}.py"

        if not strategy_file.exists():
            raise FileNotFoundError(f"战法文件不存在: {strategy_file}")

        # 动态加载模块
        spec = importlib.util.spec_from_file_location(name, strategy_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"无法加载战法: {name}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 提取战法信息
        metadata = self._extract_metadata(module)
        screen_func = getattr(module, 'screen', None)
        default_params = getattr(module, 'get_default_params', lambda: {})()
        params_schema = getattr(module, 'get_params_schema', lambda: {})()

        if screen_func is None:
            raise AttributeError(f"战法缺少screen函数: {name}")

        # 缓存战法
        strategy_info = {
            'screen_func': screen_func,
            'metadata': metadata,
            'default_params': default_params,
            'params_schema': params_schema,
            'module': module
        }
        self._strategies[cache_key] = strategy_info

        return strategy_info

    def _extract_metadata(self, module) -> Dict:
        """从模块提取元数据"""
        metadata = {
            'name': getattr(module, 'STRATEGY_NAME', 'Unknown'),
            'description': getattr(module, 'STRATEGY_DESCRIPTION', ''),
            'author': getattr(module, 'STRATEGY_AUTHOR', 'Unknown'),
            'version': getattr(module, 'STRATEGY_VERSION', '1.0.0'),
            'category': getattr(module, 'STRATEGY_CATEGORY', 'custom'),
            'tags': getattr(module, 'STRATEGY_TAGS', [])
        }
        return metadata

    def execute_strategy(self, name: str, stock_data: Dict, params: Dict = None, category: str = 'custom') -> bool:
        """
        执行战法筛选

        参数:
            name: 战法名称
            stock_data: 股票数据
            params: 战法参数（可选，默认使用default_params）
            category: 战法类别

        返回:
            True: 符合战法条件
            False: 不符合
        """
        strategy = self.load_strategy(name, category)

        # 合并参数
        if params is None:
            params = {}
        final_params = {**strategy['default_params'], **params}

        # 执行筛选
        try:
            result = strategy['screen_func'](stock_data, **final_params)
            return bool(result)
        except Exception as e:
            print(f"战法执行出错 {name}: {e}")
            return False

    def save_strategy(self, name: str, code: str, category: str = 'custom', overwrite: bool = False) -> str:
        """
        保存战法代码

        参数:
            name: 战法名称
            code: 战法代码
            category: 战法类别
            overwrite: 是否覆盖已存在的战法

        返回:
            保存的文件路径
        """
        strategy_dir = self.builtin_dir if category == 'builtin' else self.custom_dir
        strategy_file = strategy_dir / f"{name}.py"

        # 检查文件是否存在
        if strategy_file.exists() and not overwrite:
            raise FileExistsError(f"战法已存在: {name}.py。使用 overwrite=True 来覆盖")

        # 保存代码
        strategy_file.write_text(code, encoding='utf-8')

        # 清除缓存
        cache_key = f"{category}.{name}"
        if cache_key in self._strategies:
            del self._strategies[cache_key]

        return str(strategy_file)

    def list_strategies(self, category: str = None) -> List[Dict]:
        """
        列出所有战法

        参数:
            category: 战法类别，None表示列出所有

        返回:
            战法信息列表
        """
        strategies = []

        search_dirs = []
        if category is None or category == 'builtin':
            search_dirs.append(('builtin', self.builtin_dir))
        if category is None or category == 'custom':
            search_dirs.append(('custom', self.custom_dir))

        for cat, dir_path in search_dirs:
            for py_file in dir_path.glob("*.py"):
                if py_file.name.startswith('_'):
                    continue

                name = py_file.stem
                try:
                    info = self.load_strategy(name, cat)
                    strategies.append({
                        'name': name,
                        'category': cat,
                        'file': str(py_file),
                        'metadata': info['metadata']
                    })
                except Exception as e:
                    # 加载失败，只返回基本信息
                    strategies.append({
                        'name': name,
                        'category': cat,
                        'file': str(py_file),
                        'metadata': {'name': name, 'description': f'加载失败: {e}'}
                    })

        return strategies

    def get_strategy_info(self, name: str, category: str = 'custom') -> Dict:
        """获取战法详细信息"""
        strategy = self.load_strategy(name, category)
        return {
            'name': name,
            'category': category,
            'metadata': strategy['metadata'],
            'default_params': strategy['default_params'],
            'params_schema': strategy['params_schema']
        }

    def delete_strategy(self, name: str, category: str = 'custom') -> bool:
        """删除战法"""
        strategy_dir = self.builtin_dir if category == 'builtin' else self.custom_dir
        strategy_file = strategy_dir / f"{name}.py"

        if not strategy_file.exists():
            return False

        # 删除文件
        strategy_file.unlink()

        # 清除缓存
        cache_key = f"{category}.{name}"
        if cache_key in self._strategies:
            del self._strategies[cache_key]

        return True

    def export_strategy(self, name: str, output_path: str, category: str = 'custom'):
        """导出战法到指定路径（用于分享）"""
        strategy_dir = self.builtin_dir if category == 'builtin' else self.custom_dir
        strategy_file = strategy_dir / f"{name}.py"

        if not strategy_file.exists():
            raise FileNotFoundError(f"战法不存在: {name}")

        import shutil
        shutil.copy2(strategy_file, output_path)
        return output_path

    def import_strategy(self, file_path: str, name: str = None, category: str = 'custom'):
        """导入战法文件（用于分享）"""
        import shutil

        src = Path(file_path)
        if not src.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 确定目标名称
        if name is None:
            name = src.stem

        strategy_dir = self.builtin_dir if category == 'builtin' else self.custom_dir
        dest = strategy_dir / f"{name}.py"

        if dest.exists():
            raise FileExistsError(f"战法已存在: {name}")

        shutil.copy2(src, dest)
        return str(dest)


# 全局战法管理器实例
_strategy_manager = None


def get_strategy_manager() -> StrategyManager:
    """获取全局战法管理器实例"""
    global _strategy_manager
    if _strategy_manager is None:
        _strategy_manager = StrategyManager()
    return _strategy_manager
