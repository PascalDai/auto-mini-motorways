"""
配置管理器
负责读取和管理项目配置文件
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = Path(config_file)
        self.config_data = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f) or {}
            else:
                print(f"配置文件 {self.config_file} 不存在，使用默认配置")
                self.config_data = self._get_default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            self.config_data = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'game': {
                'window_title': 'Mini Motorways',
                'expected_resolution': [1920, 1080],
                'screenshot_region': None
            },
            'screenshot': {
                'save_raw': True,
                'save_marked': True,
                'format': 'png',
                'quality': 95
            },
            'logging': {
                'level': 'INFO',
                'max_screenshots_per_session': 1000,
                'cleanup_old_logs': True,
                'keep_days': 7
            },
            'remote_server': {
                'enabled': False,
                'url': 'http://localhost:8000/api/decision',
                'timeout': 5,
                'retry_times': 3
            },
            'recognition': {
                'confidence_threshold': 0.8,
                'template_matching_threshold': 0.7,
                'ocr_languages': ['en', 'ch_sim']
            },
            'automation': {
                'click_delay': 0.1,
                'drag_speed': 1.0,
                'screenshot_interval': 0.5,
                'max_operation_retry': 3
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置键路径，如 'game.window_title'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config_data
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        设置配置值
        
        Args:
            key_path: 配置键路径
            value: 配置值
        """
        keys = key_path.split('.')
        config = self.config_data
        
        # 创建嵌套字典结构
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get_game_config(self) -> Dict[str, Any]:
        """获取游戏相关配置"""
        return self.get('game', {})
    
    def get_screenshot_config(self) -> Dict[str, Any]:
        """获取截图相关配置"""
        return self.get('screenshot', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志相关配置"""
        return self.get('logging', {})
    
    def get_remote_server_config(self) -> Dict[str, Any]:
        """获取远程服务器相关配置"""
        return self.get('remote_server', {})
    
    def get_recognition_config(self) -> Dict[str, Any]:
        """获取识别相关配置"""
        return self.get('recognition', {})
    
    def get_automation_config(self) -> Dict[str, Any]:
        """获取自动化相关配置"""
        return self.get('automation', {})


# 全局配置实例
_config_instance = None

def get_config(config_file: str = "config.yaml") -> ConfigManager:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager(config_file)
    return _config_instance 