#!/usr/bin/env python3
"""
窗口激活功能测试
验证窗口激活是否正常工作
"""

from game_capture import GameCapture
from game_controller import GameController
import time

def main():
    print("🔍 窗口激活功能测试")
    print("=" * 50)
    
    try:
        # 初始化游戏捕获器
        game_capture = GameCapture()
        
        # 查找游戏窗口
        window_info = game_capture.find_game_window()
        if 'error' in window_info:
            print(f"❌ 未找到游戏窗口: {window_info['error']}")
            return False
        
        print("✅ 找到游戏窗口")
        print(f"   位置: ({window_info['x']}, {window_info['y']})")
        print(f"   大小: {window_info['width']}x{window_info['height']}")
        
        # 计算游戏窗口的边界
        window_bounds = (
            window_info['x'], 
            window_info['y'], 
            window_info['width'], 
            window_info['height']
        )
        
        # 初始化游戏控制器
        game_controller = GameController(window_bounds)
        
        print("\n🎯 测试窗口激活功能...")
        print("⚠️  请确保游戏窗口当前不在前台")
        input("按Enter键开始测试窗口激活...")
        
        # 测试激活窗口
        success = game_controller.activate_game_window()
        
        if success:
            print("✅ 窗口激活成功！")
            print("💡 请检查游戏窗口是否已经切换到前台")
        else:
            print("❌ 窗口激活失败")
        
        return success
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 50)
    if success:
        print("✅ 窗口激活测试完成")
    else:
        print("❌ 窗口激活测试失败") 