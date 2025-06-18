#!/bin/bash

# Mini Motorways 集成版游戏控制器启动脚本
# 整合了所有修复的完整版本

echo "🎮 Mini Motorways 集成版游戏控制器"
echo "=================================="
echo "📍 当前目录: $(pwd)"
echo "⏰ 启动时间: $(date)"
echo ""

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 虚拟环境已激活: $VIRTUAL_ENV"
else
    echo "⚠️  虚拟环境未激活，正在激活..."
    source venv/bin/activate
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo "✅ 虚拟环境激活成功"
    else
        echo "❌ 虚拟环境激活失败"
        exit 1
    fi
fi

echo ""
echo "🚀 启动集成版游戏控制器..."
echo "包含功能："
echo "  ✅ 多显示器支持"
echo "  ✅ 精确UI检测"
echo "  ✅ 鼠标移动控制"
echo "  ✅ 窗口激活"
echo "  ✅ 完整日志记录"
echo ""

# 切换到src/core目录
cd src/core

# 运行集成版控制器
python3 integrated_game_controller.py

echo ""
echo "🏁 程序执行完成"
echo "⏰ 结束时间: $(date)" 