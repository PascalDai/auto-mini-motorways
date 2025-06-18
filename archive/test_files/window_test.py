#!/usr/bin/env python3

"""
窗口识别测试脚本

这个脚本专门用于测试Mini Motorways游戏窗口识别功能
帮助调试多屏幕环境下的窗口定位问题
"""

import sys
import logging
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent))

from window_finder import WindowFinder

# 设置日志级别
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("🔍 Mini Motorways - 窗口识别测试")
    print("=" * 60)
    print()
    print("这个程序会帮助你检测Mini Motorways游戏窗口")
    print()
    print("📋 使用步骤:")
    print("1. 确保Mini Motorways游戏已经打开")
    print("2. 游戏窗口不要最小化")
    print("3. 运行此测试程序")
    print()

def test_window_detection():
    """测试窗口检测功能"""
    print("🔍 开始窗口检测测试...")
    print()
    
    # 创建窗口查找器
    finder = WindowFinder()
    
    print("📱 第一步：获取所有窗口信息")
    print("-" * 40)
    
    # 获取所有窗口
    all_windows = finder.get_all_windows()
    
    if not all_windows:
        print("❌ 无法获取窗口信息")
        print("💡 可能的原因:")
        print("   - 权限不足")
        print("   - 系统设置问题")
        return False
    
    print(f"✅ 找到 {len(all_windows)} 个窗口")
    print()
    
    print("🎮 第二步：查找游戏窗口")
    print("-" * 40)
    
    # 查找游戏窗口
    game_window = finder.find_game_window()
    
    if game_window:
        print(f"🎉 成功找到游戏窗口!")
        print(f"   进程名: {game_window['process']}")
        print(f"   窗口标题: '{game_window['title']}'")
        print(f"   位置: ({game_window['x']}, {game_window['y']})")
        print(f"   大小: {game_window['width']} x {game_window['height']}")
        print()
        
        # 验证窗口
        if finder.is_window_valid(game_window):
            print("✅ 窗口信息验证通过")
            
            # 获取捕获区域
            region = finder.get_window_region(game_window)
            print(f"📸 捕获区域: {region}")
            
            return True
        else:
            print("❌ 窗口信息验证失败")
            return False
    else:
        print("❌ 未找到游戏窗口")
        print()
        print("🔧 故障排除建议:")
        print("1. 检查游戏是否真的在运行")
        print("2. 确保游戏窗口没有最小化")
        print("3. 尝试切换到游戏窗口")
        print("4. 检查游戏窗口标题是否包含'Mini Motorways'")
        print()
        
        # 显示可能相关的窗口
        print("🔍 可能相关的窗口:")
        for window in all_windows:
            title = window['title'].lower()
            process = window['process'].lower()
            if ('mini' in title or 'motor' in title or 
                'mini' in process or 'motor' in process or
                'game' in title or 'steam' in title):
                print(f"   - {window['process']}: '{window['title']}'")
        
        return False

def main():
    """主函数"""
    print_welcome()
    
    try:
        success = test_window_detection()
        
        print()
        print("=" * 60)
        if success:
            print("🎉 窗口识别测试成功!")
            print("现在可以运行完整的画面捕获测试了")
            print("运行命令: python3 src/capture_test.py")
        else:
            print("❌ 窗口识别测试失败")
            print("请按照上述建议解决问题后重试")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 