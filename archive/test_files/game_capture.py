"""
游戏画面捕获模块
负责捕获Mini Motorways游戏画面
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

class GameCapture:
    """游戏画面捕获类"""
    
    def __init__(self):
        """初始化捕获器"""
        self.window_info = None
        self.screenshot_count = 0
        self.window_finder = WindowFinder()
        
        # 禁用pyautogui的安全检查（避免鼠标移动到角落导致异常）
        pyautogui.FAILSAFE = False
        
        logger.info("游戏捕获器已初始化")
    
    def find_game_window(self) -> Optional[dict]:
        """
        查找Mini Motorways游戏窗口
        返回窗口信息字典，如果找不到返回None
        """
        try:
            self.window_info = self.window_finder.find_and_validate_game_window()
            return self.window_info
        except Exception as e:
            logger.error(f"查找游戏窗口时出错: {e}")
            return None
    
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Image.Image]:
        """
        捕获屏幕画面
        
        Args:
            region: 捕获区域 (x, y, width, height)，None表示全屏
            
        Returns:
            PIL Image对象，失败返回None
        """
        try:
            if region:
                # 捕获指定区域
                screenshot = pyautogui.screenshot(region=region)
            else:
                # 捕获全屏
                screenshot = pyautogui.screenshot()
            
            logger.info(f"成功捕获屏幕画面，尺寸: {screenshot.size}")
            return screenshot
            
        except Exception as e:
            logger.error(f"捕获屏幕时出错: {e}")
            return None
    
    def save_screenshot(self, image: Image.Image, filename: Optional[str] = None) -> bool:
        """
        保存截图到文件
        
        Args:
            image: PIL Image对象
            filename: 文件名，None则自动生成
            
        Returns:
            保存成功返回True，失败返回False
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{CAPTURE_SETTINGS['screenshot_prefix']}{timestamp}_{self.screenshot_count:03d}.png"
            
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
    
    def capture_and_save(self, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        捕获并保存屏幕画面
        
        Args:
            region: 捕获区域
            
        Returns:
            成功返回True，失败返回False
        """
        # 如果没有指定区域，但找到了游戏窗口，则使用游戏窗口区域
        if region is None and self.window_info:
            region = self.window_finder.get_window_region(self.window_info)
            logger.info(f"使用游戏窗口区域: {region}")
        
        # 捕获屏幕
        screenshot = self.capture_screen(region)
        if screenshot is None:
            return False
        
        # 保存截图
        if CAPTURE_SETTINGS['save_screenshots']:
            return self.save_screenshot(screenshot)
        
        return True
    
    def start_continuous_capture(self, duration: Optional[float] = None) -> None:
        """
        开始连续捕获
        
        Args:
            duration: 捕获持续时间（秒），None表示无限制
        """
        logger.info("开始连续捕获游戏画面...")
        
        # 首先查找游戏窗口
        if not self.find_game_window():
            logger.warning("未找到游戏窗口，将捕获全屏")
        
        start_time = time.time()
        capture_count = 0
        
        try:
            while True:
                # 检查是否超过持续时间
                if duration and (time.time() - start_time) > duration:
                    break
                
                # 检查是否超过最大截图数量
                if capture_count >= CAPTURE_SETTINGS['max_screenshots']:
                    logger.info(f"已达到最大截图数量限制: {CAPTURE_SETTINGS['max_screenshots']}")
                    break
                
                # 捕获并保存
                if self.capture_and_save():
                    capture_count += 1
                    logger.info(f"完成第 {capture_count} 次捕获")
                else:
                    logger.error("捕获失败")
                
                # 等待指定间隔
                time.sleep(GAME_SETTINGS['capture_interval'])
                
        except KeyboardInterrupt:
            logger.info("用户中断捕获")
        except Exception as e:
            logger.error(f"连续捕获时出错: {e}")
        finally:
            logger.info(f"捕获结束，总共捕获 {capture_count} 张截图")
    
    def get_screen_info(self) -> dict:
        """
        获取屏幕信息
        
        Returns:
            包含屏幕信息的字典
        """
        try:
            screen_size = pyautogui.size()
            return {
                "screen_width": screen_size.width,
                "screen_height": screen_size.height,
                "screenshot_count": self.screenshot_count
            }
        except Exception as e:
            logger.error(f"获取屏幕信息时出错: {e}")
            return {}

if __name__ == "__main__":
    # 测试代码
    capture = GameCapture()
    
    print("屏幕信息:", capture.get_screen_info())
    print("查找游戏窗口:", capture.find_game_window())
    
    # 捕获一张测试截图
    print("捕获测试截图...")
    capture.capture_and_save() 