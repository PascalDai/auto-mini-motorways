#!/bin/bash

# Mini Motorways 自动启动测试脚本
# 用于测试从主界面自动选择关卡并开始游戏的功能

echo "🎮 Mini Motorways 自动启动测试"
echo "================================"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 ./install.sh"
    exit 1
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 检查Python模块
echo "📦 检查必要的Python模块..."
python -c "import pyautogui, cv2, numpy, PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少必要的Python模块，请运行 ./install.sh 重新安装"
    exit 1
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p logs
mkdir -p data/debug_images
mkdir -p data/screenshots

# 检查游戏是否运行
echo "🔍 检查Mini Motorways游戏是否运行..."
game_running=$(osascript -e 'tell application "System Events" to exists (process "Mini Motorways")')

if [ "$game_running" = "false" ]; then
    echo "⚠️ 警告：未检测到Mini Motorways游戏进程"
    echo "   请确保游戏已启动并可见"
    read -p "   是否继续测试？(y/n): " continue_test
    if [ "$continue_test" != "y" ]; then
        echo "测试已取消"
        exit 0
    fi
fi

# 显示重要提示
echo ""
echo "⚠️ 重要提示："
echo "   1. 确保Mini Motorways游戏已启动并在主界面"
echo "   2. 游戏窗口应该可见且未被其他窗口遮挡"
echo "   3. 系统将自动点击游戏界面，请勿移动鼠标"
echo "   4. 如需紧急停止，请将鼠标快速移到屏幕角落"
echo "   5. 测试过程中会保存调试图像到 data/debug_images/"
echo ""

# 询问用户确认
read -p "🚀 准备开始自动启动测试，是否继续？(y/n): " start_test

if [ "$start_test" != "y" ]; then
    echo "测试已取消"
    exit 0
fi

echo ""
echo "🎯 开始自动启动测试..."
echo "📝 日志将保存到 logs/auto_launch_test.log"
echo ""

# 运行测试
cd src
python auto_launch_test.py

# 检查测试结果
test_result=$?

echo ""
echo "================================"

if [ $test_result -eq 0 ]; then
    echo "✅ 自动启动测试完成"
else
    echo "❌ 自动启动测试出现问题"
fi

echo ""
echo "📊 查看结果："
echo "   - 测试日志: logs/auto_launch_test.log"
echo "   - 调试图像: data/debug_images/"
echo "   - 状态报告: data/status_report_*.json"

# 询问是否查看日志
read -p "📖 是否查看最新的测试日志？(y/n): " view_log

if [ "$view_log" = "y" ]; then
    echo ""
    echo "=== 最新测试日志 ==="
    tail -50 logs/auto_launch_test.log
fi

echo ""
echo "🎮 自动启动测试结束" 