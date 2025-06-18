"""
修复版游戏画面捕获模块 - 解决多显示器问题
只捕获游戏窗口所在的区域，而不是整个桌面
"""

import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import subprocess
import re

import pyautogui
from PIL import Image
import numpy as np

from config import GAME_SETTINGS, CAPTURE_SETTINGS, SCREENSHOTS_DIR
from window_finder import WindowFinder

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameCaptureFixed:
    """修复版游戏画面捕获类 - 专门针对多显示器环境"""
    
    def __init__(self):
        """初始化捕获器"""
        self.window_info = None
        self.screenshot_count = 0
        self.window_finder = WindowFinder()
        
        # 禁用pyautogui的安全检查
        pyautogui.FAILSAFE = False
        
        logger.info("修复版游戏捕获器已初始化")
    
    def find_game_window(self) -> Optional[dict]:
        """查找Mini Motorways游戏窗口"""
        try:
            self.window_info = self.window_finder.find_and_validate_game_window()
            if self.window_info and 'error' not in self.window_info:
                logger.info(f"找到游戏窗口: 位置({self.window_info['x']}, {self.window_info['y']}), "
                           f"大小{self.window_info['width']}x{self.window_info['height']}")
            return self.window_info
        except Exception as e:
            logger.error(f"查找游戏窗口时出错: {e}")
            return {'error': str(e)}
    
    def capture_game_window(self) -> Optional[Image.Image]:
        """
        专门捕获游戏窗口区域
        这是修复多显示器问题的关键方法
        """
        try:
            # 确保有游戏窗口信息
            if not self.window_info or 'error' in self.window_info:
                logger.warning("没有有效的游戏窗口信息，尝试重新查找...")
                if not self.find_game_window() or 'error' in self.window_info:
                    logger.error("无法找到游戏窗口")
                    return None
            
            # 计算游戏窗口的屏幕区域
            x = self.window_info['x']
            y = self.window_info['y'] 
            width = self.window_info['width']
            height = self.window_info['height']
            
            logger.info(f"捕获游戏窗口区域: ({x}, {y}, {width}, {height})")
            
            # 使用pyautogui捕获指定区域
            # 注意：pyautogui的region参数是 (left, top, width, height)
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            logger.info(f"成功捕获游戏窗口，尺寸: {screenshot.size}")
            return screenshot
            
        except Exception as e:
            logger.error(f"捕获游戏窗口时出错: {e}")
            return None
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Image.Image]:
        """
        捕获屏幕画面 - 修复版
        优先捕获游戏窗口，而不是全屏
        """
        try:
            if region:
                # 捕获指定区域
                screenshot = pyautogui.screenshot(region=region)
                logger.info(f"捕获指定区域，尺寸: {screenshot.size}")
            else:
                # 默认捕获游戏窗口而不是全屏
                screenshot = self.capture_game_window()
                if screenshot is None:
                    logger.warning("游戏窗口捕获失败，回退到全屏捕获")
                    screenshot = pyautogui.screenshot()
                    logger.info(f"全屏捕获，尺寸: {screenshot.size}")
            
            return screenshot
            
        except Exception as e:
            logger.error(f"捕获屏幕时出错: {e}")
            return None
    
    def save_screenshot(self, image: Image.Image, filename: Optional[str] = None) -> bool:
        """保存截图到文件"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"fixed_{CAPTURE_SETTINGS['screenshot_prefix']}{timestamp}_{self.screenshot_count:03d}.png"
            
            filepath = SCREENSHOTS_DIR / filename
            
            # 保存图像
            image.save(filepath, 
                      format=GAME_SETTINGS['image_format'],
                      quality=GAME_SETTINGS['image_quality'])
            
            self.screenshot_count += 1
            logger.info(f"截图已保存: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"保存截图时出错: {e}")
            return False
    
    def test_capture(self) -> bool:
        """测试捕获功能"""
        print("🧪 测试修复版游戏捕获器")
        print("=" * 50)
        
        try:
            # 查找游戏窗口
            print("1️⃣ 查找游戏窗口...")
            window_info = self.find_game_window()
            if not window_info or 'error' in window_info:
                print(f"❌ 未找到游戏窗口: {window_info.get('error', '未知错误')}")
                return False
            
            print("✅ 找到游戏窗口")
            print(f"   位置: ({window_info['x']}, {window_info['y']})")
            print(f"   大小: {window_info['width']}x{window_info['height']}")
            
            # 测试捕获游戏窗口
            print("\n2️⃣ 测试游戏窗口捕获...")
            screenshot = self.capture_game_window()
            if screenshot is None:
                print("❌ 游戏窗口捕获失败")
                return False
            
            print("✅ 游戏窗口捕获成功")
            print(f"   截图尺寸: {screenshot.size}")
            
            # 保存测试截图
            print("\n3️⃣ 保存测试截图...")
            test_filename = f"test_fixed_capture_{int(time.time())}.png"
            if self.save_screenshot(screenshot, test_filename):
                print(f"✅ 测试截图已保存: {test_filename}")
            else:
                print("❌ 保存测试截图失败")
                return False
            
            # 验证截图内容
            print("\n4️⃣ 验证截图内容...")
            expected_width = window_info['width']
            expected_height = window_info['height']
            
            if screenshot.size == (expected_width, expected_height):
                print("✅ 截图尺寸匹配游戏窗口")
            else:
                print(f"⚠️ 截图尺寸不匹配:")
                print(f"   期望: {expected_width}x{expected_height}")
                print(f"   实际: {screenshot.size}")
            
            print("\n🎉 修复版捕获器测试完成！")
            return True
            
        except Exception as e:
            print(f"❌ 测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    # 测试修复版捕获器
    capture = GameCaptureFixed()
    capture.test_capture() 