#!/bin/bash

echo "🎮 Mini Motorways AI 项目安装脚本"
echo "=================================="
echo ""

# 检查Python版本
echo "🔍 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python 3.8或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python版本: $PYTHON_VERSION"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 未找到pip3，请先安装pip"
    exit 1
fi

echo "✅ pip3 已安装"
echo ""

# 创建虚拟环境（可选）
read -p "🤔 是否创建Python虚拟环境？(推荐) [y/N]: " create_venv

if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ 虚拟环境已创建并激活"
    echo "💡 下次使用前请运行: source venv/bin/activate"
    echo ""
fi

# 安装依赖
echo "📥 安装Python依赖包..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 依赖安装成功"
else
    echo "❌ 依赖安装失败，请检查网络连接或Python环境"
    exit 1
fi

echo ""

# 创建必要的目录
echo "📁 创建项目目录..."
mkdir -p data/screenshots
mkdir -p logs
echo "✅ 目录创建完成"

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 下一步操作："
echo "1. 打开Mini Motorways游戏"
echo "2. 运行测试: python3 src/capture_test.py"
echo "3. 首次运行时需要授权屏幕录制权限"
echo ""
echo "💡 如果创建了虚拟环境，请先运行: source venv/bin/activate"
echo ""
echo "🆘 如果遇到问题，请查看README.md文件" 