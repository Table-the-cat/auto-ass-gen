"""
实验1: 优化threshold参数
通过遍历不同的threshold值，找到F1 Score最大的最优阈值

实验逻辑说明：
1. 遍历不同的threshold值（0.2-0.6）
2. 对每个threshold，使用VAD生成语音片段
3. 调用pre_process对VAD结果进行后处理（合并间隔过小的片段）
4. 与真实字幕对比，计算F1 Score
5. 找到F1 Score最高的threshold值

注意：此实验使用pre_process，模拟实际使用场景（与src/main.py一致）
"""
import sys
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from subtitle_parser import SubtitleParser
from vad_analyzer import VADAnalyzer, SILERO_AVAILABLE, extract_audio_from_video
from metrics import evaluate_vad_performance

# 从src导入pre_process函数
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from util import pre_process


class SimpleConfig:
    """简单配置对象，用于传递参数给pre_process"""
    def __init__(self, merge_min_gap: float = 0.5):
        self.merge_min_gap = merge_min_gap


class ThresholdExperiment:
    """threshold参数优化实验"""
    
    def __init__(self, data_dir: str, results_dir: str, merge_min_gap: float = 0.5, ffmpeg_path: str = None):
        """
        初始化实验
        
        Args:
            data_dir: 数据目录，包含音频文件和对应的字幕文件
            results_dir: 结果输出目录
            merge_min_gap: 最小间隔（秒），用于预处理时间戳
            ffmpeg_path: FFmpeg可执行文件路径，如果为None则尝试从配置文件读取
        """
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        if not SILERO_AVAILABLE:
            raise ImportError("需要安装Silero VAD")
        
        self.vad_analyzer = VADAnalyzer(use_onnx=True)
        self.parser = SubtitleParser()
        self.config = SimpleConfig(merge_min_gap=merge_min_gap)
        
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
    
    def load_dataset(self) -> list:
        """
        加载数据集（支持视频文件）
        
        Returns:
            list: 数据对列表，每项包含 {'video': path, 'audio': path, 'subtitle': path, 'category': str}
        """
        dataset = []
        
        # 遍历数据目录，查找视频和字幕对
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']
        
        for video_file in self.data_dir.iterdir():
            if video_file.suffix.lower() not in video_extensions:
                continue
            
            # 查找同名字幕文件
            subtitle_file = None
            sub_path = video_file.with_suffix('.ass')
            if sub_path.exists():
                subtitle_file = sub_path
            
            if subtitle_file:
                # 生成音频文件路径（临时目录）
                audio_file = self.results_dir / 'temp_audio' / f'{video_file.stem}.wav'
                
                # 从文件名或目录结构推断类别
                category = self._infer_category(video_file)
                dataset.append({
                    'video': str(video_file),
                    'audio': str(audio_file),
                    'subtitle': str(subtitle_file),
                    'category': category
                })
        
        print(f"加载了 {len(dataset)} 个数据对")
        return dataset
    
    def _infer_category(self, audio_path: Path) -> str:
        """从文件名或路径推断类别"""
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
    
    def run_experiment(self, threshold_range: list = None, 
                      min_speech_duration_ms: int = 250,
                      min_silence_duration_ms: int = 1000,
                      iou_threshold: float = 0.5,
                      ffmpeg_path: str = None) -> dict:
        """
        运行实验
        
        Args:
            threshold_range: 要测试的threshold值列表
            min_speech_duration_ms: 最小语音持续时间
            min_silence_duration_ms: 最小静音持续时间
            iou_threshold: 匹配的IoU阈值
            ffmpeg_path: FFmpeg可执行文件路径，如果为None则使用初始化时的路径
            
        Returns:
            dict: 实验结果
        """
        # 如果没有提供ffmpeg_path，使用实例的ffmpeg_path
        if ffmpeg_path is None:
            ffmpeg_path = self.ffmpeg_path
        if threshold_range is None:
            # 修改为0.2-0.6，步长0.05
            threshold_range = np.arange(0.2, 0.65, 0.05).tolist()
        
        print("=" * 60)
        print("实验1: threshold参数优化")
        print("=" * 60)
        print(f"阈值范围: {threshold_range}")
        print(f"min_speech_duration_ms: {min_speech_duration_ms}")
        print(f"min_silence_duration_ms: {min_silence_duration_ms}")
        print(f"merge_min_gap: {self.config.merge_min_gap}秒")
        print(f"IoU阈值: {iou_threshold}")
        print()
        
        # 加载数据集
        dataset = self.load_dataset()
        if not dataset:
            print("错误: 未找到任何数据")
            return {}
        
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
        
        # 统计数据
        categories = {}
        for item in dataset:
            cat = item['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n数据集统计:")
        for cat, count in categories.items():
            print(f"  - {cat}: {count} 个样本")
        print()
        
        # 存储结果
        results = {
            'threshold_values': threshold_range,
            'per_threshold': {},
            'per_category': {},
            'overall': {}
        }
        
        # 对每个threshold值进行测试
        for threshold in tqdm(threshold_range, desc="测试threshold"):
            threshold_results = {
                'f1_scores': [],
                'precision_scores': [],
                'recall_scores': [],
                'category_results': {}
            }
            
            # 创建使用当前threshold的VAD分析器
            current_vad = VADAnalyzer(
                threshold=threshold,
                min_speech_duration_ms=min_speech_duration_ms,
                min_silence_duration_ms=min_silence_duration_ms
            )
            
            # 对每个样本进行评估
            for item in tqdm(dataset, desc=f"threshold={threshold:.2f}", leave=False):
                try:
                    # 检查音频文件是否存在
                    if not Path(item['audio']).exists():
                        print(f"\n警告: 音频文件不存在: {item['audio']}")
                        continue
                    
                    # 加载真实字幕
                    gt_timestamps = self.parser.parse_file(item['subtitle'])
                    
                    # 使用当前threshold生成VAD结果
                    vad_timestamps = current_vad.detect_speech(item['audio'])
                    
                    # 预处理时间戳（与src/main.py保持一致）
                    # 调整间隔过小的语音片段
                    pred_timestamps = pre_process(vad_timestamps, config=self.config)
                    
                    # 评估性能
                    metrics = evaluate_vad_performance(pred_timestamps, gt_timestamps, iou_threshold)
                    
                    # 记录结果
                    threshold_results['f1_scores'].append(metrics['f1'])
                    threshold_results['precision_scores'].append(metrics['precision'])
                    threshold_results['recall_scores'].append(metrics['recall'])
                    
                    # 按类别记录
                    category = item['category']
                    if category not in threshold_results['category_results']:
                        threshold_results['category_results'][category] = []
                    threshold_results['category_results'][category].append(metrics['f1'])
                
                except Exception as e:
                    print(f"\n处理 {item['audio']} 时出错: {e}")
                    continue
            
            # 计算平均值
            avg_f1 = np.mean(threshold_results['f1_scores']) if threshold_results['f1_scores'] else 0
            avg_precision = np.mean(threshold_results['precision_scores']) if threshold_results['precision_scores'] else 0
            avg_recall = np.mean(threshold_results['recall_scores']) if threshold_results['recall_scores'] else 0
            
            results['per_threshold'][threshold] = {
                'avg_f1': avg_f1,
                'avg_precision': avg_precision,
                'avg_recall': avg_recall,
                'std_f1': np.std(threshold_results['f1_scores']) if threshold_results['f1_scores'] else 0,
                'category_f1': {cat: np.mean(scores) for cat, scores in threshold_results['category_results'].items()}
            }
            
            print(f"threshold={threshold:.2f}: F1={avg_f1:.3f}, P={avg_precision:.3f}, R={avg_recall:.3f}")
        
        # 找到最优threshold
        best_threshold = max(results['per_threshold'].items(), 
                            key=lambda x: x[1]['avg_f1'])[0]
        results['overall']['best_threshold'] = best_threshold
        results['overall']['best_f1'] = results['per_threshold'][best_threshold]['avg_f1']
        
        print("\n" + "=" * 60)
        print(f"最优threshold: {best_threshold:.2f}")
        print(f"最大F1 Score: {results['overall']['best_f1']:.3f}")
        print("=" * 60)
        
        # 保存结果
        self._save_results(results)
        self._plot_results(results)
        
        return results
    
    def _save_results(self, results: dict):
        """保存结果到JSON文件"""
        output_file = self.results_dir / 'exp1_threshold_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n结果已保存到: {output_file}")
    
    def _plot_results(self, results: dict):
        """绘制结果图表"""
        thresholds = results['threshold_values']
        f1_scores = [results['per_threshold'][t]['avg_f1'] for t in thresholds]
        precision_scores = [results['per_threshold'][t]['avg_precision'] for t in thresholds]
        recall_scores = [results['per_threshold'][t]['avg_recall'] for t in thresholds]
        
        plt.figure(figsize=(12, 6))
        
        plt.plot(thresholds, f1_scores, 'o-', label='F1 Score', linewidth=2)
        plt.plot(thresholds, precision_scores, 's-', label='Precision', linewidth=2)
        plt.plot(thresholds, recall_scores, '^-', label='Recall', linewidth=2)
        
        # 标记最优点
        best_threshold = results['overall']['best_threshold']
        best_f1 = results['overall']['best_f1']
        plt.plot(best_threshold, best_f1, 'r*', markersize=15, label=f'Best (threshold={best_threshold:.2f})')
        
        plt.xlabel('Threshold', fontsize=12)
        plt.ylabel('Score', fontsize=12)
        plt.title('VAD Performance vs Threshold', fontsize=14)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        output_file = self.results_dir / 'exp1_threshold_plot.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"图表已保存到: {output_file}")
        plt.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='实验1: threshold参数优化')
    parser.add_argument('--data_dir', type=str, default='exp/data',
                       help='数据目录路径')
    parser.add_argument('--results_dir', type=str, default='exp/results',
                       help='结果输出目录')
    
    args = parser.parse_args()
    
    experiment = ThresholdExperiment(args.data_dir, args.results_dir)
    experiment.run_experiment()

