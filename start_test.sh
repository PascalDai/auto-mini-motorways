#!/bin/bash

echo "🎮 Mini Motorways AI - 快速测试启动"
echo "===================================="
echo ""

# 检查虚拟环境
if [ -d "venv" ]; then
    echo "🔄 激活虚拟环境..."
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
    echo ""
fi

# 检查依赖是否安装
echo "🔍 检查依赖..."
python3 -c "import pyautogui, PIL" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 依赖检查通过"
else
    echo "❌ 依赖缺失，请先运行: ./install.sh"
    exit 1
fi

echo ""
echo "🚀 启动画面捕获测试..."
echo ""

# 运行测试
python3 src/capture_test.py 