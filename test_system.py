#!/usr/bin/env python3
"""
Mini Motorways 自动化系统测试脚本
用于验证各个组件的功能是否正常
"""

import sys
import time
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.logger import get_logger, reset_logger
from src.utils.config import get_config
from src.core.window_manager import WindowManager
from src.core.screenshot import ScreenshotManager


def test_config_system():
    """测试配置系统"""
    print("🧪 测试配置系统...")
    
    config = get_config()
    
    # 测试基本配置读取
    window_title = config.get('game.window_title')
    assert window_title == 'Mini Motorways', f"配置读取失败: {window_title}"
    
    # 测试默认值
    non_existent = config.get('non.existent.key', 'default_value')
    assert non_existent == 'default_value', "默认值处理失败"
    
    # 测试配置设置
    config.set('test.key', 'test_value')
    assert config.get('test.key') == 'test_value', "配置设置失败"
    
    print("✅ 配置系统测试通过")
    return True


def test_logger_system():
    """测试日志系统"""
    print("🧪 测试日志系统...")
    
    logger = reset_logger("logs/test_log.md")
    
    # 测试各种日志类型
    logger.add_section("测试章节")
    logger.add_success("测试成功信息")
    logger.add_error("测试错误信息")
    logger.add_warning("测试警告信息")
    logger.add_info("测试信息")
    
    # 测试操作记录
    logger.add_action("测试操作", {"坐标": "(100, 200)", "类型": "点击"})
    
    # 测试识别结果
    test_elements = [
        {"name": "测试元素", "coordinates": (100, 100), "confidence": 0.95}
    ]
    logger.add_recognition_result("测试阶段", test_elements, 0.9)
    
    # 检查日志文件是否创建
    log_file = Path("logs/test_log.md")
    assert log_file.exists(), "日志文件创建失败"
    
    # 检查日志内容
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "测试章节" in content, "日志内容写入失败"
        assert "✅" in content, "成功标记写入失败"
        assert "❌" in content, "错误标记写入失败"
    
    print("✅ 日志系统测试通过")
    return True


def test_window_manager():
    """测试窗口管理器"""
    print("🧪 测试窗口管理器...")
    
    window_manager = WindowManager()
    
    # 测试窗口列表功能
    all_windows = window_manager.list_all_windows()
    assert isinstance(all_windows, list), "窗口列表获取失败"
    print(f"   当前系统窗口数量: {len(all_windows)}")
    
    # 尝试查找游戏窗口（可能失败，这是正常的）
    found = window_manager.find_game_window(max_attempts=2, wait_interval=0.5)
    if found:
        print("   ✅ 找到游戏窗口")
        
        # 测试窗口信息获取
        region = window_manager.get_window_region()
        assert region is not None, "窗口区域获取失败"
        print(f"   窗口区域: {region}")
        
        center = window_manager.get_window_center()
        assert center is not None, "窗口中心获取失败"
        print(f"   窗口中心: {center}")
        
        # 测试窗口有效性
        assert window_manager.is_window_valid(), "窗口有效性检查失败"
        
    else:
        print("   ⚠️ 未找到游戏窗口（这是正常的，如果游戏未运行）")
    
    print("✅ 窗口管理器测试通过")
    return True


def test_screenshot_manager():
    """测试截图管理器"""
    print("🧪 测试截图管理器...")
    
    screenshot_manager = ScreenshotManager()
    
    # 测试截图目录创建
    assert screenshot_manager.current_session_dir.exists(), "截图目录创建失败"
    print(f"   截图目录: {screenshot_manager.current_session_dir}")
    
    # 测试全屏截图
    screenshot_path = screenshot_manager.take_screenshot(description="测试截图")
    if screenshot_path:
        assert Path(screenshot_path).exists(), "截图文件创建失败"
        print(f"   ✅ 截图成功: {Path(screenshot_path).name}")
        
        # 测试标记截图
        test_elements = [
            {
                'name': '测试标记',
                'coordinates': (100, 100),
                'confidence': 0.9,
                'type': 'success'
            }
        ]
        
        marked_path = screenshot_manager.create_marked_screenshot(
            screenshot_path, test_elements, "测试标记截图"
        )
        
        if marked_path:
            assert Path(marked_path).exists(), "标记截图创建失败"
            print(f"   ✅ 标记截图成功: {Path(marked_path).name}")
        
        # 测试统计信息
        stats = screenshot_manager.get_screenshot_stats()
        assert isinstance(stats, dict), "统计信息获取失败"
        assert stats['current_session_count'] > 0, "截图计数错误"
        print(f"   截图统计: {stats}")
        
    else:
        print("   ❌ 截图失败")
        return False
    
    print("✅ 截图管理器测试通过")
    return True


def run_integration_test():
    """运行集成测试"""
    print("🧪 运行集成测试...")
    
    logger = reset_logger("logs/integration_test.md")
    logger.add_section("集成测试开始", level=1)
    
    # 创建所有管理器
    window_manager = WindowManager()
    screenshot_manager = ScreenshotManager()
    
    # 模拟完整的工作流程
    logger.add_section("模拟工作流程")
    
    # 1. 查找窗口
    logger.add_info("步骤1: 查找游戏窗口")
    window_found = window_manager.find_game_window(max_attempts=3)
    
    if window_found:
        logger.add_success("游戏窗口找到")
        
        # 2. 截图
        logger.add_info("步骤2: 截取游戏画面")
        region = window_manager.get_window_screenshot_region()
        screenshot_path = screenshot_manager.take_screenshot(region, "集成测试截图")
        
        if screenshot_path:
            logger.add_success("截图成功")
            logger.add_image("游戏截图", screenshot_path)
            
            # 3. 模拟识别结果
            logger.add_info("步骤3: 模拟游戏状态识别")
            mock_elements = [
                {
                    'name': '开始按钮',
                    'coordinates': (960, 540),
                    'confidence': 0.95,
                    'type': 'success'
                },
                {
                    'name': '设置按钮',
                    'coordinates': (1800, 100),
                    'confidence': 0.88,
                    'type': 'info'
                }
            ]
            
            logger.add_recognition_result("主菜单", mock_elements, 0.92)
            
            # 4. 创建标记截图
            marked_path = screenshot_manager.create_marked_screenshot(
                screenshot_path, mock_elements, "识别结果标记"
            )
            
            if marked_path:
                logger.add_success("标记截图创建成功")
                logger.add_image("标记截图", marked_path)
            
            # 5. 模拟操作决策
            logger.add_info("步骤4: 模拟操作决策")
            logger.add_action("点击开始按钮", {
                "坐标": "(960, 540)",
                "延迟": "0.1秒",
                "类型": "鼠标点击"
            })
            
            logger.add_success("集成测试完成")
            
        else:
            logger.add_error("截图失败")
            return False
    else:
        logger.add_warning("未找到游戏窗口，使用全屏截图进行测试")
        
        # 使用全屏截图继续测试
        screenshot_path = screenshot_manager.take_screenshot(None, "全屏测试截图")
        if screenshot_path:
            logger.add_success("全屏截图成功")
            logger.add_image("测试截图", screenshot_path)
        else:
            logger.add_error("全屏截图也失败")
            return False
    
    logger.finalize_session()
    print("✅ 集成测试通过")
    return True


def main():
    """主测试函数"""
    print("🚀 开始系统测试...\n")
    
    tests = [
        ("配置系统", test_config_system),
        ("日志系统", test_logger_system),
        ("窗口管理器", test_window_manager),
        ("截图管理器", test_screenshot_manager),
        ("集成测试", run_integration_test)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*50}")
            print(f"测试: {test_name}")
            print('='*50)
            
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_name} 测试失败")
                
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} 测试异常: {str(e)}")
    
    print(f"\n{'='*50}")
    print("测试结果汇总")
    print('='*50)
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📊 总计: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！系统已准备就绪。")
        return True
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败，请检查相关功能。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 