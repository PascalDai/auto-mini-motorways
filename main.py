#!/usr/bin/env python3
"""
Mini Motorways 自动化系统主启动脚本
"""

import sys
import time
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.logger import get_logger, reset_logger
from src.utils.config import get_config
from src.core.window_manager import WindowManager
from src.core.screenshot import ScreenshotManager


def main():
    """主函数"""
    # 初始化日志和配置
    logger = reset_logger()  # 重置日志，开始新会话
    config = get_config()
    
    logger.add_section("系统启动", level=1)
    logger.add_success("Mini Motorways 自动化系统启动")
    
    try:
        # 初始化核心组件
        logger.add_section("组件初始化")
        
        # 窗口管理器
        window_manager = WindowManager()
        logger.add_success("窗口管理器初始化完成")
        
        # 截图管理器
        screenshot_manager = ScreenshotManager()
        logger.add_success("截图管理器初始化完成")
        
        # 查找游戏窗口
        logger.add_section("游戏窗口查找")
        if not window_manager.find_game_window():
            logger.add_error("未找到游戏窗口，请确保Mini Motorways正在运行")
            return False
        
        # 激活窗口
        if window_manager.activate_window():
            logger.add_success("游戏窗口已激活")
        
        # 获取窗口信息
        window_region = window_manager.get_window_screenshot_region()
        if window_region:
            logger.add_info(f"截图区域: {window_region}")
        
        # 进行测试截图
        logger.add_section("测试截图")
        screenshot_path = screenshot_manager.take_screenshot(
            region=window_region,
            description="系统测试截图"
        )
        
        if screenshot_path:
            logger.add_success("测试截图成功")
            logger.add_image("测试截图", screenshot_path)
            
            # 创建一个简单的标记示例
            test_elements = [
                {
                    'name': '窗口中心',
                    'coordinates': window_manager.get_window_center() or (960, 540),
                    'confidence': 1.0,
                    'type': 'info'
                }
            ]
            
            marked_path = screenshot_manager.create_marked_screenshot(
                screenshot_path, 
                test_elements,
                "测试标记截图"
            )
            
            if marked_path:
                logger.add_success("标记截图创建成功")
                logger.add_image("标记截图", marked_path)
        
        # 显示统计信息
        logger.add_section("系统统计")
        screenshot_stats = screenshot_manager.get_screenshot_stats()
        for key, value in screenshot_stats.items():
            logger.add_info(f"{key}: {value}")
        
        logger.add_section("系统测试完成")
        logger.add_success("所有基础功能测试通过")
        logger.add_info("系统已准备就绪，可以开始游戏自动化")
        
        return True
        
    except Exception as e:
        logger.add_error(f"系统启动失败: {str(e)}")
        return False
    
    finally:
        # 结束会话
        logger.finalize_session()


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 系统启动成功！")
        print("📋 请查看 logs/session_log.md 获取详细日志")
        print("📸 截图保存在 screenshots/ 目录下")
    else:
        print("\n❌ 系统启动失败！")
        print("📋 请查看 logs/session_log.md 了解错误详情")
    
    sys.exit(0 if success else 1) 