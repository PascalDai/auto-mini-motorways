#!/usr/bin/env python3
"""
点击效果监控工具：实时监控游戏状态变化
"""

from game_capture import GameCapture
from game_controller import GameController
from ui_detector import UIDetector
from image_analyzer import ImageAnalyzer
import cv2
import numpy as np
import time

def monitor_game_state(duration=10):
    """监控游戏状态变化"""
    game_capture = GameCapture()
    image_analyzer = ImageAnalyzer()
    
    print(f"🔍 开始监控游戏状态变化（{duration}秒）...")
    
    start_time = time.time()
    last_state = None
    state_changes = []
    
    while time.time() - start_time < duration:
        try:
            # 捕获画面
            pil_screenshot = game_capture.capture_screen()
            if pil_screenshot:
                screenshot = cv2.cvtColor(np.array(pil_screenshot), cv2.COLOR_RGB2BGR)
                current_state = image_analyzer.detect_game_state(screenshot)
                
                current_time = time.time() - start_time
                
                if current_state != last_state:
                    print(f"   [{current_time:.1f}s] 状态变化: {last_state} → {current_state}")
                    state_changes.append((current_time, last_state, current_state))
                    last_state = current_state
                elif last_state is None:
                    print(f"   [{current_time:.1f}s] 初始状态: {current_state}")
                    last_state = current_state
                
            time.sleep(0.5)  # 每0.5秒检查一次
            
        except Exception as e:
            print(f"   监控错误: {e}")
            time.sleep(0.5)
    
    print(f"✅ 监控完成")
    return state_changes

def main():
    print("🎮 点击效果监控工具")
    print("=" * 50)
    
    try:
        # 初始化组件
        game_capture = GameCapture()
        ui_detector = UIDetector()
        game_controller = None
        
        # 查找游戏窗口
        window_info = game_capture.find_game_window()
        if 'error' in window_info:
            print(f"❌ 未找到游戏窗口: {window_info['error']}")
            return
        
        # 设置游戏控制器
        window_bounds = (window_info['x'], window_info['y'], window_info['width'], window_info['height'])
        game_controller = GameController(window_bounds)
        
        print("📊 检查当前游戏状态...")
        
        # 捕获初始状态
        pil_screenshot = game_capture.capture_screen()
        if not pil_screenshot:
            print("❌ 截图失败")
            return
        
        screenshot = cv2.cvtColor(np.array(pil_screenshot), cv2.COLOR_RGB2BGR)
        image_analyzer = ImageAnalyzer()
        initial_state = image_analyzer.detect_game_state(screenshot)
        
        print(f"   当前状态: {initial_state}")
        
        # 检测游玩按钮
        play_button = ui_detector.find_best_play_button(screenshot)
        if not play_button:
            print("❌ 未找到游玩按钮")
            return
        
        print(f"   游玩按钮位置: {play_button['center']}")
        print(f"   置信度: {play_button['confidence']:.3f}")
        
        # 询问是否执行测试
        print(f"\n🤔 是否执行点击测试并监控状态变化？")
        response = input("输入 'y' 开始测试，其他键取消: ").strip().lower()
        
        if response != 'y':
            print("❌ 已取消测试")
            return
        
        print(f"\n🚀 开始测试流程...")
        
        # 第1步：激活窗口
        print("1️⃣ 激活游戏窗口...")
        game_controller.activate_game_window()
        time.sleep(1)
        
        # 第2步：开始监控（后台）
        print("2️⃣ 开始状态监控...")
        
        # 第3步：执行点击
        print("3️⃣ 执行点击...")
        click_success = game_controller.click_ui_element(play_button)
        
        if not click_success:
            print("   ❌ 点击失败")
            return
        
        print("   ✅ 点击已执行")
        
        # 第4步：监控状态变化
        print("4️⃣ 监控状态变化...")
        state_changes = monitor_game_state(duration=8)
        
        # 分析结果
        print(f"\n📊 测试结果分析:")
        print(f"   初始状态: {initial_state}")
        
        if state_changes:
            print(f"   检测到 {len(state_changes)} 次状态变化:")
            for i, (timestamp, old_state, new_state) in enumerate(state_changes, 1):
                print(f"     {i}. [{timestamp:.1f}s] {old_state} → {new_state}")
            
            final_state = state_changes[-1][2]
            if final_state != initial_state:
                print(f"   🎉 成功！游戏状态已从 {initial_state} 变为 {final_state}")
                print(f"   ✅ 点击生效，游戏已响应")
            else:
                print(f"   ⚠️ 状态有变化但最终回到初始状态")
        else:
            print(f"   ❌ 未检测到状态变化")
            print(f"   可能原因：")
            print(f"     - 点击位置不准确")
            print(f"     - 游戏未响应点击")
            print(f"     - 需要更长时间才能看到变化")
        
        # 最终确认
        print(f"\n🔍 最终状态确认...")
        time.sleep(1)
        final_screenshot = game_capture.capture_screen()
        if final_screenshot:
            final_screenshot_cv = cv2.cvtColor(np.array(final_screenshot), cv2.COLOR_RGB2BGR)
            final_state = image_analyzer.detect_game_state(final_screenshot_cv)
            print(f"   最终状态: {final_state}")
            
            if final_state != initial_state:
                print(f"   🎉 确认成功！游戏状态已改变")
            else:
                print(f"   ❌ 游戏状态未改变")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 