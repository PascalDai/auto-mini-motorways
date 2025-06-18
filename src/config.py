"""
项目配置文件
包含所有可配置的参数和设置
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
LOGS_DIR = PROJECT_ROOT / "logs"

# 创建必要的目录
for directory in [DATA_DIR, SCREENSHOTS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# 游戏设置
GAME_SETTINGS = {
    "window_title": "Mini Motorways",  # 游戏窗口标题
    "capture_interval": 2.0,          # 截图间隔（秒）
    "image_format": "PNG",            # 图像格式
    "image_quality": 95,              # 图像质量
}

# 屏幕捕获设置
CAPTURE_SETTINGS = {
    "save_screenshots": True,         # 是否保存截图
    "max_screenshots": 100,           # 最大截图数量
    "screenshot_prefix": "game_",     # 截图文件前缀
}

# 日志设置
LOG_SETTINGS = {
    "log_level": "INFO",              # 日志级别
    "log_file": LOGS_DIR / "mini_motorways.log",
    "max_log_size": 10 * 1024 * 1024, # 最大日志文件大小 (10MB)
}

# 服务器设置（暂时未使用）
SERVER_SETTINGS = {
    "host": "localhost",
    "port": 8000,
    "api_endpoint": "/api/game-state",
}

print(f"配置已加载 - 项目根目录: {PROJECT_ROOT}")
print(f"截图保存目录: {SCREENSHOTS_DIR}")
print(f"日志保存目录: {LOGS_DIR}") 