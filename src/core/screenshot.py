"""
截图管理器
负责游戏画面的截图、保存和管理
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import mss

from ..utils.logger import get_logger
from ..utils.config import get_config


class ScreenshotManager:
    """截图管理器"""
    
    def __init__(self):
        """初始化截图管理器"""
        self.config = get_config()
        self.logger = get_logger()
        self.screenshot_dir = Path("screenshots")
        self.current_session_dir = None
        self.screenshot_count = 0
        
        # 创建截图目录
        self._setup_directories()
        
        # 初始化截图工具
        self.sct = mss.mss()
    
    def _setup_directories(self):
        """设置截图目录结构"""
        # 创建主截图目录
        self.screenshot_dir.mkdir(exist_ok=True)
        
        # 创建当前会话目录（按日期时间命名）
        session_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.current_session_dir = self.screenshot_dir / session_name
        self.current_session_dir.mkdir(exist_ok=True)
        
        self.logger.add_info(f"截图保存目录: {self.current_session_dir}")
    
    def take_screenshot(self, region: Optional[Tuple[int, int, int, int]] = None, 
                       description: str = "游戏截图") -> Optional[str]:
        """
        截取屏幕或指定区域
        
        Args:
            region: 截图区域 (left, top, width, height)
            description: 截图描述
            
        Returns:
            截图文件路径，失败返回None
        """
        try:
            self.screenshot_count += 1
            timestamp = datetime.now().strftime("%H-%M-%S-%f")[:-3]  # 精确到毫秒
            
            # 确定截图区域
            if region:
                monitor = {
                    "left": region[0],
                    "top": region[1], 
                    "width": region[2],
                    "height": region[3]
                }
            else:
                # 使用主显示器
                monitor = self.sct.monitors[1]
            
            # 截图
            screenshot = self.sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # 保存原始截图
            raw_filename = f"{timestamp}_raw.png"
            raw_path = self.current_session_dir / raw_filename
            
            if self.config.get('screenshot.save_raw', True):
                quality = self.config.get('screenshot.quality', 95)
                img.save(raw_path, "PNG", optimize=True)
            
            # 记录到日志
            relative_path = f"screenshots/{self.current_session_dir.name}/{raw_filename}"
            self.logger.add_info(f"截图保存: {relative_path}")
            
            return str(raw_path)
            
        except Exception as e:
            self.logger.add_error(f"截图失败: {str(e)}")
            return None
    
    def create_marked_screenshot(self, original_path: str, elements: list, 
                               description: str = "标记截图") -> Optional[str]:
        """
        创建带标记的截图
        
        Args:
            original_path: 原始截图路径
            elements: 要标记的元素列表
            description: 标记截图描述
            
        Returns:
            标记截图文件路径，失败返回None
        """
        try:
            # 读取原始图片
            img = Image.open(original_path)
            draw = ImageDraw.Draw(img)
            
            # 尝试加载字体
            try:
                # 尝试使用系统字体
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
            except:
                try:
                    # 备用字体
                    font = ImageFont.truetype("arial.ttf", 16)
                except:
                    # 使用默认字体
                    font = ImageFont.load_default()
            
            # 定义颜色映射
            color_map = {
                'success': '#00FF00',    # 绿色 - 成功识别
                'warning': '#FFFF00',    # 黄色 - 警告
                'error': '#FF0000',      # 红色 - 错误
                'info': '#0000FF',       # 蓝色 - 信息
                'action': '#FF00FF'      # 紫色 - 操作目标
            }
            
            # 标记每个元素
            for i, element in enumerate(elements):
                name = element.get('name', f'元素{i+1}')
                coords = element.get('coordinates', (0, 0))
                confidence = element.get('confidence', 0)
                element_type = element.get('type', 'info')
                
                # 确定颜色
                color = color_map.get(element_type, '#FFFFFF')
                
                # 绘制矩形框
                if 'bbox' in element:
                    # 如果有边界框信息
                    bbox = element['bbox']
                    left, top, right, bottom = bbox
                    draw.rectangle([left, top, right, bottom], outline=color, width=2)
                else:
                    # 如果只有坐标点，绘制圆形标记
                    x, y = coords
                    radius = 10
                    draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                               outline=color, width=2)
                
                # 添加文字标签
                label = f"{name} ({confidence:.0%})" if confidence > 0 else name
                text_x, text_y = coords[0] + 15, coords[1] - 25
                
                # 绘制文字背景
                text_bbox = draw.textbbox((text_x, text_y), label, font=font)
                draw.rectangle(text_bbox, fill='black', outline=color)
                
                # 绘制文字
                draw.text((text_x, text_y), label, fill='white', font=font)
            
            # 保存标记截图
            original_name = Path(original_path).stem
            marked_filename = f"{original_name}_marked.png"
            marked_path = self.current_session_dir / marked_filename
            
            if self.config.get('screenshot.save_marked', True):
                img.save(marked_path, "PNG", optimize=True)
            
            # 记录到日志
            relative_path = f"screenshots/{self.current_session_dir.name}/{marked_filename}"
            self.logger.add_info(f"标记截图保存: {relative_path}")
            
            return str(marked_path)
            
        except Exception as e:
            self.logger.add_error(f"创建标记截图失败: {str(e)}")
            return None
    
    def save_debug_image(self, image_array: np.ndarray, filename: str, 
                        description: str = "调试图片") -> Optional[str]:
        """
        保存调试用的图片数组
        
        Args:
            image_array: 图片数组（OpenCV格式）
            filename: 文件名
            description: 图片描述
            
        Returns:
            保存的文件路径，失败返回None
        """
        try:
            # 确保文件名有扩展名
            if not filename.endswith(('.png', '.jpg', '.jpeg')):
                filename += '.png'
            
            debug_path = self.current_session_dir / filename
            
            # 转换颜色格式（OpenCV使用BGR，PIL使用RGB）
            if len(image_array.shape) == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            
            # 保存图片
            cv2.imwrite(str(debug_path), image_array)
            
            # 记录到日志
            relative_path = f"screenshots/{self.current_session_dir.name}/{filename}"
            self.logger.add_info(f"调试图片保存: {relative_path}")
            
            return str(debug_path)
            
        except Exception as e:
            self.logger.add_error(f"保存调试图片失败: {str(e)}")
            return None
    
    def cleanup_old_screenshots(self, keep_days: int = None):
        """
        清理旧的截图文件
        
        Args:
            keep_days: 保留天数，None则使用配置文件设置
        """
        if keep_days is None:
            keep_days = self.config.get('logging.keep_days', 7)
        
        if not self.config.get('logging.cleanup_old_logs', True):
            return
        
        try:
            current_time = time.time()
            cutoff_time = current_time - (keep_days * 24 * 60 * 60)
            
            deleted_count = 0
            for session_dir in self.screenshot_dir.iterdir():
                if session_dir.is_dir() and session_dir != self.current_session_dir:
                    # 检查目录创建时间
                    dir_time = session_dir.stat().st_ctime
                    if dir_time < cutoff_time:
                        # 删除整个会话目录
                        import shutil
                        shutil.rmtree(session_dir)
                        deleted_count += 1
            
            if deleted_count > 0:
                self.logger.add_info(f"清理了 {deleted_count} 个旧的截图会话目录")
                
        except Exception as e:
            self.logger.add_error(f"清理旧截图失败: {str(e)}")
    
    def get_screenshot_stats(self) -> dict:
        """
        获取截图统计信息
        
        Returns:
            统计信息字典
        """
        try:
            stats = {
                'current_session_count': self.screenshot_count,
                'current_session_dir': str(self.current_session_dir),
                'total_sessions': len([d for d in self.screenshot_dir.iterdir() if d.is_dir()]),
                'total_size_mb': 0
            }
            
            # 计算总大小
            total_size = 0
            for file_path in self.screenshot_dir.rglob('*.png'):
                total_size += file_path.stat().st_size
            
            stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            self.logger.add_error(f"获取截图统计失败: {str(e)}")
            return {}
    
    def get_latest_screenshot(self) -> Optional[str]:
        """
        获取最新的截图路径
        
        Returns:
            最新截图路径，没有则返回None
        """
        try:
            png_files = list(self.current_session_dir.glob("*_raw.png"))
            if png_files:
                # 按修改时间排序，返回最新的
                latest_file = max(png_files, key=lambda p: p.stat().st_mtime)
                return str(latest_file)
            return None
        except Exception as e:
            self.logger.add_error(f"获取最新截图失败: {str(e)}")
            return None 