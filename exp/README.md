# VAD参数优化实验

本目录包含用于优化Silero VAD和字幕生成参数的实验代码。

## 目录结构

```
exp/
├── README.md                    # 本文件
├── __init__.py                 # 模块初始化
├── data/                       # 数据目录（需要手动准备）
│   ├── live_sample1.wav       # 音频文件
│   ├── live_sample1.ass       # 对应的字幕文件
│   ├── interview_sample1.wav
│   ├── interview_sample1.srt
│   └── ...
├── results/                    # 实验结果输出目录
│   ├── exp1_threshold_results.json
│   ├── exp1_threshold_plot.png
│   ├── exp2_min_silence_results.json
│   ├── exp2_min_silence_plot.png
│   ├── exp3_merge_min_gap_results.json
│   └── exp3_merge_min_gap_plot.png
├── subtitle_parser.py          # 字幕文件解析器
├── vad_analyzer.py             # VAD分析器
├── metrics.py                  # 评估指标计算
├── exp1_threshold.py           # 实验1：threshold优化
├── exp2_min_silence.py         # 实验2：min_silence_duration_ms分析
├── exp3_merge_min_gap.py       # 实验3：merge_min_gap分析
└── run_all_experiments.py      # 运行所有实验
```

## 实验说明

### 实验1: threshold参数优化

**目标**: 找到使F1 Score最大的最优threshold值

**方法**:
1. 使用真实字幕文件作为Ground Truth
2. 遍历threshold值 [0.20, 0.25, 0.30, ..., 0.60]（步长0.05）
3. 对每个threshold，运行VAD并计算与真实字幕的F1 Score
4. 选择F1 Score最大的threshold作为最优值

**输出**:
- `exp1_threshold_results.json`: 详细结果数据
- `exp1_threshold_plot.png`: F1/Precision/Recall曲线图

### 实验2: min_silence_duration_ms参数分析

**目标**: 确定合适的最小静音时长

**方法**:
1. 从真实字幕中提取所有相邻字幕的间隔
2. 过滤掉0值和重复值
3. 计算前5%分位数作为参考值

**输出**:
- `exp2_min_silence_results.json`: 统计结果
- `exp2_min_silence_plot.png`: 间隔分布直方图和分类箱线图

### 实验3: merge_min_gap参数分析

**目标**: 确定合适的最小合并间隔

**方法**:
1. 找到真实字幕中首尾相连的点（tolerance ≤ 0.05秒）
2. 在VAD生成的时间戳中，搜索这些连接点附近的间隔
3. 收集这些间隔值，计算前5%分位数

**输出**:
- `exp3_merge_min_gap_results.json`: 统计结果
- `exp3_merge_min_gap_plot.png`: 间隔分布图

## 数据准备

### 数据要求

建议准备以下类型的数据：
- **Live直播**: 40-50小时
- **访谈**: 30-40小时
- **电台**: 10-20小时
- **动画** (参考): 5-10小时

**总计**: 约100小时视频

### 数据格式

每个样本需要包含：
1. **视频文件**: 支持 `.mp4`, `.mkv`, `.avi`, `.mov`, `.flv`, `.wmv`
2. **字幕文件**: `.ass` 格式（推荐），与视频文件同名
3. **音频提取**: 自动完成，无需手动处理

示例：
```
exp/data/
├── live_show_001.mp4
├── live_show_001.ass
├── interview_2024_01.mkv
├── interview_2024_01.ass
└── ...
```

### 命名规范

文件名中包含类别关键词以便自动分类：
- Live: 文件名包含 `live`
- 访谈: 文件名包含 `interview` 或 `访谈`
- 电台: 文件名包含 `radio` 或 `电台`
- 动画: 文件名包含 `anime` 或 `动画`

## 运行实验

### 安装依赖

```bash
pip install numpy matplotlib tqdm silero-vad torch torchaudio soundfile
```

### 运行单个实验

```bash
# 实验1: threshold优化
python exp/exp1_threshold.py --data_dir exp/data --results_dir exp/results

# 实验2: min_silence分析
python exp/exp2_min_silence.py --data_dir exp/data --results_dir exp/results --percentile 5

# 实验3: merge_min_gap分析
python exp/exp3_merge_min_gap.py --data_dir exp/data --results_dir exp/results --threshold 0.5 --percentile 5
```

### 运行所有实验

```bash
python exp/run_all_experiments.py --data_dir exp/data --results_dir exp/results --percentile 5
```

### 运行指定实验

```bash
# 只运行实验1和2
python exp/run_all_experiments.py --experiments 1 2

# 只运行实验3
python exp/run_all_experiments.py --experiments 3
```

## 参数说明

### 通用参数
- `--data_dir`: 数据目录路径 (默认: `exp/data`)
- `--results_dir`: 结果输出目录 (默认: `exp/results`)
- `--percentile`: 百分位数，用于计算参考值 (默认: 5.0)

### 实验1特定参数
- 无额外参数

### 实验2特定参数
- 无额外参数

### 实验3特定参数
- `--threshold`: VAD阈值 (默认: 0.5，建议使用实验1的结果)

## 结果解读

### 实验1结果

```json
{
  "overall": {
    "best_threshold": 0.5,
    "best_f1": 0.823
  },
  "per_threshold": {
    "0.5": {
      "avg_f1": 0.823,
      "avg_precision": 0.856,
      "avg_recall": 0.792
    }
  }
}
```

- **best_threshold**: 推荐使用的threshold值
- **best_f1**: 该threshold下的F1 Score

### 实验2结果

```json
{
  "overall": {
    "percentile_value": 0.8,
    "mean": 2.5,
    "median": 1.8
  }
}
```

- **percentile_value**: 推荐的min_silence_duration_ms (秒)
- 建议设置为: `percentile_value * 1000` (毫秒)

### 实验3结果

```json
{
  "overall": {
    "percentile_value": 0.3,
    "mean": 0.8,
    "median": 0.5
  }
}
```

- **percentile_value**: 推荐的merge_min_gap (秒)
- 直接使用该值作为配置参数

## 应用建议

根据实验结果更新配置文件：

```yaml
vad:
  threshold: 0.5              # 使用实验1的结果
  min_silence_duration_ms: 800  # 使用实验2的结果
  
subtitle:
  merge_min_gap: 0.3          # 使用实验3的结果
```

## 注意事项

1. **数据质量**: 确保字幕文件准确标注了语音起止时间
2. **数据多样性**: 包含不同类型的音频以提高参数的泛化性
3. **计算资源**: 实验1需要较长时间，建议使用GPU加速
4. **结果验证**: 建议在新数据上验证优化后的参数效果

## 故障排除

### 问题1: 未找到数据文件

**原因**: data目录为空或文件格式不正确

**解决**: 确保音频和字幕文件已正确放置在data目录中

### 问题2: Silero VAD不可用

**原因**: 未安装silero-vad

**解决**: 
```bash
pip install silero-vad
```

### 问题3: 内存不足

**原因**: 处理大量音频文件

**解决**: 
- 减少单次处理的数据量
- 使用更大内存的机器
- 分批运行实验

## 扩展实验

### 自定义threshold范围

修改 `exp1_threshold.py` 中的 `threshold_range`:

```python
threshold_range = np.arange(0.3, 0.7, 0.05).tolist()
```

### 自定义IoU阈值

在运行实验时调整匹配标准:

```python
experiment.run_experiment(iou_threshold=0.3)
```

### 分析其他参数

可以参考现有实验代码，添加新的实验来分析其他参数，如：
- `min_speech_duration_ms`
- `max_speech_duration_s`
- `speech_pad_ms`

## 参考资料

- [Silero VAD](https://github.com/snakers4/silero-vad)
- [ASS字幕格式规范](http://www.tcax.org/docs/ass-specs.htm)

