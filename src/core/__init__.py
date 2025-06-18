"""
核心模块
包含窗口管理、截图、游戏状态识别等核心功能
"""

from .window_manager import WindowManager
from .screenshot import ScreenshotManager

__all__ = [
    'WindowManager',
    'ScreenshotManager'
] 