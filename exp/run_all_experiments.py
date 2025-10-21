"""
运行所有实验
"""
import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent))

from exp1_threshold import ThresholdExperiment
from exp2_min_silence import MinSilenceExperiment
from exp3_merge_min_gap import MergeMinGapExperiment


def main():
    parser = argparse.ArgumentParser(description='运行所有VAD参数优化实验')
    parser.add_argument('--data_dir', type=str, default='exp/data',
                       help='数据目录路径')
    parser.add_argument('--results_dir', type=str, default='exp/results',
                       help='结果输出目录')
    parser.add_argument('--experiments', type=str, nargs='+', 
                       choices=['1', '2', '3', 'all'],
                       default=['all'],
                       help='要运行的实验: 1=threshold, 2=min_silence, 3=merge_min_gap, all=全部')
    parser.add_argument('--percentile', type=float, default=5.0,
                       help='百分位数 (用于实验2和3)')
    
    args = parser.parse_args()
    
    experiments_to_run = args.experiments
    if 'all' in experiments_to_run:
        experiments_to_run = ['1', '2', '3']
    
    print("\n" + "=" * 80)
    print("VAD参数优化实验套件")
    print("=" * 80)
    print(f"数据目录: {args.data_dir}")
    print(f"结果目录: {args.results_dir}")
    print(f"运行实验: {', '.join(experiments_to_run)}")
    print("=" * 80 + "\n")
    
    results = {}
    
    # 实验1: threshold优化
    if '1' in experiments_to_run:
        print("\n" + "▶" * 40)
        print("开始运行实验1: threshold参数优化")
        print("▶" * 40 + "\n")
        
        try:
            exp1 = ThresholdExperiment(args.data_dir, args.results_dir)
            results['exp1'] = exp1.run_experiment()
            print("\n✓ 实验1完成")
        except Exception as e:
            print(f"\n✗ 实验1失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 实验2: min_silence_duration_ms分析
    if '2' in experiments_to_run:
        print("\n" + "▶" * 40)
        print("开始运行实验2: min_silence_duration_ms参数分析")
        print("▶" * 40 + "\n")
        
        try:
            exp2 = MinSilenceExperiment(args.data_dir, args.results_dir)
            results['exp2'] = exp2.run_experiment(percentile=args.percentile)
            print("\n✓ 实验2完成")
        except Exception as e:
            print(f"\n✗ 实验2失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 实验3: merge_min_gap分析
    if '3' in experiments_to_run:
        print("\n" + "▶" * 40)
        print("开始运行实验3: merge_min_gap参数分析")
        print("▶" * 40 + "\n")
        
        try:
            exp3 = MergeMinGapExperiment(args.data_dir, args.results_dir)
            
            # 如果实验1已运行，使用其最优threshold
            threshold = 0.5
            if 'exp1' in results and 'overall' in results['exp1']:
                threshold = results['exp1']['overall'].get('best_threshold', 0.5)
                print(f"使用实验1的最优threshold: {threshold:.2f}")
            
            results['exp3'] = exp3.run_experiment(
                threshold=threshold,
                percentile=args.percentile
            )
            print("\n✓ 实验3完成")
        except Exception as e:
            print(f"\n✗ 实验3失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 输出总结
    print("\n" + "=" * 80)
    print("实验总结")
    print("=" * 80)
    
    if 'exp1' in results and 'overall' in results['exp1']:
        print(f"\n实验1 - 最优threshold: {results['exp1']['overall']['best_threshold']:.2f}")
        print(f"         最大F1 Score: {results['exp1']['overall']['best_f1']:.3f}")
    
    if 'exp2' in results and 'overall' in results['exp2']:
        percentile_val = results['exp2']['overall']['percentile_value']
        print(f"\n实验2 - 推荐min_silence_duration_ms: {percentile_val * 1000:.0f} ms")
    
    if 'exp3' in results and 'overall' in results['exp3']:
        percentile_val = results['exp3']['overall']['percentile_value']
        print(f"\n实验3 - 推荐merge_min_gap: {percentile_val:.3f} 秒 ({percentile_val * 1000:.0f} ms)")
    
    print("\n" + "=" * 80)
    print("所有实验完成！")
    print(f"结果已保存到: {args.results_dir}")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()

