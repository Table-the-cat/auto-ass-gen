"""
实验3: 分析merge_min_gap参数
通过对比真实字幕中的首尾相连点和VAD生成的间隔，确定合适的最小间隔

实验逻辑说明：
1. 从真实字幕中找到"首尾相连"的点（即一个字幕结束，下一个字幕紧接着开始）
2. 使用VAD生成语音片段（不调用pre_process，保持原始间隔）
3. 在VAD结果中查找对应位置的实际间隔
4. 分析这些间隔的分布，确定合适的merge_min_gap值

注意：此实验不使用pre_process，因为我们需要分析VAD的原始间隔来决定merge_min_gap参数
"""
import sys
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from subtitle_parser import SubtitleParser
from vad_analyzer import VADAnalyzer, SILERO_AVAILABLE, extract_audio_from_video


class MergeMinGapExperiment:
    """merge_min_gap参数分析实验"""
    
    def __init__(self, data_dir: str, results_dir: str, ffmpeg_path: str = None):
        """
        初始化实验
        
        Args:
            data_dir: 数据目录
            results_dir: 结果输出目录
            ffmpeg_path: FFmpeg可执行文件路径，如果为None则尝试从配置文件读取
        """
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        if not SILERO_AVAILABLE:
            raise ImportError("需要安装Silero VAD")
        
        self.vad_analyzer = VADAnalyzer(use_onnx=True)
        self.parser = SubtitleParser()
        
        # 尝试从主配置文件读取ffmpeg_path
        if ffmpeg_path is None:
            try:
                from config import load_config
                main_config = load_config()
                self.ffmpeg_path = main_config.ffmpeg_path
            except:
                self.ffmpeg_path = "ffmpeg"  # 回退到默认值
        else:
            self.ffmpeg_path = ffmpeg_path if ffmpeg_path else "ffmpeg"
    
    def run_experiment(self, threshold: float = 0.5,
                      min_speech_duration_ms: int = 250,
                      max_speech_duration_s: float = 10.0,
                      min_silence_duration_ms: int = 1000,
                      search_window: float = 0.5,
                      percentile: float = 5.0,
                      ffmpeg_path: str = None) -> dict:
        """
        运行实验
        
        Args:
            threshold: VAD阈值
            min_speech_duration_ms: 最小语音持续时间
            max_speech_duration_s: 最大语音持续时间
            min_silence_duration_ms: 最小静音时续时间
            search_window: 搜索窗口大小（秒）
            percentile: 要计算的百分位数
            ffmpeg_path: FFmpeg可执行文件路径，如果为None则使用初始化时的路径
            
        Returns:
            dict: 实验结果
        """
        # 如果没有提供ffmpeg_path，使用实例的ffmpeg_path
        if ffmpeg_path is None:
            ffmpeg_path = self.ffmpeg_path
        print("=" * 60)
        print("实验3: merge_min_gap参数分析")
        print("=" * 60)
        print(f"VAD配置:")
        print(f"  - threshold: {threshold}")
        print(f"  - min_speech_duration_ms: {min_speech_duration_ms}")
        print(f"  - max_speech_duration_s: {max_speech_duration_s}")
        print(f"  - min_silence_duration_ms: {min_silence_duration_ms}")
        print(f"搜索窗口: {search_window} 秒")
        print(f"目标百分位数: {percentile}%")
        print()
        
        # 加载数据集
        dataset = self._load_dataset()
        
        if not dataset:
            print("错误: 未找到任何数据")
            return {}
        
        print(f"找到 {len(dataset)} 个数据对")
        
        # 创建临时音频目录
        temp_audio_dir = self.results_dir / 'temp_audio'
        temp_audio_dir.mkdir(parents=True, exist_ok=True)
        
        # 提取音频文件
        print("\n提取音频文件...")
        for item in tqdm(dataset, desc="提取音频"):
            if not Path(item['audio']).exists():
                video_path = item['video']
                audio_path = item['audio']
                if not extract_audio_from_video(video_path, audio_path, ffmpeg_path):
                    print(f"\n警告: 无法从 {video_path} 提取音频")
        
        # 收集间隔数据
        all_gaps = []
        category_gaps = defaultdict(list)
        
        for item in tqdm(dataset, desc="处理数据"):
            try:
                # 1. 解析真实字幕，找到首尾相连的时间戳
                gt_timestamps = self.parser.parse_file(item['subtitle'])
                merge_points = self.parser.find_merged_timestamps(gt_timestamps, tolerance=0.05)
                
                if not merge_points:
                    continue
                
                # 检查音频文件是否存在
                if not Path(item['audio']).exists():
                    continue
                
                # 2. 生成VAD时间戳
                # 注意：这里直接使用VAD的原始输出，不调用pre_process进行合并
                vad_analyzer = VADAnalyzer(
                    threshold=threshold,
                    min_speech_duration_ms=min_speech_duration_ms,
                    max_speech_duration_s=max_speech_duration_s,
                    min_silence_duration_ms=min_silence_duration_ms
                )
                vad_timestamps = vad_analyzer.detect_speech(item['audio'])
                # 重要：此处不调用pre_process，以获取VAD的原始间隔用于分析
                
                # 3. 对每个merge_point，在VAD结果中查找对应的end和start
                for merge_ts in merge_points:
                    gap = self._find_gap_near_timestamp(
                        vad_timestamps, 
                        merge_ts, 
                        search_window
                    )
                    
                    if gap is not None:
                        all_gaps.append(gap)
                        
                        # 按类别分组
                        category = item['category']
                        category_gaps[category].append(gap)
            
            except Exception as e:
                print(f"\n处理 {item['audio']} 时出错: {e}")
                continue
        
        if not all_gaps:
            print("错误: 未收集到任何间隔数据")
            return {}
        
        print(f"\n总共收集到 {len(all_gaps)} 个间隔")
        
        # 计算统计信息
        results = {
            'total_gaps': len(all_gaps),
            'overall': self._calculate_statistics(all_gaps, percentile),
            'by_category': {}
        }
        
        # 按类别统计
        for category, gaps in category_gaps.items():
            if gaps:
                results['by_category'][category] = self._calculate_statistics(gaps, percentile)
        
        # 输出结果
        print("\n" + "=" * 60)
        print("统计结果:")
        print("=" * 60)
        print(f"\n整体:")
        self._print_statistics(results['overall'])
        
        print(f"\n按类别:")
        for category, stats in results['by_category'].items():
            print(f"\n  {category}:")
            self._print_statistics(stats, indent=4)
        
        print("\n" + "=" * 60)
        print(f"推荐的 merge_min_gap: {results['overall']['percentile_value']:.3f} 秒")
        print(f"                      ({results['overall']['percentile_value'] * 1000:.0f} ms)")
        print("=" * 60)
        
        # 保存结果
        self._save_results(results)
        self._plot_results(all_gaps, category_gaps, percentile)
        
        return results
    
    def _load_dataset(self) -> list:
        """加载数据集（支持视频文件）"""
        dataset = []
        
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']
        
        for video_file in self.data_dir.iterdir():
            if video_file.suffix.lower() not in video_extensions:
                continue
            
            # 查找同名字幕文件
            subtitle_file = None
            for ext in ['.ass', '.srt']:
                sub_path = video_file.with_suffix(ext)
                if sub_path.exists():
                    subtitle_file = sub_path
                    break
            
            if subtitle_file:
                # 生成音频文件路径
                audio_file = self.results_dir / 'temp_audio' / f'{video_file.stem}.wav'
                category = self._infer_category(video_file)
                dataset.append({
                    'video': str(video_file),
                    'audio': str(audio_file),
                    'subtitle': str(subtitle_file),
                    'category': category
                })
        
        return dataset
    
    def _infer_category(self, audio_path: Path) -> str:
        """推断类别"""
        name_lower = audio_path.stem.lower()
        parent_lower = audio_path.parent.name.lower()
        
        if 'live' in name_lower or 'live' in parent_lower:
            return 'live'
        elif 'interview' in name_lower or '访谈' in name_lower or 'interview' in parent_lower:
            return 'interview'
        elif 'radio' in name_lower or '电台' in name_lower or 'radio' in parent_lower:
            return 'radio'
        elif 'anime' in name_lower or '动画' in name_lower or 'anime' in parent_lower:
            return 'anime'
        else:
            return 'other'
    
    def _find_gap_near_timestamp(self, vad_timestamps: list, 
                                 target_ts: float, 
                                 window: float) -> float:
        """
        在目标时间戳附近查找VAD的间隔
        
        Args:
            vad_timestamps: VAD时间戳列表
            target_ts: 目标时间戳（真实字幕的连接点）
            window: 搜索窗口大小
            
        Returns:
            float: 找到的间隔，如果未找到返回None
        """
        # 在 [target_ts - window, target_ts] 区间内查找end
        end_candidates = []
        for ts in vad_timestamps:
            if target_ts - window <= ts['end'] <= target_ts:
                end_candidates.append(ts['end'])
        
        # 在 [target_ts, target_ts + window] 区间内查找start
        start_candidates = []
        for ts in vad_timestamps:
            if target_ts <= ts['start'] <= target_ts + window:
                start_candidates.append(ts['start'])
        
        # 如果两者都存在，计算间隔
        if end_candidates and start_candidates:
            # 选择最接近target_ts的end和start
            best_end = max(end_candidates)  # 离target_ts最近的end
            best_start = min(start_candidates)  # 离target_ts最近的start
            
            gap = best_start - best_end
            if gap > 0:  # 确保是正间隔
                return gap
        
        return None
    
    def _calculate_statistics(self, gaps: list, percentile: float) -> dict:
        """计算统计信息"""
        gaps_array = np.array(gaps)
        
        return {
            'count': len(gaps),
            'min': float(np.min(gaps_array)),
            'max': float(np.max(gaps_array)),
            'mean': float(np.mean(gaps_array)),
            'median': float(np.median(gaps_array)),
            'std': float(np.std(gaps_array)),
            'percentile_value': float(np.percentile(gaps_array, percentile)),
            'percentile': percentile
        }
    
    def _print_statistics(self, stats: dict, indent: int = 0):
        """打印统计信息"""
        prefix = ' ' * indent
        print(f"{prefix}数量: {stats['count']}")
        print(f"{prefix}最小值: {stats['min']:.3f} 秒 ({stats['min']*1000:.0f} ms)")
        print(f"{prefix}最大值: {stats['max']:.3f} 秒 ({stats['max']*1000:.0f} ms)")
        print(f"{prefix}平均值: {stats['mean']:.3f} 秒 ({stats['mean']*1000:.0f} ms)")
        print(f"{prefix}中位数: {stats['median']:.3f} 秒 ({stats['median']*1000:.0f} ms)")
        print(f"{prefix}标准差: {stats['std']:.3f} 秒")
        print(f"{prefix}{stats['percentile']:.0f}%分位数: {stats['percentile_value']:.3f} 秒 ({stats['percentile_value']*1000:.0f} ms)")
    
    def _save_results(self, results: dict):
        """保存结果"""
        output_file = self.results_dir / 'exp3_merge_min_gap_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n结果已保存到: {output_file}")
    
    def _plot_results(self, all_gaps: list, category_gaps: dict, percentile: float):
        """绘制结果图表"""
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # 图1: 整体间隔分布
        ax1 = axes[0]
        gaps_ms = [g * 1000 for g in all_gaps]
        ax1.hist(gaps_ms, bins=100, alpha=0.7, edgecolor='black')
        
        # 标记百分位数
        percentile_value = np.percentile(gaps_ms, percentile)
        ax1.axvline(percentile_value, color='r', linestyle='--', linewidth=2,
                   label=f'{percentile:.0f}% percentile: {percentile_value:.0f} ms')
        
        ax1.set_xlabel('Gap Duration (ms)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_title('Overall Merge Gap Distribution', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 图2: 按类别的间隔分布
        ax2 = axes[1]
        category_data = []
        category_labels = []
        
        for category, gaps in sorted(category_gaps.items()):
            if gaps:
                category_data.append([g * 1000 for g in gaps])
                category_labels.append(f"{category}\n(n={len(gaps)})")
        
        if category_data:
            bp = ax2.boxplot(category_data, labels=category_labels, patch_artist=True)
            
            colors = plt.cm.Set3(range(len(category_data)))
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
            
            ax2.set_ylabel('Gap Duration (ms)', fontsize=12)
            ax2.set_title('Merge Gap Distribution by Category', fontsize=14)
            ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        output_file = self.results_dir / 'exp3_merge_min_gap_plot.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"图表已保存到: {output_file}")
        plt.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='实验3: merge_min_gap参数分析')
    parser.add_argument('--data_dir', type=str, default='exp/data',
                       help='数据目录路径')
    parser.add_argument('--results_dir', type=str, default='exp/results',
                       help='结果输出目录')
    parser.add_argument('--threshold', type=float, default=0.5,
                       help='VAD阈值')
    parser.add_argument('--percentile', type=float, default=5.0,
                       help='百分位数 (0-100)')
    
    args = parser.parse_args()
    
    experiment = MergeMinGapExperiment(args.data_dir, args.results_dir)
    experiment.run_experiment(
        threshold=args.threshold,
        percentile=args.percentile
    )

