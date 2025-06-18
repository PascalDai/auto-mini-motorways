# Mini Motorways 自动化系统

这是一个用于自动化玩Mini Motorways游戏的系统。系统通过截图识别游戏状态，并与远程服务器通信获取决策指令。

## 功能特点

- 🎮 **自动游戏窗口识别**：自动查找并管理Mini Motorways游戏窗口
- 📸 **智能截图系统**：高效的屏幕截图和图像处理
- 🔍 **游戏状态识别**：识别游戏的不同阶段和UI元素
- 📝 **详细日志记录**：Markdown格式的可视化日志系统
- 🌐 **远程决策支持**：与远程AI服务器通信获取游戏策略
- ⚙️ **灵活配置管理**：YAML配置文件支持

## 项目结构

```
auto-mini-motorways/
├── src/                    # 源代码目录
│   ├── core/              # 核心功能模块
│   │   ├── window_manager.py    # 窗口管理
│   │   └── screenshot.py        # 截图管理
│   └── utils/             # 工具模块
│       ├── logger.py            # 日志记录
│       └── config.py            # 配置管理
├── logs/                  # 日志文件目录
│   └── session_log.md          # 会话日志
├── screenshots/           # 截图文件目录
├── config.yaml           # 配置文件
├── requirements.txt      # Python依赖
├── main.py              # 主启动脚本
└── README.md            # 项目说明
```

## 安装和使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动Mini Motorways游戏

确保Steam版本的Mini Motorways游戏已经启动并运行。

### 3. 运行系统

```bash
python main.py
```

### 4. 查看日志

系统运行后，可以通过以下方式查看日志：

- **Markdown日志**：打开 `logs/session_log.md` 查看详细的可视化日志
- **截图文件**：查看 `screenshots/` 目录下的截图文件

## 配置说明

编辑 `config.yaml` 文件来自定义系统行为：

```yaml
# 游戏窗口配置
game:
  window_title: "Mini Motorways"
  expected_resolution: [1920, 1080]

# 截图配置
screenshot:
  save_raw: true
  save_marked: true
  quality: 95

# 日志配置
logging:
  level: "INFO"
  keep_days: 7

# 远程服务器配置
remote_server:
  enabled: false
  url: "http://localhost:8000/api/decision"
  timeout: 5
```

## 日志系统

系统使用Markdown格式记录详细的运行日志，包括：

- ✅ 成功操作记录
- ❌ 错误信息记录
- ⚠️ 警告信息
- 📸 截图嵌入显示
- 🎯 游戏状态识别结果
- 🎮 操作执行记录
- 📊 统计信息

## 开发状态

### 已完成功能
- [x] 项目框架搭建
- [x] 配置管理系统
- [x] Markdown日志系统
- [x] 窗口管理器
- [x] 截图管理器
- [x] 基础测试功能

### 待开发功能
- [ ] 游戏状态识别器
- [ ] 图像处理和OCR
- [ ] 自动操作执行器
- [ ] 远程服务器通信
- [ ] 游戏策略决策接口

## 注意事项

1. **游戏分辨率**：建议使用1920x1080分辨率以获得最佳识别效果
2. **窗口状态**：确保游戏窗口不被遮挡，系统会自动激活窗口
3. **权限设置**：某些系统可能需要授予屏幕录制权限
4. **性能要求**：图像处理需要一定的CPU和内存资源

## 故障排除

### 找不到游戏窗口
- 确保Mini Motorways正在运行
- 检查游戏窗口标题是否正确
- 尝试调整 `config.yaml` 中的 `window_title` 设置

### 截图失败
- 检查屏幕录制权限
- 确保游戏窗口未被最小化
- 查看日志文件中的错误信息

### 日志查看问题
- 使用支持Markdown的编辑器查看日志
- 推荐使用VS Code、Typora等工具
- 图片路径为相对路径，确保在项目根目录查看

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

本项目仅供学习和研究使用。 