"""
窗口查找模块
专门用于查找和定位Mini Motorways游戏窗口
支持多屏幕环境
"""

import subprocess
import re
import logging
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)

class WindowFinder:
    """窗口查找器类"""
    
    def __init__(self):
        """初始化窗口查找器"""
        self.game_window_titles = [
            "Mini Motorways",
            "mini motorways", 
            "MINI MOTORWAYS",
            "Mini Motorways - Steam",
            "Mini Motorways - Epic Games"
        ]
        logger.info("窗口查找器已初始化")
    
    def get_all_windows(self) -> List[Dict]:
        """
        获取所有窗口信息
        返回窗口信息列表
        """
        try:
            # 使用AppleScript获取所有窗口信息
            script = '''
            tell application "System Events"
                set windowList to {}
                repeat with proc in (every process whose background only is false)
                    try
                        set procName to name of proc
                        repeat with win in (every window of proc)
                            try
                                set winName to name of win
                                set winPos to position of win
                                set winSize to size of win
                                set windowInfo to procName & "|" & winName & "|" & (item 1 of winPos) & "|" & (item 2 of winPos) & "|" & (item 1 of winSize) & "|" & (item 2 of winSize)
                                set end of windowList to windowInfo
                            end try
                        end repeat
                    end try
                end repeat
                return windowList
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.error(f"获取窗口信息失败: {result.stderr}")
                return []
            
            windows = []
            for line in result.stdout.strip().split(', '):
                if line and '|' in line:
                    try:
                        parts = line.strip().split('|')
                        if len(parts) >= 6:
                            window_info = {
                                'process': parts[0],
                                'title': parts[1],
                                'x': int(parts[2]),
                                'y': int(parts[3]),
                                'width': int(parts[4]),
                                'height': int(parts[5])
                            }
                            windows.append(window_info)
                    except (ValueError, IndexError) as e:
                        logger.debug(f"解析窗口信息失败: {line}, 错误: {e}")
                        continue
            
            logger.info(f"找到 {len(windows)} 个窗口")
            return windows
            
        except Exception as e:
            logger.error(f"获取窗口信息时出错: {e}")
            return []
    
    def find_game_window(self) -> Optional[Dict]:
        """
        查找Mini Motorways游戏窗口
        返回窗口信息字典
        """
        all_windows = self.get_all_windows()
        
        # 记录所有窗口信息用于调试
        logger.info("当前所有窗口:")
        for i, window in enumerate(all_windows):
            logger.info(f"  {i+1}. 进程: {window['process']}, 标题: '{window['title']}', 位置: ({window['x']}, {window['y']}), 大小: {window['width']}x{window['height']}")
        
        # 查找游戏窗口
        for window in all_windows:
            window_title = window['title'].strip()
            process_name = window['process'].strip()
            
            # 检查窗口标题
            for game_title in self.game_window_titles:
                if game_title.lower() in window_title.lower():
                    logger.info(f"✅ 找到游戏窗口: {window_title}")
                    return window
            
            # 检查进程名称
            if 'mini' in process_name.lower() and 'motorways' in process_name.lower():
                logger.info(f"✅ 通过进程名找到游戏窗口: {process_name}")
                return window
        
        logger.warning("❌ 未找到Mini Motorways游戏窗口")
        logger.info("💡 请确保:")
        logger.info("   1. Mini Motorways游戏已经打开")
        logger.info("   2. 游戏窗口不是最小化状态")
        logger.info("   3. 游戏窗口在当前桌面空间中可见")
        
        return None
    
    def get_window_region(self, window_info: Dict) -> Tuple[int, int, int, int]:
        """
        获取窗口的捕获区域
        返回 (x, y, width, height) 元组
        """
        return (
            window_info['x'],
            window_info['y'], 
            window_info['width'],
            window_info['height']
        )
    
    def is_window_valid(self, window_info: Dict) -> bool:
        """
        检查窗口信息是否有效
        """
        if not window_info:
            return False
        
        # 检查窗口大小是否合理
        if window_info['width'] < 100 or window_info['height'] < 100:
            logger.warning(f"窗口尺寸太小: {window_info['width']}x{window_info['height']}")
            return False
        
        # 检查窗口位置是否合理（不能完全在屏幕外）
        if window_info['x'] < -window_info['width'] or window_info['y'] < -window_info['height']:
            logger.warning(f"窗口位置异常: ({window_info['x']}, {window_info['y']})")
            return False
        
        return True
    
    def find_and_validate_game_window(self) -> Optional[Dict]:
        """
        查找并验证游戏窗口
        返回有效的窗口信息或None
        """
        window_info = self.find_game_window()
        
        if window_info and self.is_window_valid(window_info):
            return window_info
        
        return None 