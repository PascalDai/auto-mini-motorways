"""
自动游戏启动器
整合窗口捕获、UI检测和游戏控制功能，实现从主界面到游戏开始的完整自动化流程
"""

import cv2
import numpy as np
import time
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path

from game_capture import GameCapture
from image_analyzer import ImageAnalyzer
from ui_detector import UIDetector
from game_controller import GameController

logger = logging.getLogger(__name__)

class AutoGameLauncher:
    """自动游戏启动器类"""
    
    def __init__(self):
        """初始化自动游戏启动器"""
        # 初始化各个组件
        self.game_capture = GameCapture()
        self.image_analyzer = ImageAnalyzer()
        self.ui_detector = UIDetector()
        self.game_controller = None  # 稍后初始化，需要窗口边界信息
        
        # 状态跟踪
        self.current_state = 'unknown'
        self.launch_attempts = 0
        self.max_launch_attempts = 3
        
        # 保存路径
        self.debug_save_path = Path("data/debug_images")
        self.debug_save_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("自动游戏启动器已初始化")
    
    def initialize_game_controller(self) -> bool:
        """初始化游戏控制器（需要窗口信息）"""
        try:
            # 获取游戏窗口信息
            window_info = self.game_capture.find_game_window()
            
            if not window_info or 'error' in window_info:
                logger.error("无法获取游戏窗口信息，无法初始化游戏控制器")
                return False
            
            # 提取窗口边界
            if not all(key in window_info for key in ['x', 'y', 'width', 'height']):
                logger.error("窗口信息中缺少坐标数据")
                return False
            
            bounds = (window_info['x'], window_info['y'], window_info['width'], window_info['height'])
            
            # 初始化游戏控制器
            self.game_controller = GameController(window_bounds=bounds)
            logger.info("游戏控制器初始化成功")
            
            return True
            
        except Exception as e:
            logger.error(f"初始化游戏控制器失败: {e}")
            return False
    
    def capture_and_analyze_current_state(self) -> Dict:
        """捕获并分析当前游戏状态"""
        try:
            # 确保找到游戏窗口
            window_info = self.game_capture.find_game_window()
            if not window_info or 'error' in window_info:
                return {'error': "未找到游戏窗口"}
            
            # 获取窗口区域
            region = self.game_capture.window_finder.get_window_region(window_info)
            
            # 捕获游戏画面
            screenshot = self.game_capture.capture_screen(region)
            if screenshot is None:
                return {'error': "捕获屏幕失败"}
            
            # 转换为OpenCV格式
            image_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 分析游戏状态
            game_state = self.image_analyzer.detect_game_state(image_cv)
            
            # 更新当前状态
            self.current_state = game_state
            
            # 创建状态结果
            state_result = {
                'game_state': game_state,
                'state_description': self.image_analyzer.game_states.get(game_state, '未知状态')
            }
            
            # 如果是主界面，进行UI元素检测
            ui_elements = {}
            if self.current_state == 'main_menu':
                ui_detection_result = self.ui_detector.analyze_main_menu_layout(image_cv)
                
                if 'error' not in ui_detection_result:
                    ui_elements = ui_detection_result
                    
                    # 保存调试图像
                    debug_image = self.ui_detector.create_debug_image(image_cv, ui_detection_result)
                    debug_path = self.debug_save_path / f"ui_debug_{int(time.time())}.png"
                    cv2.imwrite(str(debug_path), debug_image)
                    logger.info(f"UI调试图像已保存: {debug_path}")
            
            return {
                'game_state': self.current_state,
                'image_cv': image_cv,
                'state_analysis': state_result,
                'ui_elements': ui_elements,
                'window_info': window_info
            }
            
        except Exception as e:
            logger.error(f"捕获和分析当前状态失败: {e}")
            return {'error': str(e)}
    
    def wait_for_main_menu(self, timeout: int = 30, check_interval: float = 2.0) -> bool:
        """
        等待游戏进入主界面
        
        Args:
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            是否成功检测到主界面
        """
        try:
            logger.info(f"等待游戏进入主界面，超时时间: {timeout} 秒")
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # 分析当前状态
                analysis_result = self.capture_and_analyze_current_state()
                
                if 'error' in analysis_result:
                    logger.warning(f"状态分析出错: {analysis_result['error']}")
                    time.sleep(check_interval)
                    continue
                
                current_state = analysis_result.get('game_state', 'unknown')
                logger.info(f"当前游戏状态: {current_state}")
                
                if current_state == 'main_menu':
                    logger.info("检测到主界面")
                    return True
                
                # 等待下次检查
                time.sleep(check_interval)
            
            logger.warning("等待主界面超时")
            return False
            
        except Exception as e:
            logger.error(f"等待主界面时出错: {e}")
            return False
    
    def launch_game_from_main_menu(self) -> bool:
        """从主界面启动游戏"""
        try:
            logger.info("开始从主界面启动游戏")
            
            # 确保游戏控制器已初始化
            if not self.game_controller:
                if not self.initialize_game_controller():
                    logger.error("游戏控制器初始化失败")
                    return False
            
            # 分析当前状态
            analysis_result = self.capture_and_analyze_current_state()
            
            if 'error' in analysis_result:
                logger.error(f"状态分析失败: {analysis_result['error']}")
                return False
            
            if analysis_result['game_state'] != 'main_menu':
                logger.error(f"当前不在主界面，状态: {analysis_result['game_state']}")
                return False
            
            # 获取UI元素信息
            ui_elements = analysis_result.get('ui_elements', {})
            layout_analysis = ui_elements.get('layout_analysis', {})
            
            # 检查推荐操作
            recommended_action = layout_analysis.get('recommended_action', 'unknown')
            logger.info(f"推荐操作: {recommended_action}")
            
            # 执行相应操作
            if recommended_action == 'click_play_button':
                return self._handle_play_button_click(layout_analysis)
            
            elif recommended_action == 'select_city':
                # 在城市选择界面，寻找游玩按钮
                return self._handle_city_selection_with_play_button(layout_analysis)
            
            else:
                logger.warning(f"未知的推荐操作: {recommended_action}")
                # 尝试通用的启动流程
                return self._try_generic_launch_sequence()
            
        except Exception as e:
            logger.error(f"从主界面启动游戏失败: {e}")
            return False
    
    def _handle_play_button_click(self, layout_analysis: Dict) -> bool:
        """处理开始游戏按钮点击"""
        try:
            play_button_info = layout_analysis.get('play_button_info')
            
            if not play_button_info:
                logger.error("未找到开始游戏按钮信息")
                return False
            
            logger.info("找到开始游戏按钮，准备点击")
            
            # 点击开始游戏按钮
            if not self.game_controller.start_game_from_main_menu(play_button_info):
                logger.error("点击开始游戏按钮失败")
                return False
            
            # 等待界面切换并检查结果
            time.sleep(3.0)
            
            # 检查是否成功进入下一个界面
            analysis_result = self.capture_and_analyze_current_state()
            
            if 'error' not in analysis_result:
                new_state = analysis_result.get('game_state', 'unknown')
                logger.info(f"点击后的新状态: {new_state}")
                
                if new_state != 'main_menu':
                    logger.info("成功离开主界面")
                    return True
            
            logger.warning("点击开始游戏按钮后状态未改变")
            return False
            
        except Exception as e:
            logger.error(f"处理开始游戏按钮点击失败: {e}")
            return False
    
    def _handle_city_selection_with_play_button(self, layout_analysis: Dict) -> bool:
        """处理城市选择界面，寻找并点击游玩按钮"""
        try:
            # 首先检查是否有游玩按钮
            play_button_info = layout_analysis.get('play_button_info')
            
            if play_button_info:
                logger.info("在城市选择界面找到游玩按钮，准备点击")
                return self._handle_play_button_click(layout_analysis)
            
            # 如果没有检测到游玩按钮，重新分析当前画面
            logger.info("未在初始分析中找到游玩按钮，重新分析画面...")
            
            # 重新捕获和分析画面，专门寻找游玩按钮
            analysis_result = self.capture_and_analyze_current_state()
            
            if 'error' in analysis_result:
                logger.error("重新分析画面失败")
                return False
            
            ui_elements = analysis_result.get('ui_elements', {})
            layout_analysis_new = ui_elements.get('layout_analysis', {})
            
            play_button_info = layout_analysis_new.get('play_button_info')
            
            if play_button_info:
                logger.info("重新分析后找到游玩按钮")
                return self._handle_play_button_click(layout_analysis_new)
            
            # 如果仍然没有找到游玩按钮，尝试传统的城市选择流程
            logger.warning("未找到游玩按钮，尝试传统城市选择流程")
            return self._handle_city_selection_legacy(layout_analysis)
            
        except Exception as e:
            logger.error(f"处理城市选择界面失败: {e}")
            return False
    
    def _handle_city_selection_legacy(self, layout_analysis: Dict) -> bool:
        """处理传统的城市选择（备用方法）"""
        try:
            city_selection_info = layout_analysis.get('city_selection_info')
            
            if not city_selection_info:
                logger.error("未找到城市选择区域信息")
                return False
            
            logger.info("使用传统方法处理城市选择")
            
            # 选择城市
            if not self.game_controller.select_city(city_selection_info):
                logger.error("城市选择失败")
                return False
            
            # 等待并检查结果
            time.sleep(2.0)
            
            # 尝试继续导航到游戏开始
            return self.game_controller.navigate_to_game_start()
            
        except Exception as e:
            logger.error(f"传统城市选择处理失败: {e}")
            return False
    
    def _try_generic_launch_sequence(self) -> bool:
        """尝试通用的游戏启动序列"""
        try:
            logger.info("尝试通用的游戏启动序列")
            
            # 尝试按Enter键
            self.game_controller.navigate_to_game_start()
            time.sleep(2.0)
            
            # 检查状态变化
            analysis_result = self.capture_and_analyze_current_state()
            
            if 'error' not in analysis_result:
                new_state = analysis_result.get('game_state', 'unknown')
                logger.info(f"通用启动序列后的状态: {new_state}")
                
                if new_state != 'main_menu':
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"通用启动序列失败: {e}")
            return False
    
    def run_auto_launch_cycle(self, max_attempts: int = 3) -> bool:
        """
        运行完整的自动启动周期
        
        Args:
            max_attempts: 最大尝试次数
            
        Returns:
            是否成功启动游戏
        """
        try:
            logger.info(f"开始自动游戏启动周期，最大尝试次数: {max_attempts}")
            
            for attempt in range(1, max_attempts + 1):
                logger.info(f"第 {attempt} 次尝试启动游戏")
                
                # 等待主界面
                if not self.wait_for_main_menu(timeout=15):
                    logger.warning(f"第 {attempt} 次尝试：未检测到主界面")
                    continue
                
                # 尝试启动游戏
                if self.launch_game_from_main_menu():
                    logger.info(f"第 {attempt} 次尝试：游戏启动成功！")
                    return True
                
                logger.warning(f"第 {attempt} 次尝试：游戏启动失败")
                
                # 等待一段时间再重试
                if attempt < max_attempts:
                    wait_time = 5.0
                    logger.info(f"等待 {wait_time} 秒后重试")
                    time.sleep(wait_time)
            
            logger.error("所有启动尝试均失败")
            return False
            
        except Exception as e:
            logger.error(f"自动启动周期失败: {e}")
            return False
    
    def get_status_report(self) -> Dict:
        """获取当前状态报告"""
        try:
            # 获取当前状态
            analysis_result = self.capture_and_analyze_current_state()
            
            # 获取窗口信息
            window_info = self.game_capture.find_game_window()
            
            # 编译状态报告
            status_report = {
                'timestamp': time.time(),
                'current_state': self.current_state,
                'launch_attempts': self.launch_attempts,
                'game_controller_ready': self.game_controller is not None,
                'window_detected': 'error' not in window_info if window_info else False,
                'analysis_result': analysis_result
            }
            
            return status_report
            
        except Exception as e:
            logger.error(f"获取状态报告失败: {e}")
            return {'error': str(e)}
    
    def emergency_stop(self):
        """紧急停止所有操作"""
        try:
            logger.warning("执行紧急停止")
            
            if self.game_controller:
                self.game_controller.perform_emergency_stop()
            
            logger.info("紧急停止完成")
            
        except Exception as e:
            logger.error(f"紧急停止失败: {e}") 