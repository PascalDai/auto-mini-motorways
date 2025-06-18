#!/usr/bin/env python3
"""
多屏幕环境优化的点击测试工具
"""

from game_capture import GameCapture
from game_controller import GameController
from ui_detector import UIDetector
from image_analyzer import ImageAnalyzer
import cv2
import numpy as np
import time
import subprocess

def get_screen_info():
    """获取屏幕信息"""
    try:
        # 使用AppleScript获取屏幕信息
        script = '''
        tell application "System Events"
            set screenCount to count of desktops
            set screenInfo to {}
            repeat with i from 1 to screenCount
                set screenBounds to bounds of desktop i
                set end of screenInfo to screenBounds
            end repeat
            return screenInfo
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True, check=True)
        print(f"📺 屏幕信息: {result.stdout.strip()}")
        return result.stdout.strip()
    except Exception as e:
        print(f"⚠️ 无法获取屏幕信息: {e}")
        return None

def enhanced_window_activation():
    """增强的窗口激活"""
    print("🔄 增强窗口激活...")
    
    try:
        # 第1步：确保应用在前台
        script1 = '''
        tell application "Mini Motorways"
            activate
        end tell
        '''
        subprocess.run(['osascript', '-e', script1], check=True)
        print("   ✅ 应用激活")
        time.sleep(1)
        
        # 第2步：确保进程在前台
        script2 = '''
        tell application "System Events"
            set frontmost of first process whose name is "Mini Motorways" to true
        end tell
        '''
        subprocess.run(['osascript', '-e', script2], check=True)
        print("   ✅ 进程前台化")
        time.sleep(1)
        
        # 第3步：点击窗口确保激活
        script3 = '''
        tell application "System Events"
            tell process "Mini Motorways"
                click window 1
            end tell
        end tell
        '''
        subprocess.run(['osascript', '-e', script3], check=True)
        print("   ✅ 窗口点击激活")
        time.sleep(1)
        
        return True
        
    except Exception as e:
        print(f"   ⚠️ 窗口激活失败: {e}")
        return False

def precise_click_with_retry(screen_x, screen_y, retries=3):
    """精确点击，支持重试"""
    print(f"🖱️ 精确点击 ({screen_x}, {screen_y})，最多重试{retries}次...")
    
    for attempt in range(retries):
        try:
            print(f"   尝试 {attempt + 1}/{retries}...")
            
            # 使用AppleScript执行点击
            script = f'''
            tell application "System Events"
                click at {{{screen_x}, {screen_y}}}
            end tell
            '''
            
            subprocess.run(['osascript', '-e', script], check=True)
            print(f"   ✅ 点击执行成功")
            
            # 每次点击后短暂等待
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"   ❌ 第{attempt + 1}次点击失败: {e}")
            if attempt < retries - 1:
                time.sleep(1)  # 重试前等待
    
    return False

def monitor_state_change(game_capture, image_analyzer, duration=10):
    """监控游戏状态变化"""
    print(f"👁️ 监控游戏状态变化 ({duration}秒)...")
    
    start_time = time.time()
    states = []
    
    while time.time() - start_time < duration:
        try:
            pil_screenshot = game_capture.capture_screen()
            if pil_screenshot:
                screenshot = cv2.cvtColor(np.array(pil_screenshot), cv2.COLOR_RGB2BGR)
                current_state = image_analyzer.detect_game_state(screenshot)
                
                elapsed = time.time() - start_time
                states.append((elapsed, current_state))
                
                if len(states) >= 2 and states[-1][1] != states[-2][1]:
                    print(f"   [{elapsed:.1f}s] 状态变化: {states[-2][1]} → {current_state}")
                elif len(states) == 1:
                    print(f"   [{elapsed:.1f}s] 初始状态: {current_state}")
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   监控错误: {e}")
            time.sleep(0.5)
    
    return states

def main():
    print("🖥️ 多屏幕环境点击测试")
    print("=" * 50)
    
    try:
        # 获取屏幕信息
        screen_info = get_screen_info()
        
        # 初始化组件
        print("\n🔧 初始化组件...")
        game_capture = GameCapture()
        ui_detector = UIDetector()
        image_analyzer = ImageAnalyzer()
        
        # 查找游戏窗口
        print("🔍 查找游戏窗口...")
        window_info = game_capture.find_game_window()
        if 'error' in window_info:
            print(f"❌ 未找到游戏窗口: {window_info['error']}")
            return
        
        print("✅ 找到游戏窗口")
        print(f"   位置: ({window_info['x']}, {window_info['y']})")
        print(f"   大小: {window_info['width']}x{window_info['height']}")
        
        # 捕获初始画面
        print("\n📸 捕获游戏画面...")
        pil_screenshot = game_capture.capture_screen()
        if pil_screenshot is None:
            print("❌ 截图失败")
            return
        
        screenshot = cv2.cvtColor(np.array(pil_screenshot), cv2.COLOR_RGB2BGR)
        initial_state = image_analyzer.detect_game_state(screenshot)
        print(f"   当前游戏状态: {initial_state}")
        
        # 检测游玩按钮
        print("\n🎯 检测游玩按钮...")
        play_button = ui_detector.find_best_play_button(screenshot)
        
        if not play_button:
            print("❌ 未找到游玩按钮")
            return
        
        print(f"✅ 找到游玩按钮")
        print(f"   位置: {play_button['center']}")
        print(f"   置信度: {play_button['confidence']:.3f}")
        
        # 计算屏幕坐标
        button_x, button_y = play_button['center']
        scale_x = window_info['width'] / screenshot.shape[1]
        scale_y = window_info['height'] / screenshot.shape[0]
        
        window_x = int(button_x * scale_x)
        window_y = int(button_y * scale_y)
        screen_x = window_info['x'] + window_x
        screen_y = window_info['y'] + window_y
        
        print(f"\n📐 坐标计算:")
        print(f"   截图尺寸: {screenshot.shape[1]}x{screenshot.shape[0]}")
        print(f"   缩放比例: {scale_x:.3f}x{scale_y:.3f}")
        print(f"   窗口内坐标: ({window_x}, {window_y})")
        print(f"   屏幕坐标: ({screen_x}, {screen_y})")
        
        # 多屏幕环境说明
        print(f"\n🖥️ 多屏幕环境说明:")
        print(f"   负数坐标在多屏幕环境中是正常的")
        print(f"   游戏窗口在第二个显示器: Y={window_info['y']}")
        
        # 询问是否执行测试
        print(f"\n🤔 是否执行多屏幕优化点击测试？")
        response = input("输入 'y' 执行测试，其他键取消: ").strip().lower()
        
        if response != 'y':
            print("❌ 已取消测试")
            return
        
        print(f"\n🚀 开始多屏幕优化测试...")
        
        # 第1步：增强窗口激活
        print("1️⃣ 增强窗口激活...")
        activation_success = enhanced_window_activation()
        
        # 第2步：精确点击（支持重试）
        print("2️⃣ 执行精确点击...")
        click_success = precise_click_with_retry(screen_x, screen_y, retries=3)
        
        if not click_success:
            print("   ❌ 所有点击尝试都失败了")
            return
        
        # 第3步：监控状态变化
        print("3️⃣ 监控游戏状态变化...")
        states = monitor_state_change(game_capture, image_analyzer, duration=8)
        
        # 分析结果
        print(f"\n📊 测试结果分析:")
        print(f"   初始状态: {initial_state}")
        
        if len(states) > 1:
            final_state = states[-1][1]
            print(f"   最终状态: {final_state}")
            
            # 检查是否有状态变化
            state_changes = []
            for i in range(1, len(states)):
                if states[i][1] != states[i-1][1]:
                    state_changes.append((states[i][0], states[i-1][1], states[i][1]))
            
            if state_changes:
                print(f"   检测到 {len(state_changes)} 次状态变化:")
                for timestamp, old_state, new_state in state_changes:
                    print(f"     [{timestamp:.1f}s] {old_state} → {new_state}")
                
                if final_state != initial_state:
                    print("   🎉 成功！游戏状态已改变")
                    print("   ✅ 多屏幕环境点击生效")
                else:
                    print("   ⚠️ 有变化但最终回到初始状态")
            else:
                print("   ❌ 未检测到状态变化")
        
        # 最终确认
        time.sleep(2)
        final_screenshot = game_capture.capture_screen()
        if final_screenshot:
            final_screenshot_cv = cv2.cvtColor(np.array(final_screenshot), cv2.COLOR_RGB2BGR)
            final_state = image_analyzer.detect_game_state(final_screenshot_cv)
            
            print(f"\n🔍 最终确认:")
            print(f"   最终状态: {final_state}")
            
            if final_state != initial_state:
                print("   🎉 确认成功！游戏状态已改变")
            else:
                print("   ❌ 游戏状态未改变")
                print("   💡 可能需要检查按钮检测精度")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 