#!/usr/bin/env python3
"""
精确的窗口切换和点击位置测试工具
"""

from game_capture import GameCapture
from game_controller import GameController
from ui_detector import UIDetector
import cv2
import numpy as np
import time
import subprocess
import os

def force_activate_game_window():
    """强制激活游戏窗口到前台"""
    print("🔄 强制激活游戏窗口...")
    
    try:
        # 方法1：使用AppleScript强制激活
        script = '''
        tell application "System Events"
            set frontmost of first process whose name is "Mini Motorways" to true
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        print("   ✅ AppleScript激活成功")
        time.sleep(1)
        
        # 方法2：额外确保窗口在前台
        script2 = '''
        tell application "Mini Motorways"
            activate
        end tell
        '''
        subprocess.run(['osascript', '-e', script2], check=True)
        print("   ✅ 应用激活成功")
        time.sleep(1)
        
        return True
        
    except Exception as e:
        print(f"   ⚠️ AppleScript激活失败: {e}")
        return False

def get_precise_click_position(play_button, window_info, screenshot_shape):
    """计算精确的点击位置"""
    print("🎯 计算精确点击位置...")
    
    button_x, button_y = play_button['center']
    
    print(f"   原始按钮位置: ({button_x}, {button_y})")
    print(f"   截图尺寸: {screenshot_shape[1]}x{screenshot_shape[0]}")
    print(f"   游戏窗口: {window_info['width']}x{window_info['height']}")
    
    # 计算缩放比例
    scale_x = window_info['width'] / screenshot_shape[1]
    scale_y = window_info['height'] / screenshot_shape[0]
    
    print(f"   缩放比例: X={scale_x:.3f}, Y={scale_y:.3f}")
    
    # 转换到窗口坐标
    window_x = int(button_x * scale_x)
    window_y = int(button_y * scale_y)
    
    print(f"   窗口内坐标: ({window_x}, {window_y})")
    
    # 转换到屏幕坐标
    screen_x = window_info['x'] + window_x
    screen_y = window_info['y'] + window_y
    
    print(f"   屏幕坐标: ({screen_x}, {screen_y})")
    
    # 验证坐标范围
    if (window_info['x'] <= screen_x <= window_info['x'] + window_info['width'] and
        window_info['y'] <= screen_y <= window_info['y'] + window_info['height']):
        print("   ✅ 坐标在窗口范围内")
    else:
        print("   ❌ 坐标超出窗口范围")
        print(f"   窗口范围: X({window_info['x']}-{window_info['x'] + window_info['width']}), Y({window_info['y']}-{window_info['y'] + window_info['height']})")
    
    return screen_x, screen_y

def execute_precise_click(screen_x, screen_y):
    """执行精确点击"""
    print(f"🖱️ 执行精确点击 ({screen_x}, {screen_y})...")
    
    try:
        # 使用AppleScript执行点击，确保准确性
        script = f'''
        tell application "System Events"
            click at {{{screen_x}, {screen_y}}}
        end tell
        '''
        
        subprocess.run(['osascript', '-e', script], check=True)
        print("   ✅ 点击执行成功")
        return True
        
    except Exception as e:
        print(f"   ❌ 点击执行失败: {e}")
        return False

def main():
    print("🎯 精确窗口切换和点击测试")
    print("=" * 50)
    
    try:
        # 初始化组件
        game_capture = GameCapture()
        ui_detector = UIDetector()
        
        # 查找游戏窗口
        print("🔍 查找游戏窗口...")
        window_info = game_capture.find_game_window()
        if 'error' in window_info:
            print(f"❌ 未找到游戏窗口: {window_info['error']}")
            return
        
        print("✅ 找到游戏窗口")
        print(f"   位置: ({window_info['x']}, {window_info['y']})")
        print(f"   大小: {window_info['width']}x{window_info['height']}")
        
        # 捕获当前画面
        print("\n📸 捕获游戏画面...")
        pil_screenshot = game_capture.capture_screen()
        if pil_screenshot is None:
            print("❌ 截图失败")
            return
        
        screenshot = cv2.cvtColor(np.array(pil_screenshot), cv2.COLOR_RGB2BGR)
        print(f"   截图尺寸: {screenshot.shape[1]}x{screenshot.shape[0]}")
        
        # 检测游玩按钮
        print("\n🎯 检测游玩按钮...")
        play_button = ui_detector.find_best_play_button(screenshot)
        
        if not play_button:
            print("❌ 未找到游玩按钮")
            return
        
        print(f"✅ 找到游玩按钮")
        print(f"   位置: {play_button['center']}")
        print(f"   置信度: {play_button['confidence']:.3f}")
        
        # 计算精确点击位置
        screen_x, screen_y = get_precise_click_position(play_button, window_info, screenshot.shape)
        
        # 在截图上标记按钮位置
        debug_image = screenshot.copy()
        button_x, button_y = play_button['center']
        cv2.circle(debug_image, (int(button_x), int(button_y)), 15, (0, 255, 0), 3)
        cv2.putText(debug_image, f"Click Here ({int(button_x)}, {int(button_y)})", 
                   (int(button_x) + 20, int(button_y) - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # 保存调试图片
        debug_filename = f"../data/precise_click_debug_{int(time.time())}.png"
        cv2.imwrite(debug_filename, debug_image)
        print(f"\n💾 调试图片已保存: {debug_filename}")
        
        # 询问是否执行测试
        print(f"\n🤔 是否执行精确点击测试？")
        print(f"   将会：")
        print(f"   1. 强制激活游戏窗口")
        print(f"   2. 等待窗口完全激活")
        print(f"   3. 在屏幕坐标 ({screen_x}, {screen_y}) 执行点击")
        
        response = input("输入 'y' 执行测试，其他键取消: ").strip().lower()
        
        if response != 'y':
            print("❌ 已取消测试")
            return
        
        print(f"\n🚀 开始精确测试流程...")
        
        # 第1步：强制激活游戏窗口
        print("1️⃣ 强制激活游戏窗口...")
        activation_success = force_activate_game_window()
        
        if not activation_success:
            print("   ⚠️ 窗口激活可能失败，但继续测试")
        
        # 第2步：等待窗口完全激活
        print("2️⃣ 等待窗口完全激活...")
        time.sleep(2)  # 增加等待时间
        
        # 第3步：执行精确点击
        print("3️⃣ 执行精确点击...")
        click_success = execute_precise_click(screen_x, screen_y)
        
        if not click_success:
            print("   ❌ 点击失败")
            return
        
        # 第4步：等待游戏响应
        print("4️⃣ 等待游戏响应...")
        time.sleep(3)
        
        # 第5步：检查结果
        print("5️⃣ 检查游戏状态...")
        new_pil_screenshot = game_capture.capture_screen()
        if new_pil_screenshot:
            from image_analyzer import ImageAnalyzer
            image_analyzer = ImageAnalyzer()
            
            # 检查初始状态
            initial_state = image_analyzer.detect_game_state(screenshot)
            
            # 检查新状态
            new_screenshot = cv2.cvtColor(np.array(new_pil_screenshot), cv2.COLOR_RGB2BGR)
            new_state = image_analyzer.detect_game_state(new_screenshot)
            
            print(f"   点击前状态: {initial_state}")
            print(f"   点击后状态: {new_state}")
            
            if new_state != initial_state:
                print("🎉 成功！游戏状态已改变")
                print("   ✅ 精确点击生效")
            else:
                print("⚠️ 游戏状态未改变")
                print("   可能需要进一步调试")
        
        print(f"\n📋 测试完成")
        print(f"   请观察游戏窗口是否有变化")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 