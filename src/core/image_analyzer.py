"""
图像分析模块
负责分析Mini Motorways游戏截图，识别游戏状态和界面元素
"""

import cv2
import numpy as np
import logging
from PIL import Image
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """图像分析器类"""
    
    def __init__(self):
        """初始化图像分析器"""
        self.game_states = {
            'main_menu': '主界面',
            'city_selection': '城市选择',
            'game_playing': '游戏进行中',
            'game_paused': '游戏暂停',
            'game_over': '游戏结束',
            'unknown': '未知状态'
        }
        
        # 预定义的颜色范围（HSV格式）- 基于实际截图分析优化
        self.color_ranges = {
            'menu_background': [(0, 0, 200), (180, 30, 255)],   # 主界面背景（高明度低饱和度）
            'menu_blue': [(90, 20, 100), (120, 200, 255)],      # 菜单蓝色元素
            'road_gray': [(0, 0, 40), (180, 30, 120)],          # 道路灰色
            'grass_green': [(35, 40, 40), (85, 255, 255)],      # 草地绿色
            'water_blue': [(90, 50, 50), (110, 255, 255)],      # 水面蓝色
            'building_red': [(0, 120, 120), (10, 255, 255)],    # 建筑红色
            'ui_elements': [(0, 0, 180), (180, 50, 255)],       # UI元素（浅色）
            'accent_yellow': [(15, 50, 100), (35, 255, 255)],   # 黄色强调色
            'accent_orange': [(10, 50, 100), (25, 255, 255)]    # 橙色强调色
        }
        
        logger.info("图像分析器已初始化")
    
    def load_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        加载图像文件
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            OpenCV格式的图像数组，失败返回None
        """
        try:
            # 使用PIL加载图像，然后转换为OpenCV格式
            pil_image = Image.open(image_path)
            # PIL使用RGB，OpenCV使用BGR，需要转换
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            logger.info(f"成功加载图像: {image_path}, 尺寸: {opencv_image.shape}")
            return opencv_image
        except Exception as e:
            logger.error(f"加载图像失败: {image_path}, 错误: {e}")
            return None
    
    def detect_game_state(self, image: np.ndarray) -> str:
        """
        检测当前游戏状态
        
        Args:
            image: OpenCV格式的图像
            
        Returns:
            游戏状态字符串
        """
        try:
            # 转换为HSV颜色空间，便于颜色检测
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 获取图像尺寸
            height, width = image.shape[:2]
            
            # 检查是否为主界面
            if self._is_main_menu(image, hsv):
                return 'main_menu'
            
            # 检查是否为城市选择界面
            if self._is_city_selection(image, hsv):
                return 'city_selection'
            
            # 检查是否为游戏进行中
            if self._is_game_playing(image, hsv):
                return 'game_playing'
            
            # 检查是否为游戏暂停
            if self._is_game_paused(image, hsv):
                return 'game_paused'
            
            # 检查是否为游戏结束
            if self._is_game_over(image, hsv):
                return 'game_over'
            
            return 'unknown'
            
        except Exception as e:
            logger.error(f"检测游戏状态时出错: {e}")
            return 'unknown'
    
    def _is_main_menu(self, image: np.ndarray, hsv: np.ndarray) -> bool:
        """检测是否为主界面"""
        try:
            # 主界面特征：大量浅色背景 + 少量蓝色元素 + 强调色
            background_mask = self._create_color_mask(hsv, 'menu_background')
            blue_mask = self._create_color_mask(hsv, 'menu_blue')
            yellow_mask = self._create_color_mask(hsv, 'accent_yellow')
            orange_mask = self._create_color_mask(hsv, 'accent_orange')
            
            total_pixels = image.shape[0] * image.shape[1]
            
            # 计算各颜色区域的比例
            background_ratio = np.sum(background_mask) / total_pixels
            blue_ratio = np.sum(blue_mask) / total_pixels
            yellow_ratio = np.sum(yellow_mask) / total_pixels
            orange_ratio = np.sum(orange_mask) / total_pixels
            
            # 主界面判断条件：
            # 1. 大量浅色背景 (>80%)
            # 2. 有少量蓝色元素 (1-10%)
            # 3. 可能有强调色 (黄色或橙色)
            is_main_menu = (
                background_ratio > 0.8 and
                0.01 <= blue_ratio <= 0.1 and
                (yellow_ratio > 0.005 or orange_ratio > 0.005)
            )
            
            if is_main_menu:
                logger.debug(f"检测到主界面特征 - 背景: {background_ratio:.3f}, 蓝色: {blue_ratio:.3f}, 黄色: {yellow_ratio:.3f}, 橙色: {orange_ratio:.3f}")
                return True
            
            # 备用判断：如果背景比例很高，也可能是主界面
            if background_ratio > 0.9:
                logger.debug(f"检测到主界面特征(备用) - 背景比例: {background_ratio:.3f}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"检测主界面时出错: {e}")
            return False
    
    def _is_city_selection(self, image: np.ndarray, hsv: np.ndarray) -> bool:
        """检测是否为城市选择界面"""
        # 城市选择界面通常有地图预览和城市名称
        # 这里先简单实现，后续可以完善
        return False
    
    def _is_game_playing(self, image: np.ndarray, hsv: np.ndarray) -> bool:
        """检测是否为游戏进行中"""
        try:
            # 游戏进行中会有道路、建筑、草地等元素
            road_mask = self._create_color_mask(hsv, 'road_gray')
            green_mask = self._create_color_mask(hsv, 'grass_green')
            
            # 计算道路和绿地的比例
            road_ratio = np.sum(road_mask) / (image.shape[0] * image.shape[1])
            green_ratio = np.sum(green_mask) / (image.shape[0] * image.shape[1])
            
            # 游戏中判断条件：有道路和绿地
            if road_ratio > 0.1 and green_ratio > 0.2:
                logger.debug(f"检测到游戏进行中特征 - 道路比例: {road_ratio:.3f}, 绿地比例: {green_ratio:.3f}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"检测游戏进行状态时出错: {e}")
            return False
    
    def _is_game_paused(self, image: np.ndarray, hsv: np.ndarray) -> bool:
        """检测是否为游戏暂停"""
        # 暂停状态通常会有暂停菜单或半透明覆盖层
        # 这里先简单实现，后续可以完善
        return False
    
    def _is_game_over(self, image: np.ndarray, hsv: np.ndarray) -> bool:
        """检测是否为游戏结束"""
        # 游戏结束通常会有分数显示和重新开始按钮
        # 这里先简单实现，后续可以完善
        return False
    
    def _create_color_mask(self, hsv: np.ndarray, color_name: str) -> np.ndarray:
        """
        创建颜色掩码
        
        Args:
            hsv: HSV格式的图像
            color_name: 颜色名称
            
        Returns:
            二值掩码
        """
        if color_name not in self.color_ranges:
            logger.warning(f"未知的颜色名称: {color_name}")
            return np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        lower, upper = self.color_ranges[color_name]
        lower = np.array(lower, dtype=np.uint8)
        upper = np.array(upper, dtype=np.uint8)
        
        return cv2.inRange(hsv, lower, upper)
    
    def analyze_image(self, image_path: str) -> Dict:
        """
        分析单张图像
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            分析结果字典
        """
        try:
            # 加载图像
            image = self.load_image(image_path)
            if image is None:
                return {'error': '无法加载图像'}
            
            # 检测游戏状态
            game_state = self.detect_game_state(image)
            
            # 基础图像信息
            height, width = image.shape[:2]
            
            # 构建分析结果
            result = {
                'timestamp': datetime.now().isoformat(),
                'image_path': image_path,
                'image_size': (width, height),
                'game_state': game_state,
                'game_state_name': self.game_states.get(game_state, '未知'),
                'analysis_details': {}
            }
            
            # 根据游戏状态添加详细分析
            if game_state == 'main_menu':
                result['analysis_details'] = self._analyze_main_menu(image)
            elif game_state == 'game_playing':
                result['analysis_details'] = self._analyze_game_playing(image)
            
            logger.info(f"图像分析完成: {game_state} - {self.game_states.get(game_state)}")
            return result
            
        except Exception as e:
            logger.error(f"分析图像时出错: {e}")
            return {'error': str(e)}
    
    def _analyze_main_menu(self, image: np.ndarray) -> Dict:
        """分析主界面详情"""
        try:
            # 转换为HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 分析颜色分布
            background_mask = self._create_color_mask(hsv, 'menu_background')
            blue_mask = self._create_color_mask(hsv, 'menu_blue')
            yellow_mask = self._create_color_mask(hsv, 'accent_yellow')
            orange_mask = self._create_color_mask(hsv, 'accent_orange')
            
            total_pixels = image.shape[0] * image.shape[1]
            
            return {
                'interface_type': 'main_menu',
                'color_analysis': {
                    'background_ratio': float(np.sum(background_mask) / total_pixels),
                    'blue_ratio': float(np.sum(blue_mask) / total_pixels),
                    'yellow_ratio': float(np.sum(yellow_mask) / total_pixels),
                    'orange_ratio': float(np.sum(orange_mask) / total_pixels)
                },
                'ui_elements': {
                    'has_light_background': np.sum(background_mask) > total_pixels * 0.8,
                    'has_blue_elements': np.sum(blue_mask) > 0,
                    'has_accent_colors': np.sum(yellow_mask) > 0 or np.sum(orange_mask) > 0
                },
                'menu_characteristics': {
                    'high_brightness': True,
                    'low_saturation': True,
                    'minimal_colors': True
                }
            }
            
        except Exception as e:
            logger.error(f"分析主界面时出错: {e}")
            return {'error': str(e)}
    
    def _analyze_game_playing(self, image: np.ndarray) -> Dict:
        """分析游戏进行中的详情"""
        try:
            # 转换为HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # 分析游戏元素
            road_mask = self._create_color_mask(hsv, 'road_gray')
            green_mask = self._create_color_mask(hsv, 'grass_green')
            water_mask = self._create_color_mask(hsv, 'water_blue')
            building_mask = self._create_color_mask(hsv, 'building_red')
            
            total_pixels = image.shape[0] * image.shape[1]
            
            return {
                'interface_type': 'game_playing',
                'terrain_analysis': {
                    'road_ratio': float(np.sum(road_mask) / total_pixels),
                    'green_ratio': float(np.sum(green_mask) / total_pixels),
                    'water_ratio': float(np.sum(water_mask) / total_pixels),
                    'building_ratio': float(np.sum(building_mask) / total_pixels)
                },
                'game_elements': {
                    'has_roads': np.sum(road_mask) > 0,
                    'has_buildings': np.sum(building_mask) > 0,
                    'has_terrain': np.sum(green_mask) > 0
                }
            }
            
        except Exception as e:
            logger.error(f"分析游戏进行状态时出错: {e}")
            return {'error': str(e)}

    def batch_analyze(self, image_dir: str) -> List[Dict]:
        """
        批量分析图像目录中的所有图像
        
        Args:
            image_dir: 图像目录路径
            
        Returns:
            分析结果列表
        """
        try:
            image_path = Path(image_dir)
            if not image_path.exists():
                logger.error(f"图像目录不存在: {image_dir}")
                return []
            
            # 获取所有PNG图像文件
            image_files = list(image_path.glob("*.png"))
            if not image_files:
                logger.warning(f"目录中没有找到PNG图像文件: {image_dir}")
                return []
            
            # 按文件名排序
            image_files.sort()
            
            results = []
            for image_file in image_files:
                logger.info(f"正在分析: {image_file.name}")
                result = self.analyze_image(str(image_file))
                results.append(result)
            
            logger.info(f"批量分析完成，共处理 {len(results)} 张图像")
            return results
            
        except Exception as e:
            logger.error(f"批量分析时出错: {e}")
            return [] 