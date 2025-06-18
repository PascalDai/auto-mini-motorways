"""
快速自动启动测试
专门测试从主界面自动进入游戏的核心功能
"""

import time
import json
from pathlib import Path
from auto_game_launcher import AutoGameLauncher

def main():
    """主测试函数"""
    print("🎮 Mini Motorways 快速自动启动测试")
    print("=" * 50)
    
    try:
        # 初始化启动器
        print("🔧 初始化自动启动器...")
        launcher = AutoGameLauncher()
        
        # 分析当前状态
        print("📊 分析当前游戏状态...")
        analysis_result = launcher.capture_and_analyze_current_state()
        
        if 'error' in analysis_result:
            print(f"❌ 状态分析失败: {analysis_result['error']}")
            return False
        
        current_state = analysis_result.get('game_state', 'unknown')
        print(f"📍 当前游戏状态: {current_state}")
        
        if current_state != 'main_menu':
            print(f"⚠️ 当前不在主界面（状态: {current_state}），请手动进入主界面后重试")
            return False
        
        # 显示检测到的UI元素
        ui_elements = analysis_result.get('ui_elements', {})
        layout_analysis = ui_elements.get('layout_analysis', {})
        
        print("🎮 检测到的UI元素:")
        print(f"  - 开始游戏按钮: {'✅' if layout_analysis.get('has_play_button') else '❌'}")
        print(f"  - 城市选择区域: {'✅' if layout_analysis.get('has_city_selection') else '❌'}")
        print(f"  - 推荐操作: {layout_analysis.get('recommended_action', '未知')}")
        
        # 如果有城市选择区域，显示详细信息
        if layout_analysis.get('has_city_selection'):
            city_info = layout_analysis.get('city_selection_info', {})
            center = city_info.get('center', (0, 0))
            confidence = city_info.get('confidence', 0)
            print(f"  🏙️ 城市选择区域: 位置 {center}, 置信度 {confidence:.2f}")
        
        # 询问用户是否继续
        response = input("\n🚀 是否继续进行自动启动测试？(y/n): ").lower().strip()
        if response != 'y':
            print("测试已取消")
            return False
        
        print("\n⚠️ 重要提示：")
        print("   - 系统将自动点击游戏界面")
        print("   - 请勿移动鼠标或点击其他地方")
        print("   - 如需紧急停止，请将鼠标移到屏幕角落")
        
        input("按Enter键开始自动启动...")
        
        # 执行自动启动
        print("\n🎯 开始自动启动流程...")
        success = launcher.launch_game_from_main_menu()
        
        if success:
            print("🎉 自动启动成功！")
            
            # 等待并检查最终状态
            print("等待3秒钟检查最终状态...")
            time.sleep(3)
            
            final_analysis = launcher.capture_and_analyze_current_state()
            final_state = final_analysis.get('game_state', 'unknown')
            print(f"📊 最终游戏状态: {final_state}")
            
            if final_state != 'main_menu':
                print("✅ 成功离开主界面，自动启动完成！")
                return True
            else:
                print("⚠️ 仍在主界面，可能需要手动干预")
                return False
        else:
            print("❌ 自动启动失败")
            
            # 获取调试信息
            status_report = launcher.get_status_report()
            print("🔍 调试信息:")
            print(f"  - 当前状态: {status_report.get('current_state', 'unknown')}")
            print(f"  - 游戏控制器就绪: {status_report.get('game_controller_ready', False)}")
            
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 快速自动启动测试成功！")
    else:
        print("❌ 快速自动启动测试失败")
    
    print("📝 详细日志和调试图像可在以下位置查看:")
    print("  - 状态报告: ../data/status_report_*.json")
    print("  - 调试图像: ../data/debug_images/")
    print("  - 截图: ../data/screenshots/") 