# 自动生成ASS字幕文件

基于语音活动检测（VAD）自动生成ASS格式字幕文件的Python工具。

## 功能特点

- ✅ 支持多种视频/音频格式输入（通过FFmpeg）
- ✅ 基于Silero VAD进行高精度语音检测
- ✅ 自动生成标准ASS字幕文件
- ✅ 支持灵活的配置文件
- ✅ 命令行参数支持

## 项目结构

```
auto-ass-gen/
├── src/
│   ├── vad/                  # 语音活动识别模块
│   │   ├── __init__.py
│   │   └── vad_processor.py
│   ├── util/                 # 工具类
│   │   ├── __init__.py
│   │   ├── audio_extractor.py  # 音频提取
│   │   ├── time_converter.py   # 时间格式转换
│   │   └── file_io.py          # 文件IO操作
│   ├── config/               # 配置文件
│   │   ├── __init__.py
│   │   ├── config_loader.py
│   │   └── default_config.yaml
│   └── main.py               # 主程序入口
├── requirements.txt          # Python依赖
└── README.md
```

## 安装

详细的安装步骤请参考 [INSTALL.md](INSTALL.md)。

**快速安装：**

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装FFmpeg（根据你的操作系统）
# Windows: 从 https://ffmpeg.org/download.html 下载
# Linux: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
```


## 使用方法

### 基本使用

```bash
cd src
python main.py
```

这将使用 `src/config/default_config.yaml` 中的默认配置。

### 使用自定义配置文件

```bash
python main.py -c my_config.yaml
```

### 直接指定输入输出文件

```bash
python main.py -i input_video.mp4 -o output_subtitle.ass
```

### 完整命令行参数

```bash
python main.py -c config.yaml -i input.mp4 -o output.ass -w temp_audio.wav
```

参数说明：
- `-c, --config`: 配置文件路径
- `-i, --input`: 输入视频/音频文件
- `-o, --output`: 输出ASS字幕文件
- `-w, --wav`: 临时WAV音频文件路径

## 配置文件

配置文件支持YAML和JSON格式。示例配置：

```yaml
paths:
  # 如果paths未生效，尝试使用绝对路径
  input_file: "input/video.mp4"
  output_wav: "output/audio.wav"
  output_ass: "output/subtitle.ass"

audio:
  sample_rate: 16000
  ffmpeg_path: "ffmpeg"

vad:
  use_onnx: true
  threshold: 0.5
  min_speech_duration_ms: 250
  max_speech_duration_s: .inf
  min_silence_duration_ms: 100
  speech_pad_ms: 30

subtitle:
  title: "自动生成字幕"
  resolution:
    width: 1280
    height: 720
  style:
    fontname: "Microsoft YaHei"
    fontsize: 48
    # ... 更多样式配置
```

### 关键参数说明

#### threshold
语音检测阈值，越大越严格

#### min_speech_duration_ms:
最短说话时长（毫秒），小于该时长的片段，即使被判定为在说话也会被忽略

#### max_speech_duration_s
最长说话时长（秒），大于该时长的片段，会在下一个静音片段时被分割
当一个片段超过该配置的值时，程序在做分割判定时会降低最短静音时长的要求，即使静音片段时长小于min_silence_duration_ms的值也可能被分割

#### min_silence_duration_ms
最短静音时长（毫秒），大于该值的静音片段（即说话的停顿）才会被分割为不同的字幕
如果设为1000ms，即一秒：
``` text
[说话8秒] → [停顿0.5秒] → [说话7秒] → [停顿0.6秒] → [说话5秒]
            ❌ 忽略（<1秒）          ❌ 忽略（<1秒）
```
结果：生成一个20秒的片段

## 工作流程

1. **音频提取**: 使用FFmpeg将视频/音频文件转换为16kHz采样率的WAV文件
2. **语音检测**: 使用Silero VAD检测语音活动片段
3. **ASS生成**: 将检测到的时间戳转换为ASS格式并保存

## ASS文件格式

生成的ASS文件包含：

- **[Script Info]**: 脚本信息（标题、分辨率等）
- **[V4+ Styles]**: 样式定义（字体、颜色、位置等）
- **[Events]**: 字幕事件（时间轴和内容）

时间格式: `H:MM:SS.ss` (小时:分钟:秒.百分之一秒)

## 注意事项

1. 输入文件必须包含音频轨道
2. Silero VAD要求音频采样率为16kHz或8kHz
3. 生成的字幕只包含时间轴，文本内容为空格（需要后续手动或自动添加）
4. 建议先在小文件上测试配置参数

## 故障排除

### FFmpeg not found
确保FFmpeg已安装并添加到系统PATH，或在配置文件中指定完整路径。

### 无法导入silero_vad
确保已安装silero-vad包：
```bash
pip install silero-vad
```

### torchaudio版本兼容性错误

如果遇到音频读取相关错误（如 `list_audio_backends` 或 `torchcodec`），请安装soundfile：

```bash
pip install soundfile
```

**重要：** 本项目使用 soundfile 直接读取音频，绕过了 torchaudio 的后端问题。确保soundfile已正确安装。

Windows用户如果遇到问题，可能需要：
```bash
pip install soundfile --force-reinstall
```

### 未检测到语音
尝试调整配置中的 `threshold` 参数（降低值可以检测到更多语音）。

## 许可证

本项目基于Silero VAD开发，请遵守相关许可证要求。

## 参考

- [Silero VAD](https://github.com/snakers4/silero-vad)
- [ASS字幕格式说明](http://www.tcax.org/docs/ass-specs.htm)

