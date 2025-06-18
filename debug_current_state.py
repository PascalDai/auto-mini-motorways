#!/usr/bin/env python3
"""
实时游戏状态调试工具
分析当前游戏画面并显示详细的检测信息
"""

import cv2
import numpy as np
import json
from datetime import datetime
from game_capture import GameCapture
from ui_detector import UIDetector
from image_analyzer import ImageAnalyzer

def main():
    print("🔍 实时游戏状态调试工具")
    print("=" * 50)
    
    try:
        # 初始化组件
        game_capture = GameCapture()
        ui_detector = UIDetector()
        image_analyzer = ImageAnalyzer()
        
        # 查找游戏窗口
        window_info = game_capture.find_game_window()
        if 'error' in window_info:
            print(f"❌ 未找到游戏窗口: {window_info['error']}")
            return False
        
        print("✅ 找到游戏窗口")
        print(f"   位置: ({window_info['x']}, {window_info['y']})")
        print(f"   大小: {window_info['width']}x{window_info['height']}")
        
        # 捕获当前画面
        pil_screenshot = game_capture.capture_screen()
        if pil_screenshot is None:
            print("❌ 截图失败")
            return False
        
        # 转换为OpenCV格式
        screenshot = cv2.cvtColor(np.array(pil_screenshot), cv2.COLOR_RGB2BGR)
        print(f"📸 截图成功，尺寸: {screenshot.shape[1]}x{screenshot.shape[0]}")
        
        # 分析游戏状态
        game_state = image_analyzer.detect_game_state(screenshot)
        print(f"\n🎮 游戏状态分析:")
        print(f"   状态: {game_state['game_state']}")
        print(f"   描述: {game_state['state_description']}")
        
        # 检测UI元素
        detection_result = ui_detector.detect_ui_elements(screenshot)
        
        if 'error' in detection_result:
            print(f"❌ UI检测失败: {detection_result['error']}")
            return False
        
        detected_elements = detection_result.get('detected_elements', {})
        
        print(f"\n🔍 UI元素检测结果:")
        print(f"   检测到的元素类型: {list(detected_elements.keys())}")
        
        # 详细显示每种元素
        for element_type, elements in detected_elements.items():
            print(f"\n   📍 {element_type}:")
            for i, element in enumerate(elements):
                center = element['center']
                confidence = element['confidence']
                bbox = element['bbox']
                print(f"      元素 {i+1}: 中心({center[0]}, {center[1]}), 置信度{confidence:.3f}, 边界框{bbox}")
        
        # 分析主界面布局
        layout_analysis = ui_detector.analyze_main_menu_layout(screenshot)
        
        if 'error' not in layout_analysis:
            layout = layout_analysis['layout_analysis']
            print(f"\n📊 界面布局分析:")
            print(f"   游玩按钮: {'✅' if layout.get('has_play_button') else '❌'}")
            print(f"   城市选择: {'✅' if layout.get('has_city_selection') else '❌'}")
            print(f"   菜单按钮: {'✅' if layout.get('has_menu_button') else '❌'}")
            print(f"   推荐操作: {layout.get('recommended_action', '未知')}")
            
            # 如果有游玩按钮，显示详细信息
            if layout.get('has_play_button'):
                play_info = layout.get('play_button_info', {})
                print(f"   🎯 游玩按钮详情:")
                print(f"      位置: {play_info.get('center', 'N/A')}")
                print(f"      置信度: {play_info.get('confidence', 'N/A'):.3f}")
                print(f"      边界框: {play_info.get('bbox', 'N/A')}")
        
        # 保存调试信息
        debug_info = {
            'timestamp': datetime.now().isoformat(),
            'window_info': window_info,
            'game_state': game_state,
            'ui_detection': detection_result,
            'layout_analysis': layout_analysis
        }
        
        debug_filename = f"../data/debug_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(debug_filename, 'w', encoding='utf-8') as f:
            json.dump(debug_info, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 调试信息已保存: {debug_filename}")
        
        # 创建带标注的调试图像
        debug_image = ui_detector.create_debug_image(screenshot, detection_result)
        debug_image_path = f"../data/debug_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        cv2.imwrite(debug_image_path, debug_image)
        
        print(f"📸 调试图像已保存: {debug_image_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 50)
    if success:
        print("✅ 调试分析完成")
    else:
        print("❌ 调试分析失败") 