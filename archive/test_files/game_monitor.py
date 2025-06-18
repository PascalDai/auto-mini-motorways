#!/usr/bin/env python3

"""
游戏状态实时监控脚本

结合画面捕获和图像分析，实时监控Mini Motorways游戏状态
为后续的自动化操作做准备
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent))

from game_capture import GameCapture
from image_analyzer import ImageAnalyzer
from window_finder import WindowFinder
from config import GAME_SETTINGS

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GameMonitor:
    """游戏状态监控器"""
    
    def __init__(self):
        """初始化监控器"""
        self.window_finder = WindowFinder()
        self.game_capture = GameCapture()
        self.image_analyzer = ImageAnalyzer()
        
        self.current_state = 'unknown'
        self.state_history = []
        self.monitoring = False
        
        logger.info("游戏监控器已初始化")
    
    def check_game_window(self) -> bool:
        """检查游戏窗口是否可用"""
        try:
            window_info = self.window_finder.find_and_validate_game_window()
            if window_info:
                logger.info(f"游戏窗口正常 - 位置: ({window_info['x']}, {window_info['y']}), 大小: {window_info['width']}x{window_info['height']}")
                return True
            else:
                logger.warning("未找到游戏窗口")
                return False
        except Exception as e:
            logger.error(f"检查游戏窗口时出错: {e}")
            return False
    
    def capture_and_analyze(self) -> Optional[Dict]:
        """捕获并分析当前游戏状态"""
        try:
            # 查找游戏窗口
            window_info = self.game_capture.find_game_window()
            if not window_info:
                logger.warning("无法找到游戏窗口，跳过本次分析")
                return None
            
            # 获取窗口区域
            region = self.window_finder.get_window_region(window_info)
            
            # 捕获屏幕
            screenshot = self.game_capture.capture_screen(region)
            if screenshot is None:
                logger.error("屏幕捕获失败")
                return None
            
            # 保存临时截图用于分析
            temp_file = f"temp_analysis_{int(time.time())}.png"
            temp_path = Path("data/screenshots") / temp_file
            
            try:
                screenshot.save(temp_path, format='PNG')
                
                # 分析图像
                analysis_result = self.image_analyzer.analyze_image(str(temp_path))
                
                # 删除临时文件
                temp_path.unlink()
                
                return analysis_result
                
            except Exception as e:
                # 确保临时文件被删除
                if temp_path.exists():
                    temp_path.unlink()
                raise e
                
        except Exception as e:
            logger.error(f"捕获和分析时出错: {e}")
            return None
    
    def update_state(self, analysis_result: Dict) -> bool:
        """更新游戏状态"""
        try:
            if 'error' in analysis_result:
                logger.error(f"分析结果包含错误: {analysis_result['error']}")
                return False
            
            new_state = analysis_result.get('game_state', 'unknown')
            state_name = analysis_result.get('game_state_name', '未知')
            
            # 检查状态是否发生变化
            if new_state != self.current_state:
                logger.info(f"游戏状态变化: {self.current_state} -> {new_state} ({state_name})")
                
                # 记录状态变化
                self.state_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'old_state': self.current_state,
                    'new_state': new_state,
                    'state_name': state_name,
                    'analysis_details': analysis_result.get('analysis_details', {})
                })
                
                self.current_state = new_state
                return True
            else:
                logger.debug(f"游戏状态保持: {state_name}")
                return False
                
        except Exception as e:
            logger.error(f"更新状态时出错: {e}")
            return False
    
    def print_status(self, analysis_result: Dict):
        """打印当前状态信息"""
        try:
            state_name = analysis_result.get('game_state_name', '未知')
            details = analysis_result.get('analysis_details', {})
            
            print(f"\r🎮 当前状态: {state_name}", end="")
            
            # 显示详细信息
            if 'color_analysis' in details:
                color_info = details['color_analysis']
                if 'background_ratio' in color_info:
                    bg_ratio = color_info['background_ratio']
                    print(f" | 背景: {bg_ratio:.1%}", end="")
            
            # 刷新显示
            sys.stdout.flush()
            
        except Exception as e:
            logger.error(f"打印状态时出错: {e}")
    
    def start_monitoring(self, interval: float = 2.0, duration: Optional[float] = None):
        """开始监控"""
        logger.info(f"开始游戏状态监控 - 间隔: {interval}秒")
        
        if duration:
            logger.info(f"监控持续时间: {duration}秒")
        
        self.monitoring = True
        start_time = time.time()
        
        try:
            # 初始检查
            if not self.check_game_window():
                print("❌ 游戏窗口检查失败，请确保游戏正在运行")
                return
            
            print("🔍 开始实时监控游戏状态...")
            print("   按 Ctrl+C 可以停止监控")
            print()
            
            while self.monitoring:
                # 检查持续时间
                if duration and (time.time() - start_time) > duration:
                    logger.info("监控时间到达，停止监控")
                    break
                
                # 捕获和分析
                analysis_result = self.capture_and_analyze()
                
                if analysis_result:
                    # 更新状态
                    state_changed = self.update_state(analysis_result)
                    
                    # 打印状态
                    self.print_status(analysis_result)
                    
                    # 如果状态发生变化，显示详细信息
                    if state_changed:
                        print()  # 换行
                        self.print_state_change_details()
                else:
                    print(f"\r❌ 分析失败", end="")
                    sys.stdout.flush()
                
                # 等待下次检查
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  监控被用户中断")
        except Exception as e:
            logger.error(f"监控过程中出现错误: {e}")
        finally:
            self.monitoring = False
            self.print_monitoring_summary()
    
    def print_state_change_details(self):
        """打印状态变化详情"""
        if self.state_history:
            latest_change = self.state_history[-1]
            print(f"📊 状态变化详情:")
            print(f"   时间: {latest_change['timestamp']}")
            print(f"   变化: {latest_change['old_state']} → {latest_change['new_state']}")
            print(f"   描述: {latest_change['state_name']}")
            print()
    
    def print_monitoring_summary(self):
        """打印监控总结"""
        print("\n" + "="*60)
        print("📊 监控总结")
        print("="*60)
        print(f"最终状态: {self.current_state}")
        print(f"状态变化次数: {len(self.state_history)}")
        
        if self.state_history:
            print("\n状态变化历史:")
            for i, change in enumerate(self.state_history, 1):
                timestamp = change['timestamp'].split('T')[1][:8]  # 只显示时间
                print(f"  {i}. {timestamp} - {change['old_state']} → {change['new_state']}")
        
        print("="*60)
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        logger.info("监控已停止")

def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("🔍 Mini Motorways - 游戏状态实时监控")
    print("=" * 60)
    print()
    print("这个程序会实时监控游戏状态变化")
    print("包括主界面、游戏进行中、暂停等状态")
    print()

def main():
    """主函数"""
    print_welcome()
    
    try:
        # 创建监控器
        monitor = GameMonitor()
        
        # 开始监控
        monitor.start_monitoring(
            interval=GAME_SETTINGS['capture_interval'],  # 使用配置的间隔
            duration=60.0  # 监控1分钟
        )
        
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 