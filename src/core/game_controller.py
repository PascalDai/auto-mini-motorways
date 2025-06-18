"""
游戏控制模块
用于执行鼠标点击、键盘输入等游戏操作
"""

import pyautogui
import time
import logging
from typing import Tuple, Optional, Dict, List
import random
import subprocess
import platform

logger = logging.getLogger(__name__)

class GameController:
    """游戏控制器类"""
    
    def __init__(self, window_bounds: Optional[Tuple[int, int, int, int]] = None):
        """
        初始化游戏控制器
        
        Args:
            window_bounds: 游戏窗口边界 (x, y, width, height)
        """
        # 设置PyAutoGUI安全设置
        pyautogui.FAILSAFE = True  # 鼠标移到屏幕角落时停止
        pyautogui.PAUSE = 0.1      # 每次操作间隔
        
        self.window_bounds = window_bounds
        self.last_click_time = 0
        self.min_click_interval = 0.5  # 最小点击间隔（秒）
        
        # 预定义的城市选择策略
        self.city_preferences = [
            'Los Angeles',  # 洛杉矶（通常是第一个）
            'Tokyo',        # 东京
            'London',       # 伦敦
            'Cairo',        # 开罗
            'Beijing'       # 北京
        ]
        
        logger.info("游戏控制器已初始化")
        if window_bounds:
            logger.info(f"游戏窗口边界: {window_bounds}")
    
    def set_window_bounds(self, bounds: Tuple[int, int, int, int]):
        """设置游戏窗口边界"""
        self.window_bounds = bounds
        logger.info(f"更新游戏窗口边界: {bounds}")
    
    def activate_game_window(self) -> bool:
        """
        激活游戏窗口，使其成为前台窗口
        
        Returns:
            操作是否成功
        """
        try:
            logger.info("正在激活游戏窗口...")
            
            if platform.system() == "Darwin":  # macOS
                # 使用AppleScript激活Mini Motorways窗口
                script = '''
                tell application "System Events"
                    set frontmost of first process whose name is "Mini Motorways" to true
                end tell
                '''
                result = subprocess.run(['osascript', '-e', script], 
                                      capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    logger.info("成功激活游戏窗口")
                    time.sleep(0.5)  # 等待窗口激活
                    return True
                else:
                    logger.warning(f"AppleScript激活失败: {result.stderr}")
                    # 尝试备用方法：点击窗口标题栏
                    return self._activate_window_by_click()
                    
            elif platform.system() == "Windows":  # Windows
                # 在Windows上使用win32gui（如果可用）
                try:
                    import win32gui
                    import win32con
                    
                    def enum_windows_callback(hwnd, windows):
                        if win32gui.IsWindowVisible(hwnd):
                            window_text = win32gui.GetWindowText(hwnd)
                            if "Mini Motorways" in window_text:
                                windows.append(hwnd)
                        return True
                    
                    windows = []
                    win32gui.EnumWindows(enum_windows_callback, windows)
                    
                    if windows:
                        hwnd = windows[0]
                        win32gui.SetForegroundWindow(hwnd)
                        logger.info("成功激活游戏窗口")
                        time.sleep(0.5)
                        return True
                    else:
                        logger.warning("未找到Mini Motorways窗口")
                        return False
                        
                except ImportError:
                    logger.warning("win32gui未安装，使用备用激活方法")
                    return self._activate_window_by_click()
                    
            else:  # Linux或其他系统
                # 使用xdotool（如果可用）
                try:
                    result = subprocess.run(['xdotool', 'search', '--name', 'Mini Motorways', 'windowactivate'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        logger.info("成功激活游戏窗口")
                        time.sleep(0.5)
                        return True
                    else:
                        logger.warning("xdotool激活失败")
                        return self._activate_window_by_click()
                except FileNotFoundError:
                    logger.warning("xdotool未安装，使用备用激活方法")
                    return self._activate_window_by_click()
            
        except Exception as e:
            logger.error(f"激活游戏窗口时出错: {e}")
            return self._activate_window_by_click()
    
    def _activate_window_by_click(self) -> bool:
        """
        通过点击窗口来激活（备用方法）
        
        Returns:
            操作是否成功
        """
        try:
            if not self.window_bounds:
                logger.error("未设置窗口边界，无法激活窗口")
                return False
            
            # 点击窗口标题栏中央来激活窗口
            window_x, window_y, window_width, _ = self.window_bounds
            title_bar_x = window_x + window_width // 2
            title_bar_y = window_y + 10  # 标题栏通常在窗口顶部
            
            logger.info(f"通过点击标题栏激活窗口: ({title_bar_x}, {title_bar_y})")
            pyautogui.click(title_bar_x, title_bar_y)
            time.sleep(0.5)  # 等待窗口激活
            
            return True
            
        except Exception as e:
            logger.error(f"通过点击激活窗口失败: {e}")
            return False
    
    def _wait_for_click_interval(self):
        """等待点击间隔，避免操作过快"""
        current_time = time.time()
        elapsed = current_time - self.last_click_time
        
        if elapsed < self.min_click_interval:
            wait_time = self.min_click_interval - elapsed
            logger.debug(f"等待 {wait_time:.2f} 秒后执行点击")
            time.sleep(wait_time)
    
    def _convert_to_screen_coordinates(self, game_x: int, game_y: int) -> Tuple[int, int]:
        """
        将游戏内坐标转换为屏幕坐标
        
        Args:
            game_x, game_y: 游戏内相对坐标
            
        Returns:
            屏幕绝对坐标
        """
        if not self.window_bounds:
            logger.warning("未设置游戏窗口边界，使用游戏坐标作为屏幕坐标")
            return (game_x, game_y)
        
        window_x, window_y, _, _ = self.window_bounds
        screen_x = window_x + game_x
        screen_y = window_y + game_y
        
        logger.debug(f"游戏坐标 ({game_x}, {game_y}) -> 屏幕坐标 ({screen_x}, {screen_y})")
        return (screen_x, screen_y)
    
    def click_at_position(self, x: int, y: int, relative_to_game: bool = True, 
                         double_click: bool = False, duration: float = 0.1) -> bool:
        """
        在指定位置点击
        
        Args:
            x, y: 点击坐标
            relative_to_game: 是否为游戏内相对坐标
            double_click: 是否双击
            duration: 点击持续时间
            
        Returns:
            操作是否成功
        """
        try:
            self._wait_for_click_interval()
            
            # 转换坐标
            if relative_to_game:
                screen_x, screen_y = self._convert_to_screen_coordinates(x, y)
            else:
                screen_x, screen_y = x, y
            
            # 检查坐标是否在合理范围内（考虑多屏幕环境）
            screen_width, screen_height = pyautogui.size()
            
            # 对于多屏幕环境，允许负坐标（第二个显示器可能在负坐标区域）
            # 但要确保坐标不会过分超出合理范围
            max_negative_x = -screen_width * 2  # 允许最多两个屏幕宽度的负坐标
            max_negative_y = -screen_height * 2  # 允许最多两个屏幕高度的负坐标
            max_positive_x = screen_width * 3    # 允许最多三个屏幕宽度的正坐标
            max_positive_y = screen_height * 3   # 允许最多三个屏幕高度的正坐标
            
            if not (max_negative_x <= screen_x <= max_positive_x and max_negative_y <= screen_y <= max_positive_y):
                logger.error(f"点击坐标超出合理范围: ({screen_x}, {screen_y})")
                logger.debug(f"允许范围: X[{max_negative_x}, {max_positive_x}], Y[{max_negative_y}, {max_positive_y}]")
                return False
            
            # 执行点击
            if double_click:
                pyautogui.doubleClick(screen_x, screen_y, duration=duration)
                logger.info(f"双击位置: ({screen_x}, {screen_y})")
            else:
                pyautogui.click(screen_x, screen_y, duration=duration)
                logger.info(f"点击位置: ({screen_x}, {screen_y})")
            
            self.last_click_time = time.time()
            return True
            
        except Exception as e:
            logger.error(f"点击操作失败: {e}")
            return False
    
    def click_ui_element(self, element_info: Dict, double_click: bool = False) -> bool:
        """
        点击UI元素
        
        Args:
            element_info: UI元素信息字典（包含center坐标）
            double_click: 是否双击
            
        Returns:
            操作是否成功
        """
        try:
            if 'center' not in element_info:
                logger.error("UI元素信息缺少center坐标")
                return False
            
            center_x, center_y = element_info['center']
            description = element_info.get('description', '未知元素')
            
            logger.info(f"准备点击 {description} 在位置 ({center_x}, {center_y})")
            
            # 添加小幅随机偏移，模拟人类点击
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
            
            return self.click_at_position(
                center_x + offset_x, 
                center_y + offset_y, 
                relative_to_game=True,
                double_click=double_click
            )
            
        except Exception as e:
            logger.error(f"点击UI元素失败: {e}")
            return False
    
    def start_game_from_main_menu(self, play_button_info: Dict) -> bool:
        """
        从主界面开始游戏
        
        Args:
            play_button_info: 开始游戏按钮信息
            
        Returns:
            操作是否成功
        """
        try:
            logger.info("开始从主界面启动游戏")
            
            # 首先激活游戏窗口
            logger.info("激活游戏窗口以确保点击生效...")
            if not self.activate_game_window():
                logger.warning("激活游戏窗口失败，但继续尝试点击")
            
            # 等待窗口激活完成
            time.sleep(1.0)
            
            # 点击开始游戏按钮
            logger.info("窗口已激活，现在点击游玩按钮...")
            if not self.click_ui_element(play_button_info):
                logger.error("点击开始游戏按钮失败")
                return False
            
            # 等待界面切换
            time.sleep(2.0)
            logger.info("已点击开始游戏按钮，等待界面切换")
            
            return True
            
        except Exception as e:
            logger.error(f"从主界面开始游戏失败: {e}")
            return False
    
    def select_city(self, city_selection_info: Dict, city_preference: str = None) -> bool:
        """
        选择城市
        
        Args:
            city_selection_info: 城市选择区域信息
            city_preference: 首选城市名称
            
        Returns:
            操作是否成功
        """
        try:
            logger.info("开始选择城市")
            
            # 如果没有指定首选城市，使用默认的第一个
            if not city_preference:
                city_preference = self.city_preferences[0]
            
            # 点击城市选择区域
            if not self.click_ui_element(city_selection_info):
                logger.error("点击城市选择区域失败")
                return False
            
            # 等待城市列表展开
            time.sleep(1.0)
            
            # 这里可以添加更复杂的城市识别和选择逻辑
            # 目前简单地点击区域中心作为默认选择
            logger.info(f"选择城市: {city_preference}")
            
            # 再次点击确认选择
            time.sleep(0.5)
            self.click_ui_element(city_selection_info)
            
            time.sleep(1.0)
            logger.info("城市选择完成")
            
            return True
            
        except Exception as e:
            logger.error(f"选择城市失败: {e}")
            return False
    
    def navigate_to_game_start(self) -> bool:
        """
        导航到游戏开始（处理可能的额外界面）
        
        Returns:
            操作是否成功
        """
        try:
            logger.info("导航到游戏开始")
            
            # 寻找并点击可能的"开始"或"确认"按钮
            # 这里可以添加更多的界面识别逻辑
            
            # 尝试按Enter键确认
            pyautogui.press('enter')
            time.sleep(1.0)
            
            # 或者尝试按空格键
            pyautogui.press('space')
            time.sleep(1.0)
            
            logger.info("游戏导航完成")
            return True
            
        except Exception as e:
            logger.error(f"导航到游戏开始失败: {e}")
            return False
    
    def perform_emergency_stop(self):
        """执行紧急停止操作"""
        try:
            logger.warning("执行紧急停止操作")
            
            # 按ESC键暂停游戏
            pyautogui.press('esc')
            time.sleep(0.5)
            
            # 移动鼠标到安全位置（屏幕中心）
            screen_width, screen_height = pyautogui.size()
            pyautogui.moveTo(screen_width // 2, screen_height // 2)
            
            logger.info("紧急停止操作完成")
            
        except Exception as e:
            logger.error(f"紧急停止操作失败: {e}")
    
    def get_current_mouse_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置"""
        try:
            x, y = pyautogui.position()
            
            # 如果设置了游戏窗口边界，转换为游戏内坐标
            if self.window_bounds:
                window_x, window_y, _, _ = self.window_bounds
                game_x = x - window_x
                game_y = y - window_y
                logger.debug(f"屏幕坐标 ({x}, {y}) -> 游戏坐标 ({game_x}, {game_y})")
                return (game_x, game_y)
            
            return (x, y)
            
        except Exception as e:
            logger.error(f"获取鼠标位置失败: {e}")
            return (0, 0)
    
    def simulate_human_behavior(self, duration: float = 1.0):
        """模拟人类行为（随机小幅鼠标移动）"""
        try:
            current_x, current_y = pyautogui.position()
            
            # 小幅随机移动
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-10, 10)
            
            target_x = current_x + offset_x
            target_y = current_y + offset_y
            
            # 平滑移动
            pyautogui.moveTo(target_x, target_y, duration=duration)
            
            logger.debug(f"模拟人类鼠标移动: ({current_x}, {current_y}) -> ({target_x}, {target_y})")
            
        except Exception as e:
            logger.debug(f"模拟人类行为时出错: {e}") 