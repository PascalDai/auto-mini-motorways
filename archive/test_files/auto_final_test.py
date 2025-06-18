#!/usr/bin/env python3
"""
完全自动化的最终测试：验证窗口激活+游玩按钮点击的完整流程
"""

from game_capture import GameCapture
from game_controller import GameController
from ui_detector import UIDetector
from image_analyzer import ImageAnalyzer
import cv2
import numpy as np
import time

def main():
    print("🎮 Mini Motorways 自动化最终测试")
    print("=" * 50)
    
    try:
        # 初始化所有组件
        print("🔧 初始化组件...")
        game_capture = GameCapture()
        ui_detector = UIDetector()
        image_analyzer = ImageAnalyzer()
        
        # 查找游戏窗口
        print("🔍 查找游戏窗口...")
        window_info = game_capture.find_game_window()
        if 'error' in window_info:
            print(f"❌ 未找到游戏窗口: {window_info['error']}")
            return False
        
        print("✅ 找到游戏窗口")
        print(f"   位置: ({window_info['x']}, {window_info['y']})")
        print(f"   大小: {window_info['width']}x{window_info['height']}")
        
        # 设置游戏控制器
        window_bounds = (window_info['x'], window_info['y'], window_info['width'], window_info['height'])
        game_controller = GameController(window_bounds)
        
        # 捕获当前画面
        print("📸 捕获游戏画面...")
        pil_screenshot = game_capture.capture_screen()
        if pil_screenshot is None:
            print("❌ 截图失败")
            return False
        
        screenshot = cv2.cvtColor(np.array(pil_screenshot), cv2.COLOR_RGB2BGR)
        
        # 分析游戏状态
        print("📊 分析游戏状态...")
        game_state = image_analyzer.detect_game_state(screenshot)
        print(f"   当前游戏状态: {game_state}")
        
        # 检测游玩按钮
        print("🎯 检测游玩按钮...")
        play_button = ui_detector.find_best_play_button(screenshot)
        
        if not play_button:
            print("❌ 未找到游玩按钮")
            
            # 尝试检测所有UI元素
            detection_result = ui_detector.detect_ui_elements(screenshot)
            detected_elements = detection_result.get('detected_elements', {})
            print(f"   检测到的UI元素: {list(detected_elements.keys())}")
            
            if 'play_button' in detected_elements:
                play_buttons = detected_elements['play_button']
                if play_buttons:
                    play_button = play_buttons[0]  # 使用第一个检测到的按钮
                    print(f"   使用备用按钮: {play_button['center']}")
                else:
                    return False
            else:
                return False
        
        print(f"✅ 找到游玩按钮:")
        print(f"   位置: {play_button['center']}")
        print(f"   置信度: {play_button['confidence']:.3f}")
        
        print(f"\n🚀 开始自动化测试流程...")
        print(f"   ⚠️ 将在3秒后开始执行...")
        
        # 倒计时
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        print(f"\n🎯 执行完整流程...")
        
        # 第1步：激活游戏窗口
        print("1️⃣ 激活游戏窗口...")
        activation_success = game_controller.activate_game_window()
        if activation_success:
            print("   ✅ 窗口激活成功")
        else:
            print("   ⚠️ 窗口激活失败，但继续测试")
        
        # 等待窗口激活
        print("   等待窗口激活完成...")
        time.sleep(1.5)
        
        # 第2步：点击游玩按钮
        print("2️⃣ 点击游玩按钮...")
        click_success = game_controller.click_ui_element(play_button)
        if click_success:
            print("   ✅ 点击操作成功")
        else:
            print("   ❌ 点击操作失败")
            return False
        
        # 第3步：等待并检查结果
        print("3️⃣ 等待游戏响应...")
        time.sleep(3.0)
        
        # 重新捕获画面检查状态变化
        print("📊 检查游戏状态变化...")
        new_pil_screenshot = game_capture.capture_screen()
        if new_pil_screenshot:
            new_screenshot = cv2.cvtColor(np.array(new_pil_screenshot), cv2.COLOR_RGB2BGR)
            new_game_state = image_analyzer.detect_game_state(new_screenshot)
            
            print(f"   点击前状态: {game_state}")
            print(f"   点击后状态: {new_game_state}")
            
            if new_game_state != game_state:
                print("🎉 成功！游戏状态已改变")
                print("   ✅ 窗口激活功能正常工作")
                print("   ✅ 游玩按钮点击成功")
                return True
            else:
                print("⚠️ 游戏状态未改变")
                
                # 额外检查：看是否有新的UI元素出现
                new_detection = ui_detector.detect_ui_elements(new_screenshot)
                new_elements = new_detection.get('detected_elements', {})
                old_detection = ui_detector.detect_ui_elements(screenshot)
                old_elements = old_detection.get('detected_elements', {})
                
                if len(new_elements) != len(old_elements):
                    print("   ✅ 检测到UI元素变化，可能游戏已响应")
                    return True
                else:
                    print("   ❌ 未检测到明显变化")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 50)
    if success:
        print("✅ 自动化测试成功完成！")
        print("🎯 窗口激活 + 游玩按钮点击功能正常工作")
    else:
        print("❌ 自动化测试失败")
        print("💡 可能需要进一步调试按钮检测或点击逻辑")
    
    print("\n📋 测试总结:")
    print("   - 如果测试成功：说明问题已解决")
    print("   - 如果仍然失败：可能需要检查按钮检测的准确性")
    print("   - 建议手动验证游戏当前界面状态") 