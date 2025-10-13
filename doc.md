# VideoTranslator 文档

## 类说明

### Device 枚举

```python
class Device(Enum):
    cuda = 'cuda'  # GPU 加速
    cpu = 'cpu'    # CPU 处理
```

### VideoTranslator 类

#### 初始化参数

```python
def __init__(self, vid_path: str|Path, model_size: str, device: Device = Device.cpu, 
             compute_type: str|None = None, verbose: bool = False)
```

- `vid_path`: 视频文件路径
- `model_size`: Whisper 模型大小 (如: "base", "small", "medium", "large")
- `device`: 运行设备，CPU 或 CUDA
- `compute_type`: 计算类型，自动选择或手动指定
- `verbose`: 是否启用详细日志

#### 主要方法

##### `env_setup(dir: Path | None = None)`

设置工作目录结构，创建必要的文件夹：

- `wav/` - 存放音频文件
- `ass/` - 存放字幕文件  
- `out/` - 存放输出视频

##### `get_audio_stream()`

使用 FFmpeg 从视频中提取音频，保存为 WAV 格式。

##### `get_resolution()`

获取视频分辨率信息。

##### `whisper_transcription()`

使用 Whisper 模型进行语音识别，返回转录结果列表。

##### `split_transcription()`

将转录结果保存为 JSON 文件，便于手动翻译。

##### `load_from_translation_file(translation_file: Path) -> bool`

从翻译文件恢复工作状态。

##### `add_translation_to_subtitle()`

将翻译内容添加到字幕文本中。

##### `generate_subtitle(styles: List[AssStyle] | None = None)`

生成 ASS 格式字幕文件。

##### `compress_subtitle()`

将字幕合成到视频中，生成最终输出视频。

##### `singleVideoPipeline(manual_translate: bool = False, translation_file: Path | None = None)`

完整的处理流水线：

- 如果提供翻译文件，直接恢复状态并生成字幕
- 如果启用手动翻译，生成转录文件供人工翻译
- 否则执行完整的自动处理流程

## 使用示例

### 基本用法

```python
from video_translator import VideoTranslator, Device

# 初始化翻译器
translator = VideoTranslator(
    vid_path="video.mp4",
    model_size="base",
    device=Device.cuda,
    verbose=True
)

# 执行完整流程
translator.singleVideoPipeline()
```

### 手动翻译工作流

```python
# 第一步：生成转录文件
translator.singleVideoPipeline(manual_translate=True)

# 手动编辑生成的 JSON 文件中的翻译字段

# 第二步：使用翻译文件生成字幕
translator.singleVideoPipeline(translation_file="path/to/translation.json")
```

## 输出文件结构

```
工作目录/
├── wav/
│   └── {视频名}_audio.wav          # 提取的音频
├── ass/
│   ├── transcription_{视频名}.json # 转录和翻译数据
│   └── {视频名}.ass               # 生成的字幕文件
└── out/
    └── w_sub_{视频名}             # 带字幕的输出视频
```

## 依赖项

- `faster-whisper`: 语音识别引擎
- `ffmpeg`: 音视频处理工具
- `ass_subtitle_generator`: 字幕生成模块（自定义）
- `utils`: 工具函数模块（自定义）

## 注意事项

1. 确保系统已安装 FFmpeg
2. 首次使用时会下载指定的 Whisper 模型
3. 手动翻译时需要编辑 JSON 文件中的 "translation" 字段
4. GPU 使用需要配置正确的 CUDA 环境