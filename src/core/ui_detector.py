"""
UI元素检测模块
专门用于识别Mini Motorways主界面的按钮、菜单等可交互元素
"""

import cv2
import numpy as np
import logging
from PIL import Image
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class UIDetector:
    """UI元素检测器类"""
    
    def __init__(self):
        """初始化UI检测器"""
        # 定义UI元素的特征
        self.ui_elements = {
            'play_button': {
                'description': '游玩按钮',
                'color_range': [(60, 20, 60), (110, 255, 255)],  # 使用更宽松的青绿色范围
                'min_size': (20, 15),  # 进一步放宽最小尺寸要求
                'max_size': (200, 100),  # 允许更大的按钮
                'expected_position': 'center_bottom'  # 预期位置：底部中央
            },
            'city_selection': {
                'description': '城市选择区域',
                'color_range': [(90, 30, 100), (120, 200, 255)],  # 蓝色区域
                'min_size': (100, 100),
                'max_size': (400, 300),
                'expected_position': 'center'
            },
            'menu_button': {
                'description': '菜单按钮',
                'color_range': [(0, 0, 180), (180, 50, 255)],  # 浅色按钮
                'min_size': (50, 20),
                'max_size': (200, 80),
                'expected_position': 'top_left'  # 左上角的返回按钮
            }
        }
        
        logger.info("UI元素检测器已初始化")
    
    def detect_ui_elements(self, image: np.ndarray) -> Dict:
        """
        检测图像中的UI元素
        
        Args:
            image: OpenCV格式的图像
            
        Returns:
            检测结果字典
        """
        try:
            # 转换为HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            height, width = image.shape[:2]
            
            detected_elements = {}
            
            # 检测每种UI元素
            for element_name, element_config in self.ui_elements.items():
                elements = self._detect_element_type(hsv, element_name, element_config, (width, height))
                if elements:
                    detected_elements[element_name] = elements
            
            return {
                'detected_elements': detected_elements,
                'image_size': (width, height),
                'total_elements': sum(len(elements) for elements in detected_elements.values())
            }
            
        except Exception as e:
            logger.error(f"检测UI元素时出错: {e}")
            return {'error': str(e)}
    
    def _detect_element_type(self, hsv: np.ndarray, element_name: str, config: Dict, image_size: Tuple[int, int]) -> List[Dict]:
        """检测特定类型的UI元素"""
        try:
            # 创建颜色掩码
            lower = np.array(config['color_range'][0])
            upper = np.array(config['color_range'][1])
            mask = cv2.inRange(hsv, lower, upper)
            
            # 形态学操作，去除噪声
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            detected_elements = []
            width, height = image_size
            
            for contour in contours:
                # 获取边界框
                x, y, w, h = cv2.boundingRect(contour)
                
                # 检查大小是否符合要求
                min_w, min_h = config['min_size']
                max_w, max_h = config['max_size']
                
                if min_w <= w <= max_w and min_h <= h <= max_h:
                    # 计算中心点
                    center_x = x + w // 2
                    center_y = y + h // 2
                    
                    # 检查位置是否合理
                    if self._is_position_valid(center_x, center_y, width, height, config['expected_position']):
                        # 计算置信度
                        area = cv2.contourArea(contour)
                        bbox_area = w * h
                        confidence = area / bbox_area if bbox_area > 0 else 0
                        
                        element_info = {
                            'bbox': (x, y, w, h),
                            'center': (center_x, center_y),
                            'area': int(area),
                            'confidence': float(confidence),
                            'description': config['description']
                        }
                        
                        detected_elements.append(element_info)
            
            # 按置信度排序
            detected_elements.sort(key=lambda x: x['confidence'], reverse=True)
            
            logger.debug(f"检测到 {len(detected_elements)} 个 {element_name} 元素")
            return detected_elements
            
        except Exception as e:
            logger.error(f"检测 {element_name} 时出错: {e}")
            return []
    
    def _is_position_valid(self, x: int, y: int, width: int, height: int, expected_position: str) -> bool:
        """检查位置是否合理"""
        try:
            center_x, center_y = width // 2, height // 2
            
            if expected_position == 'center':
                # 中心区域：距离中心点不超过1/3图像尺寸
                return (abs(x - center_x) < width // 3 and abs(y - center_y) < height // 3)
            
            elif expected_position == 'center_bottom':
                # 中下区域：水平居中，垂直在下半部分
                return (abs(x - center_x) < width // 2 and y > height * 0.7)
            
            elif expected_position == 'top_right':
                # 右上区域
                return (x > width * 0.7 and y < height * 0.3)
            
            elif expected_position == 'top_left':
                # 左上区域
                return (x < width * 0.3 and y < height * 0.3)
            
            else:
                # 未知位置，默认接受
                return True
                
        except Exception as e:
            logger.error(f"检查位置时出错: {e}")
            return False
    
    def find_best_play_button(self, image: np.ndarray) -> Optional[Dict]:
        """查找最佳的开始游戏按钮"""
        try:
            detection_result = self.detect_ui_elements(image)
            
            if 'error' in detection_result:
                return None
            
            play_buttons = detection_result['detected_elements'].get('play_button', [])
            
            if not play_buttons:
                logger.warning("未找到开始游戏按钮")
                return None
            
            # 返回置信度最高的按钮
            best_button = play_buttons[0]
            logger.info(f"找到开始游戏按钮: 位置 {best_button['center']}, 置信度 {best_button['confidence']:.2f}")
            
            return best_button
            
        except Exception as e:
            logger.error(f"查找开始游戏按钮时出错: {e}")
            return None
    
    def find_city_selection_area(self, image: np.ndarray) -> Optional[Dict]:
        """查找城市选择区域"""
        try:
            detection_result = self.detect_ui_elements(image)
            
            if 'error' in detection_result:
                return None
            
            city_areas = detection_result['detected_elements'].get('city_selection', [])
            
            if not city_areas:
                logger.warning("未找到城市选择区域")
                return None
            
            # 返回最大的区域
            best_area = max(city_areas, key=lambda x: x['area'])
            logger.info(f"找到城市选择区域: 位置 {best_area['center']}, 大小 {best_area['area']}")
            
            return best_area
            
        except Exception as e:
            logger.error(f"查找城市选择区域时出错: {e}")
            return None
    
    def analyze_main_menu_layout(self, image: np.ndarray) -> Dict:
        """分析主界面布局"""
        try:
            detection_result = self.detect_ui_elements(image)
            
            if 'error' in detection_result:
                return detection_result
            
            detected_elements = detection_result['detected_elements']
            width, height = detection_result['image_size']
            
            # 分析布局
            layout_analysis = {
                'has_play_button': 'play_button' in detected_elements,
                'has_city_selection': 'city_selection' in detected_elements,
                'has_menu_button': 'menu_button' in detected_elements,
                'total_interactive_elements': detection_result['total_elements'],
                'recommended_action': self._get_recommended_action(detected_elements)
            }
            
            # 添加具体元素信息
            if 'play_button' in detected_elements:
                layout_analysis['play_button_info'] = detected_elements['play_button'][0]
            
            if 'city_selection' in detected_elements:
                layout_analysis['city_selection_info'] = detected_elements['city_selection'][0]
            
            return {
                'layout_analysis': layout_analysis,
                'detected_elements': detected_elements,
                'image_size': (width, height)
            }
            
        except Exception as e:
            logger.error(f"分析主界面布局时出错: {e}")
            return {'error': str(e)}
    
    def _get_recommended_action(self, detected_elements: Dict) -> str:
        """根据检测到的元素推荐下一步操作"""
        # 优先级：游玩按钮 > 城市选择 > 菜单按钮
        if 'play_button' in detected_elements:
            return 'click_play_button'
        elif 'city_selection' in detected_elements:
            # 如果有城市选择区域但没有游玩按钮，可能需要先选择城市
            return 'select_city'
        elif 'menu_button' in detected_elements:
            return 'navigate_menu'
        else:
            return 'unknown'
    
    def create_debug_image(self, image: np.ndarray, detection_result: Dict) -> np.ndarray:
        """创建调试图像，标注检测到的UI元素"""
        try:
            debug_image = image.copy()
            
            if 'detected_elements' not in detection_result:
                return debug_image
            
            colors = {
                'play_button': (0, 255, 0),      # 绿色
                'city_selection': (255, 0, 0),   # 蓝色
                'menu_button': (0, 0, 255)       # 红色
            }
            
            for element_type, elements in detection_result['detected_elements'].items():
                color = colors.get(element_type, (128, 128, 128))
                
                for element in elements:
                    x, y, w, h = element['bbox']
                    center_x, center_y = element['center']
                    confidence = element['confidence']
                    
                    # 绘制边界框
                    cv2.rectangle(debug_image, (x, y), (x + w, y + h), color, 2)
                    
                    # 绘制中心点
                    cv2.circle(debug_image, (center_x, center_y), 5, color, -1)
                    
                    # 添加标签
                    label = f"{element_type}: {confidence:.2f}"
                    cv2.putText(debug_image, label, (x, y - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            
            return debug_image
            
        except Exception as e:
            logger.error(f"创建调试图像时出错: {e}")
            return image 