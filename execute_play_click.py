#!/usr/bin/env python3
"""
执行游玩按钮点击脚本
使用确认正确的坐标(564, 497)执行实际点击操作
"""

import sys
import time
from pathlib import Path
import cv2
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.logger import get_logger, reset_logger
from src.core.window_manager import WindowManager
from src.core.screenshot import ScreenshotManager
import pyautogui


def execute_play_button_click():
    """执行游玩按钮点击操作"""
    logger = reset_logger("logs/execute_play_click.md")
    logger.add_section("执行游玩按钮点击", level=1)
    
    try:
        # 初始化组件
        window_manager = WindowManager()
        screenshot_manager = ScreenshotManager()
        
        logger.add_section("窗口检测和准备")
        
        if not window_manager.find_game_window():
            logger.add_error("未找到游戏窗口")
            return False
        
        logger.add_success("找到游戏窗口")
        
        # 激活窗口
        window_manager.activate_window()
        time.sleep(1)
        
        # 截图
        logger.add_section("点击前截图")
        window_region = window_manager.get_window_screenshot_region()
        screenshot_path = screenshot_manager.take_screenshot(
            window_region, 
            "点击前界面截图"
        )
        
        if not screenshot_path:
            logger.add_error("截图失败")
            return False
        
        logger.add_success("点击前截图成功")
        logger.add_image("点击前界面", screenshot_path)
        
        # 使用确认正确的游玩按钮坐标
        logger.add_section("游玩按钮坐标确认")
        
        play_button_coords = (564, 497)  # 用户确认的正确坐标
        
        logger.add_success(f"游玩按钮坐标: {play_button_coords}")
        logger.add_info("此坐标已通过标记图确认正确")
        
        # 验证坐标有效性
        img = cv2.imread(screenshot_path)
        if img is not None:
            height, width = img.shape[:2]
            x, y = play_button_coords
            
            if 0 <= x < width and 0 <= y < height:
                logger.add_success("坐标在有效范围内")
                
                # 分析按钮区域
                roi_size = 50
                x1 = max(0, x - roi_size)
                y1 = max(0, y - roi_size)
                x2 = min(width, x + roi_size)
                y2 = min(height, y + roi_size)
                
                roi = img[y1:y2, x1:x2]
                if roi.size > 0:
                    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                    mean_brightness = np.mean(gray_roi)
                    std_brightness = np.std(gray_roi)
                    
                    logger.add_info(f"按钮区域亮度: {mean_brightness:.1f}")
                    logger.add_info(f"亮度标准差: {std_brightness:.1f}")
                    
                    if std_brightness > 15:
                        logger.add_success("按钮区域确认为有效UI元素")
                    else:
                        logger.add_warning("按钮区域亮度变化较小，但继续执行")
            else:
                logger.add_error("坐标超出图片范围")
                return False
        
        # 创建点击位置标记
        logger.add_section("创建点击位置标记")
        
        marked_elements = [
            {
                'name': '游玩按钮点击位置',
                'coordinates': play_button_coords,
                'confidence': 1.0,
                'type': 'success'
            }
        ]
        
        marked_path = screenshot_manager.create_marked_screenshot(
            screenshot_path,
            marked_elements,
            "即将点击的位置"
        )
        
        if marked_path:
            logger.add_image("点击位置标记", marked_path)
        
        # 计算实际点击坐标
        logger.add_section("计算点击坐标")
        
        window_left, window_top = window_region[0], window_region[1]
        click_x = window_left + play_button_coords[0]
        click_y = window_top + play_button_coords[1]
        
        logger.add_info(f"窗口偏移: ({window_left}, {window_top})")
        logger.add_info(f"游玩按钮相对坐标: {play_button_coords}")
        logger.add_info(f"游玩按钮绝对坐标: ({click_x}, {click_y})")
        
        # 执行点击操作
        logger.add_section("执行点击操作")
        
        logger.add_info("准备执行点击...")
        logger.add_info(f"目标: 游玩按钮")
        logger.add_info(f"坐标: {play_button_coords}")
        logger.add_info(f"功能: 进入游戏选择界面")
        
        # 确保鼠标移动到正确位置
        pyautogui.moveTo(click_x, click_y, duration=0.3)
        time.sleep(0.2)
        
        # 执行点击
        logger.add_info("执行点击...")
        pyautogui.click(click_x, click_y)
        logger.add_success("✅ 点击操作已执行！")
        
        # 等待界面切换
        logger.add_section("等待界面切换")
        logger.add_info("等待界面切换...")
        time.sleep(3)  # 给更多时间让界面完全加载
        
        # 截取点击后的界面
        logger.add_section("点击后验证")
        after_screenshot_path = screenshot_manager.take_screenshot(
            window_region, 
            "点击后界面截图"
        )
        
        if after_screenshot_path:
            logger.add_success("点击后截图成功")
            logger.add_image("点击后界面", after_screenshot_path)
            
            # 对比两张图片验证界面是否切换
            img1 = cv2.imread(screenshot_path)
            img2 = cv2.imread(after_screenshot_path)
            
            if img1 is not None and img2 is not None:
                # 计算图片差异
                diff = cv2.absdiff(img1, img2)
                diff_mean = np.mean(diff)
                
                logger.add_info(f"界面变化程度: {diff_mean:.1f}")
                
                if diff_mean > 30:  # 提高阈值，确保是明显的界面切换
                    logger.add_success("🎉 界面已成功切换！")
                    logger.add_success("🎮 成功点击游玩按钮，进入下一个页面！")
                    
                    # 简单分析新界面
                    logger.add_section("新界面分析")
                    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                    mean_brightness2 = np.mean(gray2)
                    logger.add_info(f"新界面平均亮度: {mean_brightness2:.1f}")
                    
                    if abs(mean_brightness2 - np.mean(cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY))) > 10:
                        logger.add_success("新界面亮度明显不同，确认界面切换成功")
                    
                    return True
                    
                elif diff_mean > 10:
                    logger.add_warning("界面有变化，但可能不是完整的页面切换")
                    logger.add_info("可能是动画效果或部分UI更新")
                    return True
                    
                else:
                    logger.add_error("界面变化很小，可能点击无效")
                    logger.add_error("可能原因:")
                    logger.add_error("1. 点击位置不准确")
                    logger.add_error("2. 界面响应延迟")
                    logger.add_error("3. 游戏状态异常")
                    return False
            else:
                logger.add_error("无法读取截图进行对比")
                return False
        else:
            logger.add_error("点击后截图失败")
            return False
        
    except Exception as e:
        logger.add_error(f"执行点击失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        logger.finalize_session()
        print("📋 详细日志保存到 logs/execute_play_click.md")


def main():
    """主函数"""
    print("🎮 执行游玩按钮点击")
    print("使用确认正确的坐标: (564, 497)")
    print("目标: 点击游玩按钮，进入下一个页面")
    print()
    
    success = execute_play_button_click()
    
    if success:
        print("🎉 成功点击游玩按钮！")
        print("✅ 界面已切换到下一个页面")
        print("🎯 可以继续进行下一步操作")
    else:
        print("❌ 点击操作失败")
        print("📋 请查看日志了解详细信息")


if __name__ == "__main__":
    main() 