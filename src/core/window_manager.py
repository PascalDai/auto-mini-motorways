"""
窗口管理器
负责查找、管理Mini Motorways游戏窗口
"""

import time
import subprocess
import pyautogui
import json
from typing import Optional, Tuple, List
from ..utils.logger import get_logger
from ..utils.config import get_config


class WindowManager:
    """游戏窗口管理器"""
    
    def __init__(self):
        """初始化窗口管理器"""
        self.config = get_config()
        self.logger = get_logger()
        self.game_window = None
        self.window_title = self.config.get('game.window_title', 'Mini Motorways')
        self.expected_resolution = self.config.get('game.expected_resolution', [1920, 1080])
        
        # 禁用pyautogui的安全特性，允许程序控制鼠标
        pyautogui.FAILSAFE = False
        
        # macOS窗口信息（当找到窗口时会更新）
        self.window_info = {
            'found': False,
            'app_name': None,
            'window_bounds': None
        }
    
    def _get_mini_motorways_window_info(self) -> Optional[dict]:
        """
        使用AppleScript获取Mini Motorways窗口的准确信息
        
        Returns:
            窗口信息字典或None
        """
        try:
            # 首先尝试激活应用，确保窗口可见
            activate_script = '''
            tell application "Mini Motorways"
                try
                    activate
                    delay 0.5
                on error
                    -- 应用可能没有运行或无法激活
                end try
            end tell
            '''
            
            subprocess.run(['osascript', '-e', activate_script], 
                          capture_output=True, text=True, timeout=5)
            
            # 使用更健壮的AppleScript获取Mini Motorways窗口信息
            script = '''
            tell application "System Events"
                try
                    -- 方法1: 直接查找Mini Motorways进程
                    set miniMotorwaysProcess to first process whose name is "Mini Motorways"
                    
                    -- 检查是否有窗口
                    if (count of windows of miniMotorwaysProcess) > 0 then
                        set miniMotorwaysWindow to first window of miniMotorwaysProcess
                        
                        set windowPosition to position of miniMotorwaysWindow
                        set windowSize to size of miniMotorwaysWindow
                        set windowTitle to title of miniMotorwaysWindow
                        
                        set windowX to item 1 of windowPosition
                        set windowY to item 2 of windowPosition
                        set windowWidth to item 1 of windowSize
                        set windowHeight to item 2 of windowSize
                        
                        return "{" & quote & "found" & quote & ":true," & quote & "title" & quote & ":" & quote & windowTitle & quote & "," & quote & "x" & quote & ":" & windowX & "," & quote & "y" & quote & ":" & windowY & "," & quote & "width" & quote & ":" & windowWidth & "," & quote & "height" & quote & ":" & windowHeight & "}"
                    else
                        return "{" & quote & "found" & quote & ":false," & quote & "error" & quote & ":" & quote & "Mini Motorways process has no windows" & quote & "}"
                    end if
                    
                on error errMsg
                    -- 方法2: 尝试查找包含"Mini Motorways"的窗口
                    try
                        repeat with proc in (every process whose background only is false)
                            repeat with win in (every window of proc)
                                set winTitle to title of win
                                if winTitle contains "Mini Motorways" or name of proc contains "Mini Motorways" then
                                    set windowPosition to position of win
                                    set windowSize to size of win
                                    
                                    set windowX to item 1 of windowPosition
                                    set windowY to item 2 of windowPosition
                                    set windowWidth to item 1 of windowSize
                                    set windowHeight to item 2 of windowSize
                                    
                                    return "{" & quote & "found" & quote & ":true," & quote & "title" & quote & ":" & quote & winTitle & quote & "," & quote & "x" & quote & ":" & windowX & "," & quote & "y" & quote & ":" & windowY & "," & quote & "width" & quote & ":" & windowWidth & "," & quote & "height" & quote & ":" & windowHeight & "}"
                                end if
                            end repeat
                        end repeat
                        
                        return "{" & quote & "found" & quote & ":false," & quote & "error" & quote & ":" & quote & "No Mini Motorways window found in any process" & quote & "}"
                        
                    on error errMsg2
                        return "{" & quote & "found" & quote & ":false," & quote & "error" & quote & ":" & quote & errMsg2 & quote & "}"
                    end try
                end try
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                self.logger.add_info(f"AppleScript输出: {output}")
                
                try:
                    # 解析JSON格式的输出
                    window_data = json.loads(output)
                    return window_data
                except json.JSONDecodeError:
                    self.logger.add_warning(f"无法解析窗口信息: {output}")
                    return None
            else:
                self.logger.add_warning(f"获取窗口信息失败: {result.stderr}")
                return None
                
        except Exception as e:
            self.logger.add_error(f"获取窗口信息异常: {str(e)}")
            return None
    
    def _check_game_running_macos(self) -> bool:
        """
        检查游戏是否在macOS上运行
        
        Returns:
            游戏是否运行
        """
        try:
            # 检查Mini Motorways进程是否存在
            result = subprocess.run(['pgrep', '-f', 'Mini Motorways'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.add_success("检测到Mini Motorways进程正在运行")
                return True
            else:
                # 尝试另一种检查方式
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                if 'Mini Motorways' in result.stdout:
                    self.logger.add_success("通过ps命令检测到Mini Motorways")
                    return True
                else:
                    self.logger.add_warning("未检测到Mini Motorways进程")
                    return False
                    
        except Exception as e:
            self.logger.add_error(f"检查游戏进程失败: {str(e)}")
            return False
    
    def find_game_window(self, max_attempts: int = 10, wait_interval: float = 1.0) -> bool:
        """
        查找游戏窗口
        
        Args:
            max_attempts: 最大尝试次数
            wait_interval: 每次尝试间隔时间（秒）
            
        Returns:
            是否成功找到窗口
        """
        self.logger.add_section("窗口查找")
        self.logger.add_info(f"开始查找游戏窗口: {self.window_title}")
        
        # 首先检查游戏是否在运行
        if not self._check_game_running_macos():
            self.logger.add_error("Mini Motorways游戏未运行，请先启动游戏")
            return False
        
        # 尝试获取准确的窗口信息
        for attempt in range(max_attempts):
            self.logger.add_info(f"第 {attempt + 1} 次尝试获取窗口信息...")
            
            window_data = self._get_mini_motorways_window_info()
            
            if window_data and window_data.get('found', False):
                # 成功获取到窗口信息
                self.window_info = {
                    'found': True,
                    'app_name': 'Mini Motorways',
                    'window_bounds': {
                        'left': window_data['x'],
                        'top': window_data['y'],
                        'width': window_data['width'],
                        'height': window_data['height']
                    }
                }
                
                self.logger.add_success("成功获取游戏窗口信息")
                self.logger.add_info(f"窗口标题: {window_data.get('title', 'Unknown')}")
                self.logger.add_info(f"窗口位置: ({window_data['x']}, {window_data['y']})")
                self.logger.add_info(f"窗口大小: {window_data['width']}x{window_data['height']}")
                
                # 验证窗口大小
                self._validate_window_size()
                
                return True
            else:
                self.logger.add_warning(f"第 {attempt + 1} 次尝试失败")
                if attempt < max_attempts - 1:
                    time.sleep(wait_interval)
        
        # 如果所有尝试都失败，回退到全屏模式
        self.logger.add_warning("无法获取准确窗口信息，使用全屏模式作为备选")
        screen_width, screen_height = pyautogui.size()
        
        self.window_info = {
            'found': True,
            'app_name': 'Mini Motorways',
            'window_bounds': {
                'left': 0,
                'top': 0,
                'width': screen_width,
                'height': screen_height
            }
        }
        
        self.logger.add_warning("使用全屏区域作为窗口边界")
        self.logger.add_info(f"屏幕分辨率: {screen_width}x{screen_height}")
        
        return True
    
    def _validate_window_size(self):
        """验证窗口大小是否符合预期"""
        if not self.window_info['found']:
            return
        
        bounds = self.window_info['window_bounds']
        current_size = (bounds['width'], bounds['height'])
        expected_size = tuple(self.expected_resolution)
        
        if current_size != expected_size:
            self.logger.add_warning(
                f"窗口大小不匹配 - 当前: {current_size}, 期望: {expected_size}"
            )
            self.logger.add_info("这在macOS上是正常的，系统会自动适配")
        else:
            self.logger.add_success("窗口大小符合预期")
    
    def restore_window(self) -> bool:
        """
        恢复窗口（在macOS上尝试激活应用）
        
        Returns:
            是否成功恢复
        """
        try:
            # 使用osascript激活Mini Motorways应用
            script = 'tell application "Mini Motorways" to activate'
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                self.logger.add_success("游戏应用已激活")
                time.sleep(1)  # 等待应用激活
                return True
            else:
                self.logger.add_warning(f"激活应用失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.add_error(f"恢复窗口失败: {str(e)}")
            return False
    
    def activate_window(self) -> bool:
        """
        激活游戏窗口（置于前台）
        
        Returns:
            是否成功激活
        """
        return self.restore_window()  # 在macOS上两者相同
    
    def get_window_region(self) -> Optional[Tuple[int, int, int, int]]:
        """
        获取窗口区域坐标
        
        Returns:
            窗口区域 (left, top, width, height) 或 None
        """
        if not self.window_info['found']:
            return None
        
        bounds = self.window_info['window_bounds']
        return (
            bounds['left'],
            bounds['top'],
            bounds['width'],
            bounds['height']
        )
    
    def get_window_center(self) -> Optional[Tuple[int, int]]:
        """
        获取窗口中心坐标
        
        Returns:
            窗口中心坐标 (x, y) 或 None
        """
        region = self.get_window_region()
        if not region:
            return None
        
        left, top, width, height = region
        center_x = left + width // 2
        center_y = top + height // 2
        
        return (center_x, center_y)
    
    def is_window_valid(self) -> bool:
        """
        检查窗口是否仍然有效
        
        Returns:
            窗口是否有效
        """
        return self.window_info['found'] and self._check_game_running_macos()
    
    def refresh_window_info(self) -> bool:
        """
        刷新窗口信息
        
        Returns:
            是否成功刷新
        """
        if not self.is_window_valid():
            self.logger.add_warning("当前窗口无效，重新查找")
            return self.find_game_window()
        
        return True
    
    def get_window_screenshot_region(self) -> Optional[Tuple[int, int, int, int]]:
        """
        获取用于截图的窗口区域
        
        Returns:
            截图区域 (left, top, width, height) 或 None
        """
        if not self.window_info['found']:
            return None
        
        # 检查是否有自定义截图区域配置
        custom_region = self.config.get('game.screenshot_region')
        if custom_region:
            return tuple(custom_region)
        
        # 使用整个窗口区域
        return self.get_window_region()
    
    def list_all_windows(self) -> List[str]:
        """
        列出所有窗口标题（用于调试）
        
        Returns:
            所有窗口标题列表
        """
        try:
            # 使用AppleScript获取所有窗口信息
            script = '''
            tell application "System Events"
                set windowList to {}
                repeat with proc in (every process whose background only is false)
                    try
                        repeat with win in (every window of proc)
                            set windowList to windowList & {name of proc as string & " - " & name of win as string}
                        end repeat
                    end try
                end repeat
                return windowList
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    # 解析窗口列表
                    windows = output.split(', ')
                    self.logger.add_info(f"检测到 {len(windows)} 个窗口")
                    return windows
                else:
                    return []
            else:
                self.logger.add_warning(f"获取窗口列表失败: {result.stderr}")
                return []
                
        except Exception as e:
            self.logger.add_error(f"获取窗口列表失败: {str(e)}")
            return []
    
    def debug_window_info(self):
        """调试：显示当前窗口信息"""
        self.logger.add_section("窗口调试信息")
        
        # 显示所有窗口
        windows = self.list_all_windows()
        self.logger.add_info("当前所有窗口:")
        for i, window in enumerate(windows[:10]):  # 只显示前10个
            self.logger.add_info(f"  {i+1}. {window}")
        
        # 显示当前窗口信息
        if self.window_info['found']:
            bounds = self.window_info['window_bounds']
            self.logger.add_info("当前游戏窗口信息:")
            self.logger.add_info(f"  位置: ({bounds['left']}, {bounds['top']})")
            self.logger.add_info(f"  大小: {bounds['width']}x{bounds['height']}")
        else:
            self.logger.add_warning("当前未找到游戏窗口") 