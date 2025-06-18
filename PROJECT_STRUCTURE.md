# Mini Motorways AI自动化项目 - 项目结构

## 📁 整理后的项目结构

```
auto-mini-motorways/
├── 📋 项目文档
│   ├── README.md                     # 项目说明
│   ├── ACHIEVEMENT_SUMMARY.md        # 成就总结
│   ├── PROJECT_STRUCTURE.md          # 项目结构说明（本文件）
│   └── requirements.txt              # Python依赖
│
├── 🚀 启动脚本
│   ├── start_integrated_controller.sh # 一键启动脚本
│   ├── start_test.sh                 # 测试启动脚本
│   └── install.sh                    # 安装脚本
│
├── 🎯 核心代码 (src/core/)
│   ├── integrated_game_controller.py  # 🎮 集成版游戏控制器（主入口）
│   ├── game_capture_fixed.py         # 📸 修复版游戏捕获器
│   ├── ui_detector.py                # 🔍 UI元素检测器
│   ├── image_analyzer.py             # 🖼️  图像分析器
│   ├── game_controller.py            # 🎮 游戏控制器
│   ├── window_finder.py              # 🪟 窗口查找工具
│   └── config.py                     # ⚙️ 配置文件
│
├── 📊 数据目录 (data/)
│   ├── active/                       # 活跃数据
│   ├── archive/                      # 存档的调试数据
│   ├── screenshots/                  # 截图数据
│   └── analysis_reports/             # 分析报告
│
├── 📝 日志目录 (logs/)
│   └── auto_launch_test.log          # 日志文件
│
├── 📦 存档目录 (archive/)
│   ├── test_files/                   # 存档的测试文件
│   ├── debug_data/                   # 存档的调试数据
│   └── old_versions/                 # 旧版本文件
│
├── 🧹 清理工具
│   ├── cleanup_project.py            # 项目清理脚本
│   └── cleanup_report_*.json         # 清理报告
│
└── 🐍 Python环境
    └── venv/                         # 虚拟环境
```

## 🎯 核心文件说明

### 主要入口
- **`integrated_game_controller.py`** - 集成版游戏控制器
  - 整合所有修复的完整版本
  - 包含多显示器支持、鼠标移动、精确点击等功能
  - 这是您主要使用的文件

### 核心组件
- **`game_capture_fixed.py`** - 游戏画面捕获
  - 解决多显示器问题
  - 专门捕获游戏窗口而非全屏
  
- **`ui_detector.py`** - UI元素检测
  - 高精度按钮检测（98%置信度）
  - HSV颜色空间分析
  
- **`image_analyzer.py`** - 图像分析
  - 游戏状态识别
  - 画面内容分析
  
- **`game_controller.py`** - 游戏控制
  - 鼠标移动和点击
  - 窗口激活管理
  
- **`window_finder.py`** - 窗口管理
  - 游戏窗口查找
  - 坐标转换

## 🚀 使用方法

### 快速启动
```bash
# 一键启动集成控制器
./start_integrated_controller.sh
```

### 手动启动
```bash
# 激活虚拟环境
source venv/bin/activate

# 进入核心代码目录
cd src/core

# 运行主程序
python3 integrated_game_controller.py
```

## 📦 存档说明

### 测试文件存档 (archive/test_files/)
包含20个探索过程中的测试文件：
- 各种点击测试脚本
- 调试工具
- 实验性功能

### 调试数据存档 (data/archive/)
包含24个调试数据文件：
- 调试截图
- 分析报告
- 状态记录

这些文件都被安全保存，如果需要可以随时查看。

## 🎮 系统能力

### ✅ 已实现功能
- 游戏窗口自动查找和定位
- 高精度游戏画面捕获
- 主菜单状态识别
- 游玩按钮检测和点击（98%精度）
- 窗口激活和鼠标控制
- 完整的日志和调试系统

### 🔄 工作流程
```
游戏窗口查找 → 画面捕获 → 状态分析 → UI检测 → 坐标转换 → 鼠标控制 → 状态验证
```

## 📊 清理统计

根据最新的清理报告：
- ✅ **核心文件**: 7个（已整理到src/core/）
- 📦 **测试文件存档**: 20个（移动到archive/test_files/）
- 🗂️ **调试数据清理**: 24个（移动到data/archive/）
- 📁 **新建目录**: 8个（优化项目结构）

## 🎯 下一步开发

现在项目结构清晰，可以专注于第三阶段开发：
1. 城市选择界面识别
2. 地图选择功能
3. 游戏设置调整
4. 进入实际游戏玩法

所有核心功能都在`src/core/`目录中，便于维护和扩展。 