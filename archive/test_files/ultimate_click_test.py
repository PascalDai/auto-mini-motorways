#!/usr/bin/env python3
"""
终极点击测试工具 - 尝试多种点击策略
"""

from game_capture_fixed import GameCaptureFixed
from ui_detector import UIDetector
from image_analyzer import ImageAnalyzer
import cv2
import numpy as np
import time
import subprocess

def activate_and_click_multiple_strategies(screen_x, screen_y):
    """尝试多种点击策略"""
    print(f"🎯 尝试多种点击策略在位置 ({screen_x}, {screen_y})")
    
    strategies = [
        ("单次点击", lambda x, y: single_click(x, y)),
        ("双击", lambda x, y: double_click(x, y)),
        ("长按点击", lambda x, y: long_press_click(x, y)),
        ("多次点击", lambda x, y: multiple_clicks(x, y, 3)),
    ]
    
    for strategy_name, strategy_func in strategies:
        print(f"\n📍 尝试策略: {strategy_name}")
        
        # 每次策略前重新激活窗口
        activate_window()
        time.sleep(1)
        
        # 执行策略
        if strategy_func(screen_x, screen_y):
            print(f"   ✅ {strategy_name} 执行成功")
            
            # 等待并检查结果
            time.sleep(2)
            if check_state_change():
                print(f"   🎉 {strategy_name} 生效！")
                return True
            else:
                print(f"   ⚠️ {strategy_name} 未生效")
        else:
            print(f"   ❌ {strategy_name} 执行失败")
    
    return False

def activate_window():
    """激活窗口"""
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
        return True
    except:
        return False

def single_click(x, y):
    """单次点击"""
    try:
        script = f'''
        tell application "System Events"
            click at {{{x}, {y}}}
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except:
        return False

def double_click(x, y):
    """双击"""
    try:
        script = f'''
        tell application "System Events"
            set click_point to {{{x}, {y}}}
            click at click_point
            delay 0.1
            click at click_point
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except:
        return False

def long_press_click(x, y):
    """长按点击"""
    try:
        script = f'''
        tell application "System Events"
            set click_point to {{{x}, {y}}}
            tell (click at click_point)
                delay 0.5
            end tell
        end tell
        '''
        subprocess.run(['osascript', '-e', script], check=True)
        return True
    except:
        return False

def multiple_clicks(x, y, count):
    """多次点击"""
    try:
        for i in range(count):
            script = f'''
            tell application "System Events"
                click at {{{x}, {y}}}
            end tell
            '''
            subprocess.run(['osascript', '-e', script], check=True)
            time.sleep(0.3)
        return True
    except:
        return False

def check_state_change():
    """检查状态变化"""
    try:
        game_capture = GameCaptureFixed()
        image_analyzer = ImageAnalyzer()
        
        screenshot = game_capture.capture_game_window()
        if screenshot:
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            state = image_analyzer.detect_game_state(screenshot_cv)
            return state != "main_menu"
    except:
        pass
    return False

def try_different_button_positions(base_x, base_y):
    """尝试按钮周围的不同位置"""
    print(f"🎯 尝试按钮周围的不同位置")
    
    # 尝试按钮中心及周围的位置
    offsets = [
        (0, 0),      # 中心
        (-10, 0),    # 左
        (10, 0),     # 右
        (0, -10),    # 上
        (0, 10),     # 下
        (-5, -5),    # 左上
        (5, -5),     # 右上
        (-5, 5),     # 左下
        (5, 5),      # 右下
    ]
    
    for i, (dx, dy) in enumerate(offsets):
        click_x = base_x + dx
        click_y = base_y + dy
        
        position_name = ["中心", "左", "右", "上", "下", "左上", "右上", "左下", "右下"][i]
        print(f"\n📍 尝试位置: {position_name} ({click_x}, {click_y})")
        
        # 激活窗口
        activate_window()
        time.sleep(1)
        
        # 点击
        if single_click(click_x, click_y):
            print(f"   ✅ 点击执行成功")
            
            # 检查结果
            time.sleep(2)
            if check_state_change():
                print(f"   🎉 位置 {position_name} 生效！")
                return True
            else:
                print(f"   ⚠️ 位置 {position_name} 未生效")
        else:
            print(f"   ❌ 点击执行失败")
    
    return False

def main():
    print("🚀 终极点击测试工具")
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
        
        # 捕获游戏窗口
        print("\n📸 捕获游戏窗口...")
        screenshot = game_capture.capture_game_window()
        if not screenshot:
            print("❌ 捕获失败")
            return
        
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
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
        
        print(f"   屏幕坐标: ({screen_x}, {screen_y})")
        
        # 询问测试策略
        print(f"\n🤔 选择测试策略:")
        print(f"   1 - 尝试多种点击策略")
        print(f"   2 - 尝试按钮周围不同位置")
        print(f"   3 - 两种策略都尝试")
        
        choice = input("请选择 (1/2/3): ").strip()
        
        success = False
        
        if choice in ['1', '3']:
            print(f"\n🎯 策略1: 尝试多种点击策略")
            success = activate_and_click_multiple_strategies(screen_x, screen_y)
        
        if not success and choice in ['2', '3']:
            print(f"\n🎯 策略2: 尝试按钮周围不同位置")
            success = try_different_button_positions(screen_x, screen_y)
        
        # 最终结果
        print(f"\n" + "=" * 50)
        if success:
            print("🎉 成功！找到了有效的点击方法")
            print("✅ 游戏已响应点击")
        else:
            print("❌ 所有策略都未成功")
            print("💡 可能需要:")
            print("   - 检查游戏是否处于可点击状态")
            print("   - 确认按钮检测是否准确")
            print("   - 手动验证游戏当前界面")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 