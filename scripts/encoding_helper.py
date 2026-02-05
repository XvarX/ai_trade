"""
编码辅助工具 - 统一处理中文编码问题
确保在不同操作系统（Windows/Linux/macOS）上都能正确显示中文
"""
import sys
import io
import os


def setup_utf8_output():
    """
    设置标准输出为UTF-8编码

    Windows系统默认使用GBK编码，会导致中文输出乱码
    调用此函数可以确保中文正确显示

    用法：
        在脚本开头调用：
        from scripts.encoding_helper import setup_utf8_output
        setup_utf8_output()
    """
    if sys.platform == 'win32':
        try:
            # Windows: 重新配置stdout为UTF-8
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer,
                    encoding='utf-8',
                    errors='replace'
                )
            if hasattr(sys.stderr, 'buffer'):
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer,
                    encoding='utf-8',
                    errors='replace'
                )
        except (AttributeError, ValueError):
            # 如果设置失败，尝试使用环境变量
            os.environ['PYTHONIOENCODING'] = 'utf-8'


def auto_setup():
    """
    自动设置UTF-8编码（推荐使用）

    在脚本开头调用此函数，自动处理所有编码问题

    用法：
        from scripts.encoding_helper import auto_setup
        auto_setup()
    """
    setup_utf8_output()

    # 设置环境变量
    if 'PYTHONIOENCODING' not in os.environ:
        os.environ['PYTHONIOENCODING'] = 'utf-8'


# 便捷导出
__all__ = ['setup_utf8_output', 'auto_setup']
