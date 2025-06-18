# Mini Motorways AI 自动化项目

## 项目目标
在本地Mac mini运行Mini Motorways游戏，通过计算机视觉识别游戏画面，将关键信息发送到服务器进行AI决策，最终实现游戏自动化并获得高分。

## 第一阶段：基础框架

### 功能列表
- [x] 游戏画面捕获
- [ ] 基础图像识别
- [ ] 本地-服务器通信
- [ ] 游戏控制

### 环境要求
- macOS 系统
- Python 3.8+
- Mini Motorways 游戏

### 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行画面捕获测试：
```bash
python src/capture_test.py
```

3. 打开Mini Motorways游戏，程序会自动捕获游戏画面

### 目录结构
```
auto-mini-motorways/
├── README.md                 # 项目说明
├── requirements.txt          # Python依赖
├── src/                     # 源代码
│   ├── capture_test.py      # 画面捕获测试
│   ├── game_capture.py      # 游戏画面捕获模块
│   └── config.py           # 配置文件
├── data/                   # 数据存储
│   └── screenshots/        # 截图存储
└── logs/                   # 日志文件
```

### 使用说明

1. **第一次运行**：程序会要求你授权屏幕录制权限
2. **测试步骤**：
   - 打开Mini Motorways游戏
   - 运行 `python src/capture_test.py`
   - 程序会每2秒截取一次游戏画面
   - 截图会保存在 `data/screenshots/` 目录中
3. **查看结果**：检查截图是否正确捕获了游戏画面

### 下一步计划
- 实现游戏元素识别（房子、公司、道路）
- 添加游戏状态分析
- 建立与服务器的通信 