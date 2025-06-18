#!/usr/bin/env python3

"""
颜色调试工具

分析Mini Motorways游戏截图的实际颜色分布
帮助优化颜色识别算法
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from PIL import Image

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent))

from config import SCREENSHOTS_DIR

def analyze_color_distribution(image_path: str):
    """分析图像的颜色分布"""
    try:
        # 加载图像
        pil_image = Image.open(image_path)
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        print(f"📸 分析图像: {Path(image_path).name}")
        print(f"   尺寸: {image.shape[1]} x {image.shape[0]}")
        
        # 转换为HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 分析HSV各通道的分布
        h_channel = hsv[:, :, 0]  # 色调
        s_channel = hsv[:, :, 1]  # 饱和度
        v_channel = hsv[:, :, 2]  # 明度
        
        print(f"   HSV分布:")
        print(f"     H (色调): {h_channel.min()}-{h_channel.max()}, 平均: {h_channel.mean():.1f}")
        print(f"     S (饱和度): {s_channel.min()}-{s_channel.max()}, 平均: {s_channel.mean():.1f}")
        print(f"     V (明度): {v_channel.min()}-{v_channel.max()}, 平均: {v_channel.mean():.1f}")
        
        # 分析主要颜色
        analyze_dominant_colors(image, hsv)
        
        return image, hsv
        
    except Exception as e:
        print(f"❌ 分析图像失败: {e}")
        return None, None

def analyze_dominant_colors(image, hsv):
    """分析主要颜色"""
    try:
        # 将图像重塑为像素列表
        pixels = hsv.reshape(-1, 3)
        
        # 统计不同HSV范围的像素数量
        total_pixels = len(pixels)
        
        color_ranges = {
            '深蓝色': [(100, 50, 50), (130, 255, 255)],
            '浅蓝色': [(90, 30, 100), (120, 200, 255)],
            '白色/灰色': [(0, 0, 180), (180, 30, 255)],
            '黑色/深灰': [(0, 0, 0), (180, 255, 50)],
            '绿色': [(35, 40, 40), (85, 255, 255)],
            '红色': [(0, 120, 120), (10, 255, 255)],
            '黄色': [(15, 100, 100), (35, 255, 255)],
            '橙色': [(10, 100, 100), (25, 255, 255)]
        }
        
        print(f"   颜色分布:")
        for color_name, (lower, upper) in color_ranges.items():
            lower = np.array(lower)
            upper = np.array(upper)
            
            # 创建掩码
            mask = cv2.inRange(hsv, lower, upper)
            count = np.sum(mask > 0)
            percentage = count / total_pixels * 100
            
            if percentage > 0.5:  # 只显示占比大于0.5%的颜色
                print(f"     - {color_name}: {percentage:.1f}%")
        
    except Exception as e:
        print(f"❌ 分析主要颜色失败: {e}")

def sample_pixel_colors(image_path: str, sample_points: list):
    """采样特定位置的像素颜色"""
    try:
        pil_image = Image.open(image_path)
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        print(f"   像素采样:")
        for i, (x, y) in enumerate(sample_points):
            if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
                bgr = image[y, x]
                hsv_val = hsv[y, x]
                print(f"     位置({x}, {y}): BGR{tuple(bgr)} -> HSV{tuple(hsv_val)}")
        
    except Exception as e:
        print(f"❌ 像素采样失败: {e}")

def debug_latest_screenshot():
    """调试最新的截图"""
    print("🔍 颜色分布调试工具")
    print("=" * 50)
    
    # 获取最新截图
    screenshot_dir = Path(SCREENSHOTS_DIR)
    if not screenshot_dir.exists():
        print("❌ 截图目录不存在")
        return
    
    image_files = list(screenshot_dir.glob("*.png"))
    if not image_files:
        print("❌ 没有找到截图文件")
        return
    
    latest_image = max(image_files, key=lambda f: f.stat().st_mtime)
    
    # 分析颜色分布
    image, hsv = analyze_color_distribution(str(latest_image))
    
    if image is not None:
        # 采样一些关键位置的像素
        height, width = image.shape[:2]
        sample_points = [
            (width // 2, height // 2),      # 中心
            (width // 4, height // 4),      # 左上
            (3 * width // 4, height // 4),  # 右上
            (width // 4, 3 * height // 4),  # 左下
            (3 * width // 4, 3 * height // 4)  # 右下
        ]
        
        sample_pixel_colors(str(latest_image), sample_points)
    
    print()

def suggest_color_ranges():
    """根据分析结果建议新的颜色范围"""
    print("💡 建议的颜色范围调整:")
    print("   基于实际截图分析，可能需要调整以下颜色范围:")
    print("   - 主界面背景色")
    print("   - UI文字颜色")
    print("   - 按钮颜色")
    print("   - 游戏地形颜色")
    print()

def main():
    """主函数"""
    try:
        debug_latest_screenshot()
        suggest_color_ranges()
        
        print("🎯 颜色调试完成")
        print("   请根据上述分析结果调整 image_analyzer.py 中的颜色范围")
        
    except Exception as e:
        print(f"❌ 调试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 