"""
Markdown格式的日志记录器
提供结构化的日志记录功能，支持图片嵌入和格式化输出
"""

import os
import time
from datetime import datetime
from typing import Optional, List, Tuple
from pathlib import Path


class MarkdownLogger:
    """Markdown格式日志记录器"""
    
    def __init__(self, log_file: str = "logs/session_log.md"):
        """
        初始化日志记录器
        
        Args:
            log_file: 日志文件路径
        """
        self.log_file = Path(log_file)
        self.session_start_time = datetime.now()
        self.operation_count = 0
        self.success_count = 0
        self.error_count = 0
        self.screenshot_count = 0
        
        # 确保日志目录存在
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化日志文件
        self._init_log_file()
    
    def _init_log_file(self):
        """初始化日志文件，写入头部信息"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"# Mini Motorways 自动化运行日志\n\n")
            f.write(f"## 会话开始时间: {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳字符串"""
        return datetime.now().strftime('%H:%M:%S')
    
    def _write_to_file(self, content: str):
        """写入内容到日志文件"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def add_section(self, title: str, level: int = 3):
        """
        添加新的章节
        
        Args:
            title: 章节标题
            level: 标题级别 (1-6)
        """
        timestamp = self._get_timestamp()
        header = "#" * level
        content = f"{header} {timestamp} - {title}\n\n"
        self._write_to_file(content)
    
    def add_text(self, text: str):
        """添加普通文本"""
        content = f"{text}\n\n"
        self._write_to_file(content)
    
    def add_success(self, message: str):
        """添加成功信息"""
        self.success_count += 1
        content = f"- ✅ {message}\n"
        self._write_to_file(content)
    
    def add_error(self, message: str):
        """添加错误信息"""
        self.error_count += 1
        content = f"- ❌ {message}\n"
        self._write_to_file(content)
    
    def add_warning(self, message: str):
        """添加警告信息"""
        content = f"- ⚠️ {message}\n"
        self._write_to_file(content)
    
    def add_info(self, message: str):
        """添加信息"""
        content = f"- ℹ️ {message}\n"
        self._write_to_file(content)
    
    def add_action(self, action: str, details: Optional[dict] = None):
        """
        添加操作记录
        
        Args:
            action: 操作描述
            details: 操作详情字典
        """
        self.operation_count += 1
        content = f"- 🎮 **操作**: {action}\n"
        
        if details:
            for key, value in details.items():
                content += f"  - {key}: {value}\n"
        
        self._write_to_file(content)
    
    def add_image(self, description: str, image_path: str, alt_text: Optional[str] = None):
        """
        添加图片
        
        Args:
            description: 图片描述
            image_path: 图片路径
            alt_text: 图片替代文本
        """
        self.screenshot_count += 1
        if alt_text is None:
            alt_text = description
        
        content = f"**{description}**:\n\n"
        content += f"![{alt_text}]({image_path})\n\n"
        self._write_to_file(content)
    
    def add_recognition_result(self, stage: str, elements: List[dict], confidence: float):
        """
        添加识别结果
        
        Args:
            stage: 识别的游戏阶段
            elements: 识别到的元素列表
            confidence: 整体置信度
        """
        content = f"- 🎯 **当前阶段**: {stage}\n"
        content += f"- 📊 **整体置信度**: {confidence:.2%}\n"
        content += f"- 🔍 **识别结果**:\n"
        
        for element in elements:
            name = element.get('name', '未知元素')
            coords = element.get('coordinates', (0, 0))
            conf = element.get('confidence', 0)
            status = "✅" if conf > 0.8 else "⚠️" if conf > 0.5 else "❌"
            
            content += f"  - {name}: 坐标{coords} 置信度{conf:.0%} {status}\n"
        
        content += "\n"
        self._write_to_file(content)
    
    def add_server_communication(self, request_data: dict, response_data: dict, success: bool):
        """
        添加服务器通信记录
        
        Args:
            request_data: 请求数据
            response_data: 响应数据
            success: 是否成功
        """
        status = "✅ 成功" if success else "❌ 失败"
        content = f"- 🌐 **服务器通信**: {status}\n"
        content += f"  - 请求大小: {len(str(request_data))} 字符\n"
        content += f"  - 响应大小: {len(str(response_data))} 字符\n"
        
        if not success:
            content += f"  - 错误信息: {response_data.get('error', '未知错误')}\n"
        
        content += "\n"
        self._write_to_file(content)
    
    def add_separator(self):
        """添加分隔线"""
        content = "---\n\n"
        self._write_to_file(content)
    
    def add_statistics(self):
        """添加统计信息"""
        duration = datetime.now() - self.session_start_time
        duration_str = str(duration).split('.')[0]  # 去掉微秒
        
        content = "## 会话统计信息\n\n"
        content += f"- ⏱️ **运行时长**: {duration_str}\n"
        content += f"- 🎮 **总操作数**: {self.operation_count}\n"
        content += f"- ✅ **成功操作**: {self.success_count}\n"
        content += f"- ❌ **失败操作**: {self.error_count}\n"
        content += f"- 📸 **截图数量**: {self.screenshot_count}\n"
        
        if self.operation_count > 0:
            success_rate = (self.success_count / self.operation_count) * 100
            content += f"- 📈 **成功率**: {success_rate:.1f}%\n"
        
        content += "\n"
        self._write_to_file(content)
    
    def finalize_session(self):
        """结束会话，添加最终统计信息"""
        self.add_separator()
        self.add_statistics()
        
        end_time = datetime.now()
        content = f"## 会话结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        self._write_to_file(content)


# 全局日志实例
_logger_instance = None

def get_logger(log_file: str = "logs/session_log.md") -> MarkdownLogger:
    """获取全局日志实例"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = MarkdownLogger(log_file)
    return _logger_instance

def reset_logger(log_file: str = "logs/session_log.md") -> MarkdownLogger:
    """重置日志实例"""
    global _logger_instance
    _logger_instance = MarkdownLogger(log_file)
    return _logger_instance 