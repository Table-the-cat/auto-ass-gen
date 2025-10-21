"""
实验2: 分析min_silence_duration_ms参数
通过分析真实字幕的间隔分布，确定合适的最小静音时长
"""
import sys
from pathlib import Path
import json
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from subtitle_parser import SubtitleParser


class MinSilenceExperiment:
    """min_silence_duration_ms参数分析实验"""
    
    def __init__(self, data_dir: str, results_dir: str):
        """
        初始化实验
        
        Args:
            data_dir: 数据目录
            results_dir: 结果输出目录
        """
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.parser = SubtitleParser()
    
    def run_experiment(self, percentile: float = 5.0) -> dict:
        """
        运行实验
        
        Args:
            percentile: 要计算的百分位数
            
        Returns:
            dict: 实验结果
        """
        print("=" * 60)
        print("实验2: min_silence_duration_ms参数分析")
        print("=" * 60)
        print(f"目标百分位数: {percentile}%")
        print()
        
        # 查找所有字幕文件
        subtitle_files = list(self.data_dir.glob('*.ass')) + list(self.data_dir.glob('*.srt'))
        
        if not subtitle_files:
            print("错误: 未找到任何字幕文件")
            return {}
        
        print(f"找到 {len(subtitle_files)} 个字幕文件")
        
        # 收集所有间隔
        all_gaps = []
        category_gaps = defaultdict(list)
        
        for subtitle_file in subtitle_files:
            try:
                # 解析字幕
                timestamps = self.parser.parse_file(str(subtitle_file))
                
                # 提取间隔
                gaps = self.parser.extract_gaps(timestamps)
                
                # 过滤掉0值
                gaps = [g for g in gaps if g > 0]
                
                all_gaps.extend(gaps)
                
                # 按类别分组
                category = self._infer_category(subtitle_file)
                category_gaps[category].extend(gaps)
                
                print(f"  {subtitle_file.name}: {len(gaps)} 个间隔")
            
            except Exception as e:
                print(f"  错误: 处理 {subtitle_file.name} 失败: {e}")
                continue
        
        if not all_gaps:
            print("错误: 未收集到任何间隔数据")
            return {}
        
        print(f"\n总共收集到 {len(all_gaps)} 个间隔")
        
        # 去重
        unique_gaps = list(set(all_gaps))
        print(f"去重后: {len(unique_gaps)} 个唯一间隔")
        
        # 计算统计信息
        results = {
            'total_gaps': len(all_gaps),
            'unique_gaps': len(unique_gaps),
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
        print(f"推荐的 min_silence_duration_ms: {results['overall']['percentile_value'] * 1000:.0f} ms")
        print("=" * 60)
        
        # 保存结果
        self._save_results(results)
        self._plot_results(all_gaps, category_gaps, percentile)
        
        return results
    
    def _infer_category(self, subtitle_path: Path) -> str:
        """推断类别"""
        name_lower = subtitle_path.stem.lower()
        parent_lower = subtitle_path.parent.name.lower()
        
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
        output_file = self.results_dir / 'exp2_min_silence_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n结果已保存到: {output_file}")
    
    def _plot_results(self, all_gaps: list, category_gaps: dict, percentile: float):
        """绘制结果图表"""
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # 图1: 整体间隔分布
        ax1 = axes[0]
        gaps_ms = [g * 1000 for g in all_gaps]  # 转换为毫秒
        ax1.hist(gaps_ms, bins=100, alpha=0.7, edgecolor='black')
        
        # 标记百分位数
        percentile_value = np.percentile(gaps_ms, percentile)
        ax1.axvline(percentile_value, color='r', linestyle='--', linewidth=2,
                   label=f'{percentile:.0f}% percentile: {percentile_value:.0f} ms')
        
        ax1.set_xlabel('Gap Duration (ms)', fontsize=12)
        ax1.set_ylabel('Frequency', fontsize=12)
        ax1.set_title('Overall Gap Distribution', fontsize=14)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 图2: 按类别的间隔分布（箱线图）
        ax2 = axes[1]
        category_data = []
        category_labels = []
        
        for category, gaps in sorted(category_gaps.items()):
            if gaps:
                category_data.append([g * 1000 for g in gaps])
                category_labels.append(f"{category}\n(n={len(gaps)})")
        
        if category_data:
            bp = ax2.boxplot(category_data, labels=category_labels, patch_artist=True)
            
            # 设置颜色
            colors = plt.cm.Set3(range(len(category_data)))
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
            
            ax2.set_ylabel('Gap Duration (ms)', fontsize=12)
            ax2.set_title('Gap Distribution by Category', fontsize=14)
            ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        output_file = self.results_dir / 'exp2_min_silence_plot.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"图表已保存到: {output_file}")
        plt.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='实验2: min_silence_duration_ms参数分析')
    parser.add_argument('--data_dir', type=str, default='exp/data',
                       help='数据目录路径')
    parser.add_argument('--results_dir', type=str, default='exp/results',
                       help='结果输出目录')
    parser.add_argument('--percentile', type=float, default=5.0,
                       help='百分位数 (0-100)')
    
    args = parser.parse_args()
    
    experiment = MinSilenceExperiment(args.data_dir, args.results_dir)
    experiment.run_experiment(percentile=args.percentile)

