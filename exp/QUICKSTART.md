# 快速开始指南

本指南帮助你快速运行VAD参数优化实验。

## 步骤1: 安装依赖

```bash
cd exp
pip install -r requirements.txt
```

或者单独安装：

```bash
pip install numpy matplotlib tqdm torch torchaudio soundfile silero-vad
```

## 步骤2: 准备数据

### 方式A: 使用现有数据

如果你已有视频和字幕文件，请将它们放入 `exp/data/` 目录：

```bash
exp/data/
├── live_show_001.mp4
├── live_show_001.ass
├── interview_001.mkv
├── interview_001.ass
└── ...
```

**重要**: 
- 每个视频文件必须有同名的字幕文件（推荐.ass）
- 文件名中包含类别关键词（live, interview, radio, anime）
- 音频会自动从视频中提取，无需手动处理
- 支持的视频格式：.mp4, .mkv, .avi, .mov, .flv, .wmv

### 方式B: 准备测试数据

如果只是测试功能，可以准备少量样本（例如3-5个，每个5-10分钟）：

```bash
# 直接将视频和字幕文件放入data目录
cp your_video.mp4 exp/data/live_test_001.mp4
cp your_subtitle.ass exp/data/live_test_001.ass

# 音频会自动提取，无需手动处理
```

## 步骤3: 运行实验

### 选项A: 运行所有实验

```bash
python exp/run_all_experiments.py
```

### 选项B: 只运行特定实验

```bash
# 只运行实验2（最快，不需要VAD处理）
python exp/run_all_experiments.py --experiments 2

# 运行实验2和3
python exp/run_all_experiments.py --experiments 2 3
```

### 选项C: 单独运行某个实验

```bash
# 实验1: threshold优化（耗时最长）
python exp/exp1_threshold.py

# 实验2: min_silence分析（最快）
python exp/exp2_min_silence.py

# 实验3: merge_min_gap分析
python exp/exp3_merge_min_gap.py
```

## 步骤4: 查看结果

结果保存在 `exp/results/` 目录：

```bash
exp/results/
├── exp1_threshold_results.json      # 实验1数据
├── exp1_threshold_plot.png          # 实验1图表
├── exp2_min_silence_results.json    # 实验2数据
├── exp2_min_silence_plot.png        # 实验2图表
├── exp3_merge_min_gap_results.json  # 实验3数据
└── exp3_merge_min_gap_plot.png      # 实验3图表
```

### 查看JSON结果

```bash
# Windows
type exp\results\exp2_min_silence_results.json

# Linux/Mac
cat exp/results/exp2_min_silence_results.json
```

### 查看图表

直接打开PNG文件查看可视化结果。

## 步骤5: 应用结果

根据实验输出更新你的配置文件：

```yaml
# src/config/default_config.yaml

vad:
  threshold: 0.5              # 来自实验1
  min_silence_duration_ms: 800  # 来自实验2

subtitle:
  merge_min_gap: 0.3          # 来自实验3
```

## 最小化测试运行

如果你只想快速测试系统是否正常工作：

### 1. 准备1-2个样本

```bash
exp/data/
├── test_001.mp4      # 视频文件
└── test_001.ass      # 字幕文件
```

### 2. 只运行实验2（最快）

```bash
python exp/exp2_min_silence.py --data_dir exp/data --results_dir exp/results
```

### 3. 检查输出

```bash
# 应该生成：
exp/results/exp2_min_silence_results.json
exp/results/exp2_min_silence_plot.png
```

## 常见问题

### Q: 运行很慢怎么办？

**A**: 
1. 先用少量数据测试（3-5个样本）
2. 只运行实验2（不需要VAD处理）
3. 使用GPU加速（如果有）
4. 减小threshold范围（实验1）

### Q: 提示"未找到数据"？

**A**: 检查：
1. data目录中是否有.wav文件
2. 每个.wav是否有对应的.ass或.srt文件
3. 文件名是否完全匹配（不含扩展名）

### Q: 实验1运行时间？

**A**: 取决于数据量：
- 10小时数据：约1-2小时
- 100小时数据：约10-20小时
- 建议先用小数据集测试

### Q: 可以跳过实验1吗？

**A**: 可以！实验2和3不依赖实验1。你可以：
```bash
# 只运行实验2和3
python exp/run_all_experiments.py --experiments 2 3
```

### Q: 实验失败怎么办？

**A**: 查看错误信息：
1. 检查依赖是否安装完整
2. 检查数据文件格式
3. 查看完整的错误堆栈
4. 尝试单独运行某个实验定位问题

## 进阶选项

### 自定义参数

```bash
# 使用自定义百分位数
python exp/run_all_experiments.py --percentile 10

# 指定数据和结果目录
python exp/run_all_experiments.py \
    --data_dir /path/to/data \
    --results_dir /path/to/results

# 实验3使用特定threshold
python exp/exp3_merge_min_gap.py --threshold 0.6
```

### 批处理模式

如果数据量很大，可以分批处理：

```bash
# 创建子目录
mkdir exp/data_batch1
mkdir exp/data_batch2

# 分批运行
python exp/run_all_experiments.py --data_dir exp/data_batch1
python exp/run_all_experiments.py --data_dir exp/data_batch2
```

## 下一步

- 阅读详细文档: `exp/README.md`
- 了解数据准备: `exp/data/README.md`
- 查看代码实现: `exp/exp*.py`

## 获取帮助

运行以下命令查看完整参数说明：

```bash
python exp/run_all_experiments.py --help
python exp/exp1_threshold.py --help
python exp/exp2_min_silence.py --help
python exp/exp3_merge_min_gap.py --help
```

