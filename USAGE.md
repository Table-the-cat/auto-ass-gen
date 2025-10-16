# 使用指南

## 快速开始

### 1. 准备工作

确保已安装以下依赖：

- Python 3.7+
- FFmpeg
- PyTorch
- 其他Python依赖（见 `requirements.txt`）

```bash
pip install -r requirements.txt
```

### 2. 准备输入文件

将你的视频或音频文件放入 `input/` 目录。

### 3. 修改配置文件

复制 `example_config.yaml` 并根据需要修改：

```bash
cp example_config.yaml my_config.yaml
```

编辑 `my_config.yaml`，至少需要修改：

```yaml
paths:
  input_file: "input/your_video.mp4"
  output_ass: "output/your_subtitle.ass"
```
如果提示找不到文件，改为绝对路径

### 4. 运行程序

**方法1：使用配置文件**

```bash
# Windows
run.bat -c my_config.yaml

# Linux/macOS
./run.sh -c my_config.yaml
```

**方法2：直接指定文件**

```bash
# Windows
run.bat -i input/video.mp4 -o output/subtitle.ass

# Linux/macOS
./run.sh -i input/video.mp4 -o output/subtitle.ass
```

**方法3：直接运行Python**

```bash
cd src
python main.py -i ../input/video.mp4 -o ../output/subtitle.ass
```

## 配置参数详解

### 路径配置 (paths)

```yaml
paths:
  input_file: "input/video.mp4"      # 输入文件
  output_wav: "output/audio.wav"     # 临时音频文件
  output_ass: "output/subtitle.ass"  # 输出字幕文件
```

### 音频配置 (audio)

```yaml
audio:
  sample_rate: 16000      # 采样率（Hz），建议16000
  ffmpeg_path: "ffmpeg"   # FFmpeg路径
```

### VAD配置 (vad)

```yaml
vad:
  use_onnx: true          # 使用ONNX模型（推荐）
  threshold: 0.5          # 语音检测阈值（0-1）
  min_speech_duration_ms: 250    # 最小语音长度（毫秒）
  max_speech_duration_s: .inf    # 最大语音长度（秒）
  min_silence_duration_ms: 100   # 最小静音长度（毫秒）
  speech_pad_ms: 30              # 语音片段填充（毫秒）
```

#### threshold 参数调整建议

- **检测到的语音太少**: 降低阈值（如 `0.3` 或 `0.4`）
- **检测到太多噪音**: 提高阈值（如 `0.6` 或 `0.7`）
- **默认值**: `0.5` 适用于大多数情况

### 字幕样式配置 (subtitle)

```yaml
subtitle:
  title: "我的字幕"
  resolution:
    width: 1920
    height: 1080
  style:
    fontname: "Microsoft YaHei"  # 字体名称
    fontsize: 56                 # 字体大小
    alignment: 2                 # 对齐方式（2=底部居中）
    # ... 更多样式参数
```

#### 对齐方式 (alignment)

使用小键盘布局：

```
7  8  9    (左上)  (上)  (右上)
4  5  6    (左中)  (中)  (右中)
1  2  3    (左下) (下中) (右下)
```

常用值：
- `2`: 底部居中（默认）
- `8`: 顶部居中
- `5`: 屏幕中央

## 常见问题

### Q: FFmpeg not found

**A**: 确保FFmpeg已安装并添加到系统PATH。

测试方法：
```bash
ffmpeg -version
```

如果不在PATH中，可以在配置文件中指定完整路径：
```yaml
audio:
  ffmpeg_path: "C:/ffmpeg/bin/ffmpeg.exe"  # Windows示例
```

### Q: 无法导入silero_vad

**A**: 确保已安装silero-vad包：

```bash
pip install silero-vad
```

或者从源码安装：
```bash
pip install git+https://github.com/snakers4/silero-vad.git
```

### Q: 未检测到语音

**A**: 尝试以下方法：

1. 降低 `threshold` 参数
2. 减小 `min_speech_duration_ms`
3. 检查输入文件是否包含音频轨道

### Q: 检测到太多噪音

**A**: 尝试以下方法：

1. 提高 `threshold` 参数
2. 增大 `min_speech_duration_ms`
3. 增大 `min_silence_duration_ms`

### Q: 生成的字幕没有文字

**A**: 这是正常的。本工具只生成时间轴，文字内容需要后续添加。可以：

1. 使用Aegisub等字幕编辑软件手动添加
2. 结合语音识别（ASR）工具自动添加
3. 导入已有文本逐行对应

## 高级用法

### 批量处理

创建批处理脚本：

```bash
# batch_process.sh
for video in input/*.mp4; do
    filename=$(basename "$video" .mp4)
    python src/main.py -i "$video" -o "output/${filename}.ass"
done
```

### 自定义Python脚本

```python
from src.config import load_config
from src.main import ASSGenerator

# 加载配置
config = load_config('my_config.yaml')

# 创建生成器
generator = ASSGenerator(config)

# 执行生成
success = generator.generate()
```

### 只提取音频

```python
from src.util import AudioExtractor

extractor = AudioExtractor()
extractor.extract_audio('input.mp4', 'output.wav', sample_rate=16000)
```

### 只进行VAD检测

```python
from src.vad import VADProcessor

vad = VADProcessor(use_onnx=True, threshold=0.5)
timestamps = vad.detect_speech('audio.wav')

for ts in timestamps:
    print(f"{ts['start']:.2f}s - {ts['end']:.2f}s")
```

## 工作流程示例

### 场景1：视频字幕制作

1. 生成时间轴：
   ```bash
   python src/main.py -i video.mp4 -o timeline.ass
   ```

2. 使用Aegisub打开 `timeline.ass`

3. 在每个时间轴上添加文字

4. 导出最终字幕

### 场景2：结合语音识别

1. 生成时间轴
2. 使用Whisper等工具生成文字
3. 将文字与时间轴对应
4. 生成完整字幕

## 性能优化

- **使用ONNX模型**: 比JIT模型快约2-3倍
- **调整VAD参数**: 减少不必要的片段检测
- **使用SSD存储**: 加快音频读写速度

## 输出格式

生成的ASS文件格式：

```
[Script Info]
Title: 自动生成字幕
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, ...
Style: Default,Microsoft YaHei,48,...

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.50,0:00:03.20,Default,,0,0,0,, 
Dialogue: 0,0:00:04.10,0:00:07.80,Default,,0,0,0,, 
```

每个 `Dialogue` 行代表一个语音片段，文本内容为空格。

