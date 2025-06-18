#!/usr/bin/env python3
"""
带鼠标移动的点击测试工具 - 先移动鼠标，再点击
"""

from game_capture_fixed import GameCaptureFixed
from ui_detector import UIDetector
from image_analyzer import ImageAnalyzer
import cv2
import numpy as np
import time
import subprocess
import pyautogui

def move_and_click_pyautogui(x, y):
    """使用pyautogui移动鼠标并点击"""
    print(f"🖱️ 使用pyautogui移动鼠标到 ({x}, {y}) 并点击...")
    
    try:
        # 禁用安全检查
        pyautogui.FAILSAFE = False
        
        # 获取当前鼠标位置
        current_x, current_y = pyautogui.position()
        print(f"   当前鼠标位置: ({current_x}, {current_y})")
        
        # 移动鼠标到目标位置
        print(f"   移动鼠标到: ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.5)
        
        # 确认移动后的位置
        new_x, new_y = pyautogui.position()
        print(f"   移动后位置: ({new_x}, {new_y})")
        
        # 短暂等待
        time.sleep(0.5)
        
        # 点击
        print(f"   执行点击...")
        pyautogui.click()
        
        print(f"   ✅ 移动并点击完成")
        return True
        
    except Exception as e:
        print(f"   ❌ pyautogui点击失败: {e}")
        return False

def move_and_click_applescript(x, y):
    """使用AppleScript移动鼠标并点击"""
    print(f"🖱️ 使用AppleScript移动鼠标到 ({x}, {y}) 并点击...")
    
    try:
        # 移动鼠标
        move_script = f'''
        tell application "System Events"
            set mouseLoc to {{{x}, {y}}}
            -- 移动鼠标到指定位置
            do shell script "echo 'Moving mouse to {x}, {y}'"
        end tell
        '''
        
        # 点击
        click_script = f'''
        tell application "System Events"
            click at {{{x}, {y}}}
        end tell
        '''
        
        # 执行移动（虽然AppleScript不能直接移动鼠标，但我们可以组合使用）
        subprocess.run(['osascript', '-e', click_script], check=True)
        
        print(f"   ✅ AppleScript点击完成")
        return True
        
    except Exception as e:
        print(f"   ❌ AppleScript点击失败: {e}")
        return False

def activate_window():
    """激活游戏窗口"""
    print("🔄 激活游戏窗口...")
    
    try:
        script = '''
        tell application "Mini Motorways"
            activate
        end tell
        tell application "System Events"
            set frontmost of first process whose name is "Mini Motorways" to true
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        print("   ✅ 窗口激活成功")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"   ⚠️ 窗口激活失败: {e}")
        return False

def check_state_change():
    """检查游戏状态变化"""
    try:
        game_capture = GameCaptureFixed()
        image_analyzer = ImageAnalyzer()
        
        screenshot = game_capture.capture_game_window()
        if screenshot:
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            state = image_analyzer.detect_game_state(screenshot_cv)
            print(f"   当前游戏状态: {state}")
            return state != "main_menu"
    except Exception as e:
        print(f"   状态检查失败: {e}")
    return False

def main():
    print("🖱️ 鼠标移动点击测试工具")
    print("=" * 50)
    
    try:
        # 初始化组件
        print("🔧 初始化组件...")
        game_capture = GameCaptureFixed()
        ui_detector = UIDetector()
        image_analyzer = ImageAnalyzer()
        
        # 查找游戏窗口
        print("\n🔍 查找游戏窗口...")
        window_info = game_capture.find_game_window()
        if not window_info or 'error' in window_info:
            print(f"❌ 未找到游戏窗口")
            return
        
        print("✅ 找到游戏窗口")
        print(f"   位置: ({window_info['x']}, {window_info['y']})")
        print(f"   大小: {window_info['width']}x{window_info['height']}")
        
        # 捕获游戏窗口
        print("\n📸 捕获游戏窗口...")
        screenshot = game_capture.capture_game_window()
        if not screenshot:
            print("❌ 捕获失败")
            return
        
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        print(f"   捕获成功，尺寸: {screenshot_cv.shape[1]}x{screenshot_cv.shape[0]}")
        
        # 分析初始状态
        initial_state = image_analyzer.detect_game_state(screenshot_cv)
        print(f"   初始游戏状态: {initial_state}")
        
        # 检测游玩按钮
        print("\n🎯 检测游玩按钮...")
        play_button = ui_detector.find_best_play_button(screenshot_cv)
        
        if not play_button:
            print("❌ 未找到游玩按钮")
            return
        
        print(f"✅ 找到游玩按钮")
        print(f"   位置: {play_button['center']}")
        print(f"   置信度: {play_button['confidence']:.3f}")
        
        # 计算屏幕坐标
        button_x, button_y = play_button['center']
        screen_x = window_info['x'] + button_x
        screen_y = window_info['y'] + button_y
        
        print(f"\n📐 坐标计算:")
        print(f"   按钮在窗口内位置: ({button_x}, {button_y})")
        print(f"   按钮屏幕坐标: ({screen_x}, {screen_y})")
        
        # 获取当前鼠标位置
        current_mouse_x, current_mouse_y = pyautogui.position()
        print(f"   当前鼠标位置: ({current_mouse_x}, {current_mouse_y})")
        
        # 保存调试图片
        debug_image = screenshot_cv.copy()
        cv2.circle(debug_image, (int(button_x), int(button_y)), 15, (0, 255, 0), 3)
        cv2.putText(debug_image, f"Target ({int(button_x)}, {int(button_y)})", 
                   (int(button_x) + 20, int(button_y) - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        debug_filename = f"../data/mouse_move_debug_{int(time.time())}.png"
        cv2.imwrite(debug_filename, debug_image)
        print(f"\n💾 调试图片已保存: {debug_filename}")
        
        # 询问测试方法
        print(f"\n🤔 选择点击方法:")
        print(f"   1 - 使用pyautogui (推荐)")
        print(f"   2 - 使用AppleScript")
        print(f"   3 - 两种方法都尝试")
        
        choice = input("请选择 (1/2/3): ").strip()
        
        success = False
        
        if choice in ['1', '3']:
            print(f"\n🎯 方法1: 使用pyautogui移动鼠标并点击")
            
            # 激活窗口
            activate_window()
            
            # 使用pyautogui移动并点击
            if move_and_click_pyautogui(screen_x, screen_y):
                print("✅ pyautogui点击完成")
                
                # 等待游戏响应
                print("⏳ 等待游戏响应...")
                time.sleep(3)
                
                # 检查状态变化
                if check_state_change():
                    print("🎉 成功！游戏状态已改变")
                    success = True
                else:
                    print("⚠️ 游戏状态未改变")
        
        if not success and choice in ['2', '3']:
            print(f"\n🎯 方法2: 使用AppleScript点击")
            
            # 激活窗口
            activate_window()
            
            # 使用AppleScript点击
            if move_and_click_applescript(screen_x, screen_y):
                print("✅ AppleScript点击完成")
                
                # 等待游戏响应
                print("⏳ 等待游戏响应...")
                time.sleep(3)
                
                # 检查状态变化
                if check_state_change():
                    print("🎉 成功！游戏状态已改变")
                    success = True
                else:
                    print("⚠️ 游戏状态未改变")
        
        # 最终结果
        print(f"\n" + "=" * 50)
        if success:
            print("🎉 成功！鼠标移动点击生效")
            print("✅ 游戏已响应点击")
            print("🎯 问题已解决：需要先移动鼠标再点击")
        else:
            print("❌ 鼠标移动点击仍未成功")
            print("💡 可能的原因:")
            print("   - 按钮检测位置仍不准确")
            print("   - 游戏处于特殊状态")
            print("   - 需要手动验证游戏界面")
        
        # 最终状态确认
        print(f"\n🔍 最终状态确认:")
        final_screenshot = game_capture.capture_game_window()
        if final_screenshot:
            final_screenshot_cv = cv2.cvtColor(np.array(final_screenshot), cv2.COLOR_RGB2BGR)
            final_state = image_analyzer.detect_game_state(final_screenshot_cv)
            print(f"   最终状态: {final_state}")
            
            if final_state != initial_state:
                print("   🎉 确认：游戏状态已改变")
            else:
                print("   ❌ 确认：游戏状态未改变")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 