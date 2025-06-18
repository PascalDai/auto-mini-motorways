#!/usr/bin/env python3

"""
图像分析测试脚本

用于测试Mini Motorways游戏截图的分析功能
分析游戏状态、界面元素等信息
"""

import sys
import json
import logging
import numpy as np
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent))

from image_analyzer import ImageAnalyzer
from config import SCREENSHOTS_DIR

# 设置日志级别
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("🔍 Mini Motorways - 图像分析测试")
    print("=" * 60)
    print()
    print("这个程序会分析已捕获的游戏截图")
    print("识别游戏状态、界面元素和颜色分布")
    print()

def print_analysis_result(result: dict, index: int = None):
    """打印分析结果"""
    if 'error' in result:
        print(f"❌ 分析失败: {result['error']}")
        return
    
    # 基础信息
    if index is not None:
        print(f"📸 第 {index} 张图像分析结果:")
    else:
        print("📸 图像分析结果:")
    
    print(f"   文件: {Path(result['image_path']).name}")
    print(f"   尺寸: {result['image_size'][0]} x {result['image_size'][1]}")
    print(f"   状态: {result['game_state_name']} ({result['game_state']})")
    
    # 详细分析
    if result['analysis_details']:
        details = result['analysis_details']
        
        if 'color_analysis' in details:
            color_info = details['color_analysis']
            print(f"   颜色分析:")
            for color, ratio in color_info.items():
                print(f"     - {color}: {ratio:.1%}")
        
        if 'terrain_analysis' in details:
            terrain_info = details['terrain_analysis']
            print(f"   地形分析:")
            for terrain, ratio in terrain_info.items():
                print(f"     - {terrain}: {ratio:.1%}")
        
        if 'ui_elements' in details:
            ui_info = details['ui_elements']
            print(f"   界面元素:")
            for element, present in ui_info.items():
                status = "✅" if present else "❌"
                print(f"     - {element}: {status}")
        
        if 'game_elements' in details:
            game_info = details['game_elements']
            print(f"   游戏元素:")
            for element, present in game_info.items():
                status = "✅" if present else "❌"
                print(f"     - {element}: {status}")
    
    print()

def test_single_image():
    """测试单张图像分析"""
    print("🔍 单张图像分析测试")
    print("-" * 40)
    
    # 获取最新的截图
    screenshot_dir = Path(SCREENSHOTS_DIR)
    if not screenshot_dir.exists():
        print("❌ 截图目录不存在")
        return False
    
    image_files = list(screenshot_dir.glob("*.png"))
    if not image_files:
        print("❌ 没有找到截图文件")
        return False
    
    # 选择最新的截图
    latest_image = max(image_files, key=lambda f: f.stat().st_mtime)
    print(f"📸 分析最新截图: {latest_image.name}")
    print()
    
    # 创建分析器并分析
    analyzer = ImageAnalyzer()
    result = analyzer.analyze_image(str(latest_image))
    
    print_analysis_result(result)
    return True

def test_batch_analysis():
    """测试批量图像分析"""
    print("📊 批量图像分析测试")
    print("-" * 40)
    
    # 创建分析器
    analyzer = ImageAnalyzer()
    
    # 批量分析所有截图
    results = analyzer.batch_analyze(str(SCREENSHOTS_DIR))
    
    if not results:
        print("❌ 没有找到可分析的图像")
        return False
    
    print(f"✅ 成功分析 {len(results)} 张图像")
    print()
    
    # 统计游戏状态
    state_count = {}
    for result in results:
        if 'error' not in result:
            state = result['game_state_name']
            state_count[state] = state_count.get(state, 0) + 1
    
    print("📊 游戏状态统计:")
    for state, count in state_count.items():
        print(f"   - {state}: {count} 张")
    print()
    
    # 显示每张图像的分析结果
    print("📸 详细分析结果:")
    for i, result in enumerate(results, 1):
        print_analysis_result(result, i)
    
    return True

def save_analysis_report(results: list):
    """保存分析报告"""
    try:
        # 创建报告目录
        report_dir = Path("data/analysis_reports")
        report_dir.mkdir(exist_ok=True)
        
        # 生成报告文件名
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"analysis_report_{timestamp}.json"
        
        # 保存报告 (处理numpy类型)
        def convert_numpy_types(obj):
            if isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj
        
        # 递归转换所有numpy类型
        def clean_for_json(data):
            if isinstance(data, dict):
                return {k: clean_for_json(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [clean_for_json(item) for item in data]
            else:
                return convert_numpy_types(data)
        
        cleaned_results = clean_for_json(results)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 分析报告已保存: {report_file}")
        return True
        
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
        return False

def main():
    """主函数"""
    print_welcome()
    
    try:
        # 测试单张图像分析
        if test_single_image():
            print("✅ 单张图像分析测试成功")
        else:
            print("❌ 单张图像分析测试失败")
            return
        
        print("=" * 60)
        
        # 测试批量分析
        analyzer = ImageAnalyzer()
        results = analyzer.batch_analyze(str(SCREENSHOTS_DIR))
        
        if results:
            print("✅ 批量分析测试成功")
            
            # 保存分析报告
            save_analysis_report(results)
            
            # 显示统计信息
            state_count = {}
            for result in results:
                if 'error' not in result:
                    state = result['game_state_name']
                    state_count[state] = state_count.get(state, 0) + 1
            
            print()
            print("📊 最终统计:")
            print(f"   总图像数量: {len(results)}")
            print("   游戏状态分布:")
            for state, count in state_count.items():
                percentage = count / len(results) * 100
                print(f"     - {state}: {count} 张 ({percentage:.1f}%)")
        else:
            print("❌ 批量分析测试失败")
        
        print()
        print("=" * 60)
        print("🎯 第二阶段图像分析测试完成")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 