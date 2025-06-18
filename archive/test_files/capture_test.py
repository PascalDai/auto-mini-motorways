#!/usr/bin/env python3
"""
Mini Motorways 画面捕获测试脚本

这个脚本用于测试游戏画面捕获功能
运行前请确保：
1. Mini Motorways游戏已经打开
2. 已经授权屏幕录制权限
"""

import sys
import time
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent))

from game_capture import GameCapture
from config import SCREENSHOTS_DIR

def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("🎮 Mini Motorways AI - 画面捕获测试")
    print("=" * 60)
    print()
    print("这个程序会测试游戏画面捕获功能")
    print()
    print("📋 使用步骤:")
    print("1. 确保Mini Motorways游戏已经打开")
    print("2. 首次运行时，系统会要求授权屏幕录制权限")
    print("3. 程序会每2秒捕获一次游戏画面")
    print("4. 按 Ctrl+C 可以随时停止程序")
    print()
    print(f"💾 截图保存位置: {SCREENSHOTS_DIR}")
    print()

def check_permissions():
    """检查权限"""
    print("🔍 检查系统权限...")
    
    try:
        # 尝试捕获一张测试截图
        capture = GameCapture()
        screenshot = capture.capture_screen()
        
        if screenshot:
            print("✅ 屏幕捕获权限正常")
            return True
        else:
            print("❌ 屏幕捕获失败")
            return False
            
    except Exception as e:
        print(f"❌ 权限检查失败: {e}")
        print()
        print("💡 解决方案:")
        print("1. 打开 系统偏好设置 > 安全性与隐私 > 隐私")
        print("2. 选择 '屏幕录制'")
        print("3. 添加并勾选 Terminal 或者你的Python解释器")
        print("4. 重新运行程序")
        return False

def run_capture_test():
    """运行捕获测试"""
    print("🎯 开始捕获测试...")
    print()
    
    # 创建捕获器
    capture = GameCapture()
    
    # 显示屏幕信息
    screen_info = capture.get_screen_info()
    print(f"📱 屏幕尺寸: {screen_info.get('screen_width', 'Unknown')} x {screen_info.get('screen_height', 'Unknown')}")
    
    # 查找游戏窗口
    print("🔍 查找Mini Motorways游戏窗口...")
    window_info = capture.find_game_window()
    
    if window_info:
        print("✅ 找到游戏窗口")
    else:
        print("⚠️  未找到游戏窗口，将捕获全屏")
        print("   请确保Mini Motorways游戏已经打开")
    
    print()
    print("📸 开始连续捕获...")
    print("   - 每2秒捕获一次")
    print("   - 最多捕获10张截图")
    print("   - 按 Ctrl+C 可以提前停止")
    print()
    
    # 开始捕获（限制为10张截图用于测试）
    try:
        start_time = time.time()
        capture_count = 0
        max_captures = 10
        
        while capture_count < max_captures:
            print(f"📸 正在捕获第 {capture_count + 1}/{max_captures} 张截图...")
            
            if capture.capture_and_save():
                capture_count += 1
                print(f"✅ 捕获成功")
            else:
                print(f"❌ 捕获失败")
            
            if capture_count < max_captures:
                print("⏳ 等待2秒...")
                time.sleep(2)
        
        elapsed_time = time.time() - start_time
        print()
        print("🎉 捕获测试完成!")
        print(f"📊 统计信息:")
        print(f"   - 总捕获数量: {capture_count}")
        print(f"   - 总用时: {elapsed_time:.1f} 秒")
        print(f"   - 截图保存位置: {SCREENSHOTS_DIR}")
        
    except KeyboardInterrupt:
        print()
        print("⏹️  用户中断测试")
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")

def main():
    """主函数"""
    print_welcome()
    
    # 检查权限
    if not check_permissions():
        print()
        print("❌ 权限检查失败，请解决权限问题后重新运行")
        return
    
    print()
    input("✋ 请确保Mini Motorways游戏已经打开，然后按回车键开始测试...")
    print()
    
    # 运行测试
    run_capture_test()
    
    print()
    print("🔍 测试结果检查:")
    print(f"请查看 {SCREENSHOTS_DIR} 目录中的截图文件")
    print("如果截图正确显示了游戏画面，说明捕获功能正常工作")
    print()
    print("📋 下一步:")
    print("如果测试成功，我们将继续开发图像识别功能")
    print("如果测试失败，请检查游戏是否正在运行，或者联系开发者")

if __name__ == "__main__":
    main() 