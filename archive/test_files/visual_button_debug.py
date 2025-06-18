#!/usr/bin/env python3
"""
可视化按钮位置调试工具
"""

from game_capture import GameCapture
from ui_detector import UIDetector
import cv2
import numpy as np
import time

def main():
    print("👁️ 可视化按钮位置调试工具")
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
        
        # 检测所有UI元素
        print("\n🎯 检测所有UI元素...")
        detection_result = ui_detector.detect_ui_elements(screenshot)
        detected_elements = detection_result.get('detected_elements', {})
        
        print(f"   检测到的元素类型: {list(detected_elements.keys())}")
        
        # 创建调试图像
        debug_image = screenshot.copy()
        
        # 标记所有检测到的游玩按钮
        if 'play_button' in detected_elements:
            play_buttons = detected_elements['play_button']
            print(f"\n🎮 检测到 {len(play_buttons)} 个游玩按钮候选:")
            
            for i, button in enumerate(play_buttons):
                x, y = button['center']
                confidence = button['confidence']
                
                print(f"   按钮 {i+1}: 位置({x}, {y}), 置信度{confidence:.3f}")
                
                # 用不同颜色标记不同的按钮
                if i == 0:  # 最佳按钮用绿色
                    color = (0, 255, 0)
                    thickness = 4
                elif confidence > 0.7:  # 高置信度用蓝色
                    color = (255, 0, 0)
                    thickness = 3
                else:  # 低置信度用红色
                    color = (0, 0, 255)
                    thickness = 2
                
                # 画圆标记按钮中心
                cv2.circle(debug_image, (int(x), int(y)), 20, color, thickness)
                
                # 添加文字标注
                text = f"Btn{i+1} {confidence:.2f}"
                cv2.putText(debug_image, text, 
                           (int(x) + 25, int(y) - 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                
                # 计算对应的屏幕坐标
                scale_x = window_info['width'] / screenshot.shape[1]
                scale_y = window_info['height'] / screenshot.shape[0]
                
                window_x = int(x * scale_x)
                window_y = int(y * scale_y)
                screen_x = window_info['x'] + window_x
                screen_y = window_info['y'] + window_y
                
                print(f"     → 屏幕坐标: ({screen_x}, {screen_y})")
        else:
            print("❌ 未检测到游玩按钮")
        
        # 添加窗口边界参考线
        # 计算游戏窗口在截图中的边界
        window_left = 0
        window_top = 0
        window_right = screenshot.shape[1]
        window_bottom = screenshot.shape[0]
        
        # 画窗口边界
        cv2.rectangle(debug_image, 
                     (window_left, window_top), 
                     (window_right, window_bottom), 
                     (255, 255, 255), 3)
        
        # 添加标题
        cv2.putText(debug_image, "Button Detection Debug", 
                   (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        # 添加图例
        legend_y = 100
        cv2.putText(debug_image, "Green = Best Button", 
                   (50, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(debug_image, "Blue = High Confidence", 
                   (50, legend_y + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.putText(debug_image, "Red = Low Confidence", 
                   (50, legend_y + 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # 保存调试图片
        debug_filename = f"../data/visual_button_debug_{int(time.time())}.png"
        cv2.imwrite(debug_filename, debug_image)
        print(f"\n💾 可视化调试图片已保存: {debug_filename}")
        
        # 创建缩小版本便于查看
        small_image = cv2.resize(debug_image, (1920, 1080))
        small_filename = f"../data/visual_button_debug_small_{int(time.time())}.png"
        cv2.imwrite(small_filename, small_image)
        print(f"💾 缩小版调试图片已保存: {small_filename}")
        
        print(f"\n📋 调试建议:")
        print(f"   1. 请打开调试图片查看按钮检测位置")
        print(f"   2. 确认绿色圆圈是否标记在正确的游玩按钮上")
        print(f"   3. 如果位置不对，我们需要调整UI检测器配置")
        print(f"   4. 如果位置正确但点击无效，可能是其他问题")
        
        # 显示最佳按钮信息
        best_button = ui_detector.find_best_play_button(screenshot)
        if best_button:
            print(f"\n🎯 最佳按钮详情:")
            print(f"   位置: {best_button['center']}")
            print(f"   置信度: {best_button['confidence']:.3f}")
            
            # 计算屏幕坐标
            x, y = best_button['center']
            scale_x = window_info['width'] / screenshot.shape[1]
            scale_y = window_info['height'] / screenshot.shape[0]
            
            window_x = int(x * scale_x)
            window_y = int(y * scale_y)
            screen_x = window_info['x'] + window_x
            screen_y = window_info['y'] + window_y
            
            print(f"   屏幕坐标: ({screen_x}, {screen_y})")
            
            # 检查位置是否合理
            button_y_percent = y / screenshot.shape[0]
            print(f"   垂直位置: {button_y_percent:.1%} (期望80-95%)")
            
            if button_y_percent < 0.8:
                print("   ⚠️ 按钮位置太靠上，可能检测错误")
            elif button_y_percent > 0.95:
                print("   ⚠️ 按钮位置太靠下，可能检测错误")
            else:
                print("   ✅ 按钮垂直位置合理")
        
    except Exception as e:
        print(f"❌ 调试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 