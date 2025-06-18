"""
自动启动测试脚本
用于测试从主界面自动选择关卡并开始游戏的功能
"""

import logging
import time
import json
from pathlib import Path

from auto_game_launcher import AutoGameLauncher

# 配置日志
Path("../logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/auto_launch_test.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def test_ui_detection():
    """测试UI元素检测"""
    print("\n=== 测试UI元素检测 ===")
    
    try:
        launcher = AutoGameLauncher()
        
        # 分析当前状态
        print("正在分析当前游戏状态...")
        analysis_result = launcher.capture_and_analyze_current_state()
        
        if 'error' in analysis_result:
            print(f"❌ 状态分析失败: {analysis_result['error']}")
            return False
        
        game_state = analysis_result.get('game_state', 'unknown')
        print(f"📊 当前游戏状态: {game_state}")
        
        if game_state == 'main_menu':
            ui_elements = analysis_result.get('ui_elements', {})
            layout_analysis = ui_elements.get('layout_analysis', {})
            
            print(f"🎮 检测到的UI元素:")
            print(f"  - 开始游戏按钮: {'✅' if layout_analysis.get('has_play_button') else '❌'}")
            print(f"  - 城市选择区域: {'✅' if layout_analysis.get('has_city_selection') else '❌'}")
            print(f"  - 菜单按钮: {'✅' if layout_analysis.get('has_menu_button') else '❌'}")
            print(f"  - 推荐操作: {layout_analysis.get('recommended_action', '未知')}")
            print(f"  - 交互元素总数: {layout_analysis.get('total_interactive_elements', 0)}")
            
            # 显示具体元素信息
            if layout_analysis.get('has_play_button'):
                play_info = layout_analysis.get('play_button_info', {})
                center = play_info.get('center', (0, 0))
                confidence = play_info.get('confidence', 0)
                print(f"  📍 开始游戏按钮位置: {center}, 置信度: {confidence:.2f}")
            
            if layout_analysis.get('has_city_selection'):
                city_info = layout_analysis.get('city_selection_info', {})
                center = city_info.get('center', (0, 0))
                area = city_info.get('area', 0)
                print(f"  🏙️ 城市选择区域位置: {center}, 面积: {area}")
        
        else:
            print(f"⚠️ 当前不在主界面，无法测试UI检测")
        
        return True
        
    except Exception as e:
        print(f"❌ UI检测测试失败: {e}")
        return False

def test_wait_for_main_menu():
    """测试等待主界面功能"""
    print("\n=== 测试等待主界面功能 ===")
    
    try:
        launcher = AutoGameLauncher()
        
        print("正在等待游戏进入主界面...")
        print("提示：请确保Mini Motorways游戏已启动并可见")
        
        # 等待主界面，较短的超时时间用于测试
        success = launcher.wait_for_main_menu(timeout=10, check_interval=1.0)
        
        if success:
            print("✅ 成功检测到主界面")
            return True
        else:
            print("❌ 未能检测到主界面")
            return False
            
    except Exception as e:
        print(f"❌ 等待主界面测试失败: {e}")
        return False

def test_auto_launch():
    """测试完整的自动启动流程"""
    print("\n=== 测试完整的自动启动流程 ===")
    
    try:
        launcher = AutoGameLauncher()
        
        print("🚀 开始自动游戏启动测试")
        print("⚠️ 重要提示：")
        print("   1. 请确保Mini Motorways游戏已启动")
        print("   2. 游戏窗口可见且未被其他窗口遮挡")
        print("   3. 如需紧急停止，请将鼠标移到屏幕角落")
        
        # 询问用户确认
        response = input("\n是否继续进行自动启动测试？(y/n): ").lower().strip()
        if response != 'y':
            print("测试已取消")
            return False
        
        print("\n开始自动启动流程...")
        
        # 运行自动启动周期
        success = launcher.run_auto_launch_cycle(max_attempts=2)
        
        if success:
            print("🎉 自动启动成功！游戏应该已经开始")
            
            # 等待一段时间让用户观察结果
            print("等待5秒钟让您观察结果...")
            time.sleep(5)
            
            # 获取最终状态报告
            status_report = launcher.get_status_report()
            final_state = status_report.get('current_state', 'unknown')
            print(f"📊 最终游戏状态: {final_state}")
            
            return True
        else:
            print("❌ 自动启动失败")
            
            # 获取状态报告用于调试
            status_report = launcher.get_status_report()
            print("🔍 调试信息:")
            print(f"  - 当前状态: {status_report.get('current_state', 'unknown')}")
            print(f"  - 游戏控制器就绪: {status_report.get('game_controller_ready', False)}")
            print(f"  - 窗口检测: {status_report.get('window_detected', False)}")
            
            return False
            
    except Exception as e:
        print(f"❌ 自动启动测试失败: {e}")
        return False

def test_status_report():
    """测试状态报告功能"""
    print("\n=== 测试状态报告功能 ===")
    
    try:
        launcher = AutoGameLauncher()
        
        print("正在生成状态报告...")
        status_report = launcher.get_status_report()
        
        if 'error' in status_report:
            print(f"❌ 状态报告生成失败: {status_report['error']}")
            return False
        
        print("📋 当前系统状态:")
        print(f"  - 时间戳: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(status_report.get('timestamp', 0)))}")
        print(f"  - 当前游戏状态: {status_report.get('current_state', 'unknown')}")
        print(f"  - 启动尝试次数: {status_report.get('launch_attempts', 0)}")
        print(f"  - 游戏控制器就绪: {'✅' if status_report.get('game_controller_ready') else '❌'}")
        print(f"  - 窗口检测: {'✅' if status_report.get('window_detected') else '❌'}")
        
        # 保存详细报告到文件
        report_path = Path("../data") / f"status_report_{int(time.time())}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(status_report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📄 详细报告已保存到: {report_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 状态报告测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎮 Mini Motorways 自动启动测试")
    print("=" * 50)
    
    # 确保日志目录存在
    Path("../logs").mkdir(exist_ok=True)
    Path("../data").mkdir(exist_ok=True)
    
    # 运行测试
    tests = [
        ("状态报告功能", test_status_report),
        ("UI元素检测", test_ui_detection),
        ("等待主界面功能", test_wait_for_main_menu),
        ("完整自动启动流程", test_auto_launch),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
                
        except KeyboardInterrupt:
            print(f"\n⚠️ 用户中断了 {test_name} 测试")
            break
        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")
            results.append((test_name, False))
    
    # 显示测试总结
    print(f"\n{'='*20} 测试总结 {'='*20}")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  - {test_name}: {status}")
    
    if passed == total:
        print("\n🎉 所有测试通过！自动启动系统工作正常")
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败，请检查日志文件获取详细信息")
    
    print(f"\n📝 详细日志文件: ../logs/auto_launch_test.log")

if __name__ == "__main__":
    main() 