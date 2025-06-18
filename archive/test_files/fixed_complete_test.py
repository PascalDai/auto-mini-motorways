#!/usr/bin/env python3
"""
使用修复版捕获器的完整测试工具
解决多显示器问题，确保检测和点击正确的游戏窗口
"""

from game_capture_fixed import GameCaptureFixed
from game_controller import GameController
from ui_detector import UIDetector
from image_analyzer import ImageAnalyzer
import cv2
import numpy as np
import time
import subprocess

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
        
        return True
        
    except Exception as e:
        print(f"   ⚠️ 窗口激活失败: {e}")
        return False

def precise_click(screen_x, screen_y):
    """精确点击"""
    print(f"🖱️ 精确点击 ({screen_x}, {screen_y})...")
    
    try:
        # 使用AppleScript执行点击
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
    print("🎯 修复版完整测试工具")
    print("=" * 50)
    
    try:
        # 初始化修复版组件
        print("🔧 初始化修复版组件...")
        game_capture = GameCaptureFixed()  # 使用修复版捕获器
        ui_detector = UIDetector()
        image_analyzer = ImageAnalyzer()
        
        # 查找游戏窗口
        print("\n🔍 查找游戏窗口...")
        window_info = game_capture.find_game_window()
        if not window_info or 'error' in window_info:
            print(f"❌ 未找到游戏窗口: {window_info.get('error', '未知错误')}")
            return
        
        print("✅ 找到游戏窗口")
        print(f"   位置: ({window_info['x']}, {window_info['y']})")
        print(f"   大小: {window_info['width']}x{window_info['height']}")
        
        # 设置游戏控制器
        window_bounds = (window_info['x'], window_info['y'], window_info['width'], window_info['height'])
        game_controller = GameController(window_bounds)
        
        # 捕获游戏窗口（不是全屏！）
        print("\n📸 捕获游戏窗口...")
        pil_screenshot = game_capture.capture_game_window()  # 关键：只捕获游戏窗口
        if pil_screenshot is None:
            print("❌ 游戏窗口捕获失败")
            return
        
        screenshot = cv2.cvtColor(np.array(pil_screenshot), cv2.COLOR_RGB2BGR)
        print(f"   捕获成功，尺寸: {screenshot.shape[1]}x{screenshot.shape[0]}")
        
        # 分析游戏状态
        print("\n📊 分析游戏状态...")
        initial_state = image_analyzer.detect_game_state(screenshot)
        print(f"   当前游戏状态: {initial_state}")
        
        # 检测游玩按钮（现在是在正确的游戏窗口截图上）
        print("\n🎯 检测游玩按钮...")
        play_button = ui_detector.find_best_play_button(screenshot)
        
        if not play_button:
            print("❌ 未找到游玩按钮")
            
            # 尝试检测所有UI元素
            detection_result = ui_detector.detect_ui_elements(screenshot)
            detected_elements = detection_result.get('detected_elements', {})
            print(f"   检测到的UI元素: {list(detected_elements.keys())}")
            return
        
        print(f"✅ 找到游玩按钮")
        print(f"   位置: {play_button['center']}")
        print(f"   置信度: {play_button['confidence']:.3f}")
        
        # 计算屏幕坐标（现在基于正确的游戏窗口）
        button_x, button_y = play_button['center']
        
        # 重要：现在screenshot是游戏窗口的截图，所以坐标转换更简单
        # 直接将窗口内坐标转换为屏幕坐标
        screen_x = window_info['x'] + button_x
        screen_y = window_info['y'] + button_y
        
        print(f"\n📐 坐标计算:")
        print(f"   游戏窗口截图尺寸: {screenshot.shape[1]}x{screenshot.shape[0]}")
        print(f"   游戏窗口位置: ({window_info['x']}, {window_info['y']})")
        print(f"   按钮在窗口内位置: ({button_x}, {button_y})")
        print(f"   按钮屏幕坐标: ({screen_x}, {screen_y})")
        
        # 验证坐标合理性
        if (window_info['x'] <= screen_x <= window_info['x'] + window_info['width'] and
            window_info['y'] <= screen_y <= window_info['y'] + window_info['height']):
            print("   ✅ 坐标在游戏窗口范围内")
        else:
            print("   ❌ 坐标超出游戏窗口范围")
            return
        
        # 保存调试图片
        debug_image = screenshot.copy()
        cv2.circle(debug_image, (int(button_x), int(button_y)), 15, (0, 255, 0), 3)
        cv2.putText(debug_image, f"Play Button ({int(button_x)}, {int(button_y)})", 
                   (int(button_x) + 20, int(button_y) - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        debug_filename = f"../data/fixed_debug_{int(time.time())}.png"
        cv2.imwrite(debug_filename, debug_image)
        print(f"\n💾 修复版调试图片已保存: {debug_filename}")
        
        # 询问是否执行测试
        print(f"\n🤔 是否执行修复版点击测试？")
        print(f"   现在检测的是正确的游戏窗口内容")
        print(f"   将点击屏幕坐标: ({screen_x}, {screen_y})")
        
        response = input("输入 'y' 执行测试，其他键取消: ").strip().lower()
        
        if response != 'y':
            print("❌ 已取消测试")
            return
        
        print(f"\n🚀 开始修复版测试流程...")
        
        # 第1步：增强窗口激活
        print("1️⃣ 增强窗口激活...")
        enhanced_window_activation()
        
        # 第2步：精确点击
        print("2️⃣ 执行精确点击...")
        click_success = precise_click(screen_x, screen_y)
        
        if not click_success:
            print("   ❌ 点击失败")
            return
        
        # 第3步：等待游戏响应
        print("3️⃣ 等待游戏响应...")
        time.sleep(3)
        
        # 第4步：检查结果
        print("4️⃣ 检查游戏状态变化...")
        new_pil_screenshot = game_capture.capture_game_window()
        if new_pil_screenshot:
            new_screenshot = cv2.cvtColor(np.array(new_pil_screenshot), cv2.COLOR_RGB2BGR)
            new_state = image_analyzer.detect_game_state(new_screenshot)
            
            print(f"   点击前状态: {initial_state}")
            print(f"   点击后状态: {new_state}")
            
            if new_state != initial_state:
                print("🎉 成功！游戏状态已改变")
                print("   ✅ 修复版点击生效")
                print("   ✅ 多显示器问题已解决")
                
                # 保存成功后的截图
                success_filename = f"../data/success_after_click_{int(time.time())}.png"
                cv2.imwrite(success_filename, new_screenshot)
                print(f"   💾 成功截图已保存: {success_filename}")
                
                return True
            else:
                print("⚠️ 游戏状态未改变")
                print("   可能需要进一步调试按钮检测精度")
                
                # 保存对比图片
                comparison_filename = f"../data/comparison_{int(time.time())}.png"
                comparison = np.hstack([screenshot, new_screenshot])
                cv2.imwrite(comparison_filename, comparison)
                print(f"   💾 对比图片已保存: {comparison_filename}")
                
                return False
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 50)
    if success:
        print("✅ 修复版测试成功完成！")
        print("🎯 多显示器问题已解决")
        print("🎮 游戏自动化系统准备就绪")
    else:
        print("❌ 修复版测试失败")
        print("💡 可能需要进一步调试")
    
    print("\n📋 修复总结:")
    print("   - 使用修复版捕获器只捕获游戏窗口")
    print("   - 避免了多显示器内容混淆")
    print("   - 确保按钮检测在正确的游戏画面上")
    print("   - 简化了坐标转换逻辑") 