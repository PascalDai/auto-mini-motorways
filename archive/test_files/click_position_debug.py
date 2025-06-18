#!/usr/bin/env python3
"""
点击位置调试工具：分析坐标转换和点击位置的准确性
"""

from game_capture import GameCapture
from game_controller import GameController
from ui_detector import UIDetector
import cv2
import numpy as np
import time

def main():
    print("🎯 点击位置调试工具")
    print("=" * 50)
    
    try:
        # 初始化组件
        game_capture = GameCapture()
        ui_detector = UIDetector()
        
        # 查找游戏窗口
        window_info = game_capture.find_game_window()
        if 'error' in window_info:
            print(f"❌ 未找到游戏窗口: {window_info['error']}")
            return
        
        print("🎮 游戏窗口信息:")
        print(f"   位置: ({window_info['x']}, {window_info['y']})")
        print(f"   大小: {window_info['width']}x{window_info['height']}")
        
        # 设置游戏控制器
        window_bounds = (window_info['x'], window_info['y'], window_info['width'], window_info['height'])
        game_controller = GameController(window_bounds)
        
        # 捕获画面
        pil_screenshot = game_capture.capture_screen()
        if pil_screenshot is None:
            print("❌ 截图失败")
            return
        
        screenshot = cv2.cvtColor(np.array(pil_screenshot), cv2.COLOR_RGB2BGR)
        print(f"📸 截图尺寸: {screenshot.shape[1]}x{screenshot.shape[0]}")
        
        # 检测游玩按钮
        play_button = ui_detector.find_best_play_button(screenshot)
        if not play_button:
            print("❌ 未找到游玩按钮")
            return
        
        print(f"\n🎯 游玩按钮检测结果:")
        print(f"   检测位置: {play_button['center']}")
        print(f"   置信度: {play_button['confidence']:.3f}")
        if 'size' in play_button:
            print(f"   按钮大小: {play_button['size']}")
        else:
            print(f"   按钮大小: 未知")
        
        # 计算实际点击位置
        button_x, button_y = play_button['center']
        
        # 坐标转换计算
        print(f"\n🔄 坐标转换分析:")
        print(f"   截图尺寸: {screenshot.shape[1]}x{screenshot.shape[0]}")
        print(f"   游戏窗口: {window_info['width']}x{window_info['height']}")
        print(f"   缩放比例: {screenshot.shape[1]/window_info['width']:.2f}x")
        
        # 转换到窗口坐标
        scale_x = window_info['width'] / screenshot.shape[1]
        scale_y = window_info['height'] / screenshot.shape[0]
        
        window_x = int(button_x * scale_x)
        window_y = int(button_y * scale_y)
        
        print(f"   窗口内坐标: ({window_x}, {window_y})")
        
        # 转换到屏幕坐标
        screen_x = window_info['x'] + window_x
        screen_y = window_info['y'] + window_y
        
        print(f"   屏幕坐标: ({screen_x}, {screen_y})")
        
        # 验证坐标是否在游戏窗口内
        if (window_info['x'] <= screen_x <= window_info['x'] + window_info['width'] and
            window_info['y'] <= screen_y <= window_info['y'] + window_info['height']):
            print("   ✅ 点击位置在游戏窗口内")
        else:
            print("   ❌ 点击位置超出游戏窗口范围")
        
        # 检查按钮位置是否合理
        expected_button_y = screenshot.shape[0] * 0.85  # 预期按钮在底部85%位置
        actual_button_y_percent = button_y / screenshot.shape[0]
        
        print(f"\n📍 按钮位置分析:")
        print(f"   按钮Y坐标: {button_y}")
        print(f"   按钮Y位置百分比: {actual_button_y_percent:.1%}")
        print(f"   预期位置: 底部85%左右")
        
        if 0.8 <= actual_button_y_percent <= 0.95:
            print("   ✅ 按钮位置合理")
        else:
            print("   ⚠️ 按钮位置可能有问题")
        
        # 在截图上标记按钮位置
        debug_image = screenshot.copy()
        cv2.circle(debug_image, (int(button_x), int(button_y)), 10, (0, 255, 0), 3)
        cv2.putText(debug_image, f"Button ({int(button_x)}, {int(button_y)})", 
                   (int(button_x) + 15, int(button_y) - 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # 保存调试图片
        debug_filename = f"../data/click_position_debug_{int(time.time())}.png"
        cv2.imwrite(debug_filename, debug_image)
        print(f"\n💾 调试图片已保存: {debug_filename}")
        
        # 询问是否执行测试点击
        print(f"\n🤔 是否执行测试点击？")
        print(f"   将点击屏幕坐标: ({screen_x}, {screen_y})")
        print(f"   游戏窗口将被激活")
        
        response = input("输入 'y' 执行测试点击，其他键取消: ").strip().lower()
        
        if response == 'y':
            print(f"\n🚀 执行测试点击...")
            
            # 激活窗口
            print("1️⃣ 激活游戏窗口...")
            game_controller.activate_game_window()
            time.sleep(1)
            
            # 点击
            print("2️⃣ 执行点击...")
            success = game_controller.click_ui_element(play_button)
            
            if success:
                print("   ✅ 点击命令执行成功")
                print("   请观察游戏是否有响应")
            else:
                print("   ❌ 点击命令执行失败")
        else:
            print("❌ 已取消测试点击")
        
    except Exception as e:
        print(f"❌ 调试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 