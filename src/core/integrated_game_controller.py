#!/usr/bin/env python3
"""
集成版游戏控制器 - 整合所有修复
包含多显示器支持、鼠标移动、精确点击等功能
"""

from game_capture_fixed import GameCaptureFixed
from ui_detector import UIDetector
from image_analyzer import ImageAnalyzer
import cv2
import numpy as np
import time
import subprocess
import pyautogui
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedGameController:
    """集成版游戏控制器"""
    
    def __init__(self):
        """初始化控制器"""
        self.game_capture = GameCaptureFixed()
        self.ui_detector = UIDetector()
        self.image_analyzer = ImageAnalyzer()
        self.window_info = None
        
        # 禁用pyautogui安全检查
        pyautogui.FAILSAFE = False
        
        logger.info("集成版游戏控制器已初始化")
    
    def find_and_setup_game_window(self):
        """查找并设置游戏窗口"""
        logger.info("查找游戏窗口...")
        
        self.window_info = self.game_capture.find_game_window()
        if not self.window_info or 'error' in self.window_info:
            logger.error(f"未找到游戏窗口: {self.window_info.get('error', '未知错误')}")
            return False
        
        logger.info(f"找到游戏窗口: 位置({self.window_info['x']}, {self.window_info['y']}), "
                   f"大小{self.window_info['width']}x{self.window_info['height']}")
        return True
    
    def activate_game_window(self):
        """激活游戏窗口"""
        logger.info("激活游戏窗口...")
        
        try:
            script = '''
            tell application "Mini Motorways"
                activate
            end tell
            tell application "System Events"
                set frontmost of first process whose name is "Mini Motorways" to true
            end tell
            '''
            subprocess.run(['osascript', '-e', script], check=True)
            logger.info("窗口激活成功")
            time.sleep(1)
            return True
        except Exception as e:
            logger.warning(f"窗口激活失败: {e}")
            return False
    
    def capture_game_state(self):
        """捕获并分析游戏状态"""
        logger.info("捕获游戏状态...")
        
        # 捕获游戏窗口
        screenshot = self.game_capture.capture_game_window()
        if not screenshot:
            logger.error("游戏窗口捕获失败")
            return None, None
        
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # 分析游戏状态
        game_state = self.image_analyzer.detect_game_state(screenshot_cv)
        logger.info(f"当前游戏状态: {game_state}")
        
        return screenshot_cv, game_state
    
    def detect_play_button(self, screenshot):
        """检测游玩按钮"""
        logger.info("检测游玩按钮...")
        
        play_button = self.ui_detector.find_best_play_button(screenshot)
        if not play_button:
            logger.warning("未找到游玩按钮")
            return None
        
        logger.info(f"找到游玩按钮: 位置{play_button['center']}, 置信度{play_button['confidence']:.3f}")
        return play_button
    
    def calculate_screen_coordinates(self, button_position):
        """计算屏幕坐标"""
        if not self.window_info:
            logger.error("窗口信息未初始化")
            return None, None
        
        button_x, button_y = button_position
        screen_x = self.window_info['x'] + button_x
        screen_y = self.window_info['y'] + button_y
        
        logger.info(f"坐标转换: 窗口内({button_x}, {button_y}) -> 屏幕({screen_x}, {screen_y})")
        return screen_x, screen_y
    
    def move_and_click(self, screen_x, screen_y):
        """移动鼠标并点击"""
        logger.info(f"移动鼠标到({screen_x}, {screen_y})并点击...")
        
        try:
            # 获取当前鼠标位置
            current_x, current_y = pyautogui.position()
            logger.info(f"当前鼠标位置: ({current_x}, {current_y})")
            
            # 移动鼠标
            pyautogui.moveTo(screen_x, screen_y, duration=0.5)
            
            # 确认移动
            new_x, new_y = pyautogui.position()
            logger.info(f"移动后位置: ({new_x}, {new_y})")
            
            # 短暂等待
            time.sleep(0.5)
            
            # 点击
            pyautogui.click()
            logger.info("点击执行完成")
            
            return True
            
        except Exception as e:
            logger.error(f"移动并点击失败: {e}")
            return False
    
    def click_play_button(self):
        """点击游玩按钮的完整流程"""
        logger.info("开始点击游玩按钮流程...")
        
        try:
            # 1. 确保窗口信息可用
            if not self.window_info:
                if not self.find_and_setup_game_window():
                    return False
            
            # 2. 激活游戏窗口
            self.activate_game_window()
            
            # 3. 捕获游戏状态
            screenshot, game_state = self.capture_game_state()
            if screenshot is None:
                return False
            
            # 4. 检查是否在主菜单
            if game_state != "main_menu":
                logger.warning(f"当前不在主菜单状态: {game_state}")
                return False
            
            # 5. 检测游玩按钮
            play_button = self.detect_play_button(screenshot)
            if not play_button:
                return False
            
            # 6. 计算屏幕坐标
            screen_x, screen_y = self.calculate_screen_coordinates(play_button['center'])
            if screen_x is None:
                return False
            
            # 7. 移动鼠标并点击
            if not self.move_and_click(screen_x, screen_y):
                return False
            
            # 8. 等待游戏响应
            logger.info("等待游戏响应...")
            time.sleep(3)
            
            # 9. 验证状态变化
            _, new_game_state = self.capture_game_state()
            if new_game_state and new_game_state != game_state:
                logger.info(f"成功！游戏状态从 {game_state} 变为 {new_game_state}")
                return True
            else:
                logger.warning("游戏状态未改变")
                return False
                
        except Exception as e:
            logger.error(f"点击游玩按钮过程中出现错误: {e}")
            return False
    
    def start_game_automation(self):
        """启动游戏自动化"""
        logger.info("启动游戏自动化系统...")
        
        try:
            # 初始化
            if not self.find_and_setup_game_window():
                return False
            
            # 捕获初始状态
            screenshot, initial_state = self.capture_game_state()
            if screenshot is None:
                return False
            
            logger.info(f"初始游戏状态: {initial_state}")
            
            # 如果在主菜单，点击游玩按钮
            if initial_state == "main_menu":
                logger.info("检测到主菜单，准备点击游玩按钮...")
                
                if self.click_play_button():
                    logger.info("成功进入游戏！")
                    return True
                else:
                    logger.error("点击游玩按钮失败")
                    return False
            else:
                logger.info(f"当前状态: {initial_state}，无需点击游玩按钮")
                return True
                
        except Exception as e:
            logger.error(f"游戏自动化启动失败: {e}")
            return False
    
    def save_debug_screenshot(self, screenshot, filename_suffix=""):
        """保存调试截图"""
        try:
            debug_filename = f"../data/integrated_debug_{filename_suffix}_{int(time.time())}.png"
            cv2.imwrite(debug_filename, screenshot)
            logger.info(f"调试截图已保存: {debug_filename}")
            return debug_filename
        except Exception as e:
            logger.error(f"保存调试截图失败: {e}")
            return None

def main():
    """主函数 - 演示集成版控制器"""
    print("🎮 集成版游戏控制器演示")
    print("=" * 50)
    
    # 创建控制器
    controller = IntegratedGameController()
    
    # 启动自动化
    print("🚀 启动游戏自动化...")
    success = controller.start_game_automation()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 游戏自动化启动成功！")
        print("✅ 系统已准备就绪")
    else:
        print("❌ 游戏自动化启动失败")
        print("💡 请检查日志了解详细信息")
    
    return success

if __name__ == "__main__":
    main() 