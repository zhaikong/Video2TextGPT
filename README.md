# VideoText Converter

一个基于 PyQt6 的视频转文字桌面应用，支持批量将视频转换为文本文档。

## 功能特点

- 支持批量导入视频文件
- 支持拖拽文件到界面
- 支持主流视频格式(mp4, avi, mkv等)
- 显示转换进度和状态
- 深色/浅色主题切换
- 系统托盘支持
- 可配置的转换参数

## 系统要求

- Python 3.8+
- FFmpeg
- CUDA (可选，用于GPU加速)

## 安装部署

1. 克隆仓库
```bash
git clone https://github.com/yourusername/videotext-converter.git
cd videotext-converter
```

2. 创建虚拟环境
```bash
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 安装 FFmpeg

Windows:
```bash
choco install ffmpeg
```

macOS:
```bash
brew install ffmpeg
```

Linux:
```bash
sudo apt update
sudo apt install ffmpeg
```

## 使用说明

1. 启动应用
```bash
python src/main.py
```

2. 添加视频文件
   - 点击"选择文件"按钮选择单个或多个视频文件
   - 点击"选择目录"按钮选择包含视频的文件夹
   - 直接将文件拖拽到应用窗口

3. 开始转换
   - 点击"开始转换"按钮开始处理
   - 可以随时暂停/继续/取消转换
   - 转换完成的文件将保存在配置的输出目录中

4. 设置选项
   - Whisper模型选择(tiny/base/small/medium/large)
   - 识别语言设置
   - 最大线程数
   - 输出目录设置
   - 主题切换
   - 系统托盘设置

## 项目结构

```
videotext_converter/
├── src/                    # 源代码目录
│   ├── gui/               # 图形界面相关
│   │   ├── main_window.py # 主窗口
│   │   ├── file_list.py   # 文件列表组件
│   │   ├── progress.py    # 进度展示组件
│   │   ├── status.py      # 状态展示组件
│   │   ├── theme.py       # 主题管理
│   │   └── settings.py    # 设置对话框
│   ├── core/              # 核心功能
│   │   ├── converter.py   # 转换管理
│   │   ├── extractor.py   # 音频提取
│   │   └── transcriber.py # 语音识别
│   └── utils/             # 工具类
│       ├── config.py      # 配置管理
│       └── logger.py      # 日志管理
```

## 技术架构

1. GUI层
   - 使用PyQt6构建用户界面
   - 采用组件化设计，将功能模块分离
   - 实现了深色/浅色主题支持
   - 使用信号槽机制处理事件

2. 核心层
   - 使用moviepy处理视频提取音频
   - 使用whisper进行语音识别
   - 多线程处理避免界面卡顿
   - 队列管理任务处理

3. 工具层
   - 配置管理支持JSON持久化
   - 日志系统记录运行状态
   - 异常处理机制

## 配置文件

配置文件位于 `~/.videotext/config.json`:

```json
{
    "output_dir": "~/Documents/VideoText",
    "whisper_model": "base",
    "language": "zh",
    "theme": "light",
    "max_threads": 2,
    "supported_formats": [".mp4", ".avi", ".mkv", ".mov", ".flv"]
}
```

## 日志文件

日志文件位于 `~/.videotext/logs/videotext.log`

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交改动
4. 发起 Pull Request

## 许可证

MIT License

## 更新日志

### v1.0.0
- 初始版本发布
- 基本功能实现：
  - 视频批量导入
  - 音频提取
  - 文本转写
  - 主题切换
  - 系统托盘
  - 配置管理



