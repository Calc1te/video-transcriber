# Video Translator

A video translator (that cannot translate video yet)

## 功能特点

- 🎥 支持多种视频格式
- 🎯 使用 Whisper 模型进行语音识别
- 📝 自动生成 ASS 格式字幕文件
- 🎨 支持自定义字幕样式
- 💻 支持 CPU 和 CUDA 加速

## 安装要求

- Python 3.10 或更高版本
- FFmpeg（用于音频提取）
- CUDA（可选，用于 GPU 加速）

## 安装

点击右上角Code -> Download Zip

或

```bash

# 从源码安装
git clone https://github.com/yourusername/video_translator.git
cd video_translator
pip install -e .
```



## 使用方式

### 方式 1: Web 界面

首先你得有个python

[windows download](https://www.python.org/downloads/windows/)

[macOS download](https://www.python.org/downloads/macos/)

#### Windows 用户
```cmd
双击运行 run_web.bat 文件
```

#### macOS/Linux 用户
```bash
bash run_web.sh
```

#### 或使用 Python 命令
```bash
python -m video_translator.run_web_server
```

然后打开浏览器访问：`http://127.0.0.1:5000`


### 方式 2: 命令行工具

```bash
video-translator translate your_video.mp4 --model-size base --device cuda
```

### 方式 3: Python 库

```python
from video_translator import VideoTranslator, Device

translator = VideoTranslator('video.mp4', 'large-v3', device=Device.cpu)
translator.singleVideoPipeline()
```

---

## 快速开始

以下是一个基本的使用示例：

```python
from video_translator import VideoTranslator, Device, AssStyle

# 创建翻译器实例
translator = VideoTranslator(
    vid_path="your_video.mp4",
    model_size="base",
    device=Device.cuda  # 或 Device.cpu
)

# 设置工作环境
translator.env_setup()

# 开始处理视频
translator.get_audio_stream()
translator.whisper_transcription()
# 自定义字幕样式（可选）
style = AssStyle(
    name="Custom",
    font="Arial",
    font_size=48,
    primary_color=(255, 255, 255, 255)  # 白色
)
generate_subtitle([style])
compress_subtitle()

# 或者直接使用打包好的方法
vidTr = VideoTranslator('input.mp4','large-v3')
vidTr.singleVideoPipeline(translation = False)
```

## 主要组件

- `VideoTranslator`: 核心翻译类，处理视频转换和字幕生成
- `Device`: 设备选择枚举类（CPU/CUDA）
- `AssStyle`: 字幕样式配置类
- `AssGenerator`: ASS 字幕生成器

## 依赖项

- av==16.0.0
- faster-whisper==1.2.0
- onnxruntime==1.23.1
- 其他依赖请参见 pyproject.toml

## 许可证

MIT License

欢迎提交 Issues 和 Pull Requests！

## 更新日志

### 0.1.0

- 初始版本发布
- 支持 ASS 字幕生成

## 作者

[Calc1te](https://github.com/Calc1te)

## 鸣谢

- [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- [FFmpeg](https://ffmpeg.org/)
