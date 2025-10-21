# 实验数据目录

此目录用于存放实验所需的视频和字幕文件。

## 数据准备指南

### 1. 数据要求

#### 总体要求
- **总时长**: 约100小时
- **格式**: 视频文件 + ASS字幕
- **注意**: 音频会自动从视频中提取，无需手动处理

#### 数据构成
- **Live直播**: 40-50小时
- **访谈节目**: 30-40小时
- **电台广播**: 10-20小时
- **动画片段** (参考数据): 5-10小时

### 2. 文件命名规范

为了自动识别数据类别，请在文件名中包含相应关键词：

| 类别 | 关键词 | 示例文件名 |
|-----|--------|-----------|
| Live直播 | `live` | `live_show_2024_01.wav` |
| 访谈 | `interview` 或 `访谈` | `interview_celebrity.wav` |
| 电台 | `radio` 或 `电台` | `radio_morning_show.wav` |
| 动画 | `anime` 或 `动画` | `anime_episode_01.wav` |

### 3. 文件配对

每个视频文件必须有对应的字幕文件，且文件名（不含扩展名）必须相同：

```
✅ 正确示例:
live_show_001.mp4
live_show_001.ass

interview_2024.mkv
interview_2024.ass

❌ 错误示例:
live_show_001.mp4
live_show_001_subtitle.ass  # 文件名不匹配

❌ 不推荐（但支持）:
interview_2024.mp4
interview_2024.srt  # SRT格式可用但推荐ASS
```

### 4. 目录结构示例

```
exp/data/
├── README.md                        # 本文件
├── live_show_2024_01_15.mp4        # Live直播样本
├── live_show_2024_01_15.ass
├── live_concert_highlights.mkv
├── live_concert_highlights.ass
├── interview_tech_ceo.mp4          # 访谈样本
├── interview_tech_ceo.ass
├── interview_actress_2024.avi
├── interview_actress_2024.ass
├── radio_morning_news.mp4          # 电台样本
├── radio_morning_news.ass
├── radio_talk_show_ep01.flv
├── radio_talk_show_ep01.ass
├── anime_episode_01.mp4            # 动画样本
├── anime_episode_01.ass
└── anime_movie_scene.mkv
    anime_movie_scene.ass
```

**支持的视频格式**: .mp4, .mkv, .avi, .mov, .flv, .wmv

### 5. 数据来源建议

#### 5.1 获取视频
- 下载直播/访谈/电台节目视频
- 录制直播视频
- 使用公开视频数据集

#### 5.2 获取字幕
- 专业字幕组制作的ASS字幕（推荐）
- 官方字幕文件
- 人工标注的时间轴字幕

**重要**: 
- 字幕的时间戳必须准确，这是实验的基准！
- 推荐使用ASS格式（更精确的时间戳）
- 音频会自动从视频中提取，无需手动处理

### 6. 音频处理（自动）

实验程序会自动从视频文件中提取音频：
- 自动转换为16kHz WAV格式
- 提取的音频保存在 `exp/results/temp_audio/` 目录
- 支持多种视频格式
- 使用FFmpeg进行提取（需要配置FFmpeg路径）

**无需手动处理音频！**

### 7. 字幕文件要求

#### ASS格式示例
```
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.50,0:00:03.20,Default,,0,0,0,,这是一句话
Dialogue: 0,0:00:03.80,0:00:06.50,Default,,0,0,0,,这是另一句话
```

#### SRT格式示例
```
1
00:00:01,500 --> 00:00:03,200
这是一句话

2
00:00:03,800 --> 00:00:06,500
这是另一句话
```

### 8. 数据质量检查

准备数据时请检查：

- [ ] 视频文件可以正常播放
- [ ] 字幕文件可以正常解析（推荐使用Aegisub等工具验证）
- [ ] 视频和字幕文件名匹配
- [ ] 字幕时间戳与视频音轨同步
- [ ] 文件名包含正确的类别关键词
- [ ] 字幕格式为ASS（推荐）或SRT

### 9. 快速验证脚本

创建 `check_data.py` 来验证数据：

```python
from pathlib import Path

data_dir = Path('exp/data')

# 支持的视频格式
video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']

# 查找所有视频文件
video_files = [f for f in data_dir.iterdir() 
               if f.suffix.lower() in video_extensions]
print(f"找到 {len(video_files)} 个视频文件\n")

# 检查是否有对应的字幕
for video in video_files:
    subtitle = None
    for ext in ['.ass', '.srt']:
        sub_file = video.with_suffix(ext)
        if sub_file.exists():
            subtitle = sub_file
            break
    
    if subtitle:
        print(f"✓ {video.name:40s} -> {subtitle.name}")
    else:
        print(f"✗ {video.name:40s} -> 缺少字幕文件")
```

### 10. 示例数据集

如果没有现成数据，可以考虑使用以下公开数据集：

- **Common Voice**: Mozilla的语音数据集
- **LibriSpeech**: 英文有声书数据集
- **AISHELL**: 中文语音数据集
- **字幕组资源**: 专业制作的字幕文件

**注意**: 使用公开数据集时请遵守其使用许可。

### 11. 数据隐私

如果使用包含个人信息的数据：

- 确保有权使用该数据
- 考虑数据脱敏处理
- 不要公开分享未授权的数据
- 遵守数据保护法规

### 12. 常见问题

#### Q: 视频长度有要求吗？
A: 建议单个文件5-30分钟，便于处理。总时长达到100小时即可。

#### Q: 必须是中文数据吗？
A: 不必须，Silero VAD支持多语言，字幕语言不影响VAD性能。

#### Q: 可以使用自动生成的字幕吗？
A: 不推荐。自动生成的字幕时间戳可能不准确，会影响实验结果。必须使用人工标注或专业制作的字幕。

#### Q: 数据分布不均怎么办？
A: 尽量按建议比例，但如果某类数据难以获取，可以适当调整。

#### Q: 必须提供WAV音频文件吗？
A: 不需要！实验程序会自动从视频中提取音频。只需提供视频文件和字幕文件即可。

#### Q: 为什么推荐ASS格式而不是SRT？
A: ASS格式支持更精确的时间戳（百分之一秒），而SRT是毫秒。对于VAD评估，ASS更准确。

#### Q: 需要配置FFmpeg吗？
A: 是的，需要安装FFmpeg并确保可以在命令行中调用，或在实验脚本中指定FFmpeg路径。

## 开始实验

数据准备完成后，运行：

```bash
python exp/run_all_experiments.py --data_dir exp/data --results_dir exp/results
```

