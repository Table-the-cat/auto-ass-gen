"""
评估指标计算
用于计算VAD结果与真实字幕之间的匹配度
"""
import numpy as np
from typing import List, Dict, Tuple


def calculate_iou(pred_start: float, pred_end: float, 
                  gt_start: float, gt_end: float) -> float:
    """
    计算两个时间段的IoU (Intersection over Union)
    
    Args:
        pred_start: 预测起始时间
        pred_end: 预测结束时间
        gt_start: 真实起始时间
        gt_end: 真实结束时间
        
    Returns:
        float: IoU值 (0-1)
    """
    # 计算交集
    intersection_start = max(pred_start, gt_start)
    intersection_end = min(pred_end, gt_end)
    intersection = max(0, intersection_end - intersection_start)
    
    # 计算并集
    union_start = min(pred_start, gt_start)
    union_end = max(pred_end, gt_end)
    union = union_end - union_start
    
    if union == 0:
        return 0.0
    
    return intersection / union


def match_timestamps(pred_timestamps: List[Dict[str, float]], 
                    gt_timestamps: List[Dict[str, float]],
                    iou_threshold: float = 0.5) -> Tuple[int, int, int]:
    """
    匹配预测时间戳和真实时间戳
    
    Args:
        pred_timestamps: 预测的时间戳列表
        gt_timestamps: 真实的时间戳列表
        iou_threshold: IoU阈值，超过此值视为匹配
        
    Returns:
        Tuple[int, int, int]: (真正例, 假正例, 假负例)
            TP: 预测正确的数量
            FP: 预测错误的数量（多余的预测）
            FN: 漏检的数量（未预测到的真实标注）
    """
    gt_matched = [False] * len(gt_timestamps)
    pred_matched = [False] * len(pred_timestamps)
    
    # 对每个预测时间戳，找到最佳匹配的真实时间戳
    for i, pred in enumerate(pred_timestamps):
        best_iou = 0
        best_j = -1
        
        for j, gt in enumerate(gt_timestamps):
            if gt_matched[j]:
                continue
            
            iou = calculate_iou(pred['start'], pred['end'], gt['start'], gt['end'])
            if iou > best_iou:
                best_iou = iou
                best_j = j
        
        if best_iou >= iou_threshold and best_j >= 0:
            pred_matched[i] = True
            gt_matched[best_j] = True
    
    tp = sum(pred_matched)  # 真正例：成功匹配的预测
    fp = len(pred_timestamps) - tp  # 假正例：未匹配的预测
    fn = len(gt_timestamps) - sum(gt_matched)  # 假负例：未匹配的真实标注
    
    return tp, fp, fn


def calculate_precision_recall_f1(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    """
    计算Precision、Recall和F1 Score
    
    Args:
        tp: 真正例数量
        fp: 假正例数量
        fn: 假负例数量
        
    Returns:
        Tuple[float, float, float]: (Precision, Recall, F1)
    """
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return precision, recall, f1


def evaluate_vad_performance(pred_timestamps: List[Dict[str, float]], 
                             gt_timestamps: List[Dict[str, float]],
                             iou_threshold: float = 0.5) -> Dict[str, float]:
    """
    评估VAD性能
    
    Args:
        pred_timestamps: 预测的时间戳列表
        gt_timestamps: 真实的时间戳列表
        iou_threshold: IoU阈值
        
    Returns:
        Dict: 包含各项指标的字典
    """
    tp, fp, fn = match_timestamps(pred_timestamps, gt_timestamps, iou_threshold)
    precision, recall, f1 = calculate_precision_recall_f1(tp, fp, fn)
    
    return {
        'tp': tp,
        'fp': fp,
        'fn': fn,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'pred_count': len(pred_timestamps),
        'gt_count': len(gt_timestamps)
    }


def calculate_percentile_value(values: List[float], percentile: float = 5.0) -> float:
    """
    计算百分位数值
    
    Args:
        values: 数值列表
        percentile: 百分位数（0-100）
        
    Returns:
        float: 百分位数对应的值
    """
    if not values:
        return 0.0
    
    return float(np.percentile(values, percentile))


if __name__ == '__main__':
    print("评估指标模块")
    print("=" * 60)
    print("功能:")
    print("  1. 计算IoU")
    print("  2. 匹配预测和真实时间戳")
    print("  3. 计算Precision、Recall、F1")
    print("  4. 计算百分位数")
    print("\n使用示例:")
    print("  results = evaluate_vad_performance(pred_ts, gt_ts, iou_threshold=0.5)")
    print("  print(f'F1 Score: {results[\"f1\"]:.3f}')")

