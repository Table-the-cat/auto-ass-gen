"""
时间格式转换工具
将秒转换为ASS字幕格式的时间字符串
"""


def seconds_to_ass_time(seconds):
    """
    将秒转换为ASS时间格式: H:MM:SS.ss
    
    Args:
        seconds: 秒数（float）
        
    Returns:
        str: ASS格式的时间字符串，例如 "0:02:30.50"
        
    Examples:
        >>> seconds_to_ass_time(0.5)
        '0:00:00.50'
        >>> seconds_to_ass_time(150.75)
        '0:02:30.75'
        >>> seconds_to_ass_time(3661.25)
        '1:01:01.25'
    """
    # 计算小时、分钟、秒和百分之一秒
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds % 1) * 100)
    
    # 格式化为 H:MM:SS.ss
    return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"


def ass_time_to_seconds(time_str):
    """
    将ASS时间格式转换为秒
    
    Args:
        time_str: ASS格式的时间字符串，例如 "0:02:30.50"
        
    Returns:
        float: 秒数
        
    Examples:
        >>> ass_time_to_seconds("0:00:00.50")
        0.5
        >>> ass_time_to_seconds("0:02:30.75")
        150.75
        >>> ass_time_to_seconds("1:01:01.25")
        3661.25
    """
    # 分割时间字符串
    time_parts = time_str.split(':')
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    
    # 处理秒和百分之一秒
    sec_parts = time_parts[2].split('.')
    seconds = int(sec_parts[0])
    centiseconds = int(sec_parts[1]) if len(sec_parts) > 1 else 0
    
    # 转换为总秒数
    total_seconds = hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
    return total_seconds


def merge_close_timestamps(timestamps, config=None):
    """
    合并间隔过小的语音片段，支持最大时长限制和最小间隔调整
    
    Args:
        timestamps: 原始时间戳列表，格式为 [{'start': float, 'end': float}, ...]
        config: 配置对象，包含合并参数配置。如果为None，使用默认值
        
    Returns:
        list: 合并/调整后的时间戳列表
        
    配置参数说明（通过config对象读取）：
        - merge_gap_threshold: 间隔阈值（秒），小于等于此值的片段可能被合并，默认1.0秒
        - merge_min_gap: 最小间隔（秒），小于此值时调整时间戳使其相连，默认0.5秒
        - merge_max_duration: 单个字幕最大时长（秒），超过此时长不再合并，默认15.0秒
    """
    if not timestamps:
        return []
    
    # 从配置对象读取参数，如果没有配置则使用默认值
    if config is not None:
        gap_threshold = getattr(config, 'merge_gap_threshold', 1.0)
        min_gap = getattr(config, 'merge_min_gap', 0.5)
        max_speech_duration_s = getattr(config, 'merge_max_duration', 15.0)
    else:
        # 默认值
        gap_threshold = 1.0
        min_gap = 0.5
        max_speech_duration_s = 15.0
    
    # 按开始时间排序（确保顺序正确）
    sorted_timestamps = sorted(timestamps, key=lambda x: x['start'])
    
    merged = []
    current = sorted_timestamps[0].copy()
    
    for i in range(1, len(sorted_timestamps)):
        next_ts = sorted_timestamps[i]
        
        # 计算当前片段的时长和与下一个片段的间隔
        current_duration = current['end'] - current['start']
        gap = next_ts['start'] - current['end']
        
        # 判断是否应该合并
        should_merge = False
        if gap <= gap_threshold:
            # 间隔小于阈值，检查是否超过最大时长
            if current_duration < max_speech_duration_s:
                # 当前片段未超过最大时长，可以合并
                should_merge = True
        
        if should_merge:
            # 合并片段：将当前片段的结束时间延长到下一个片段的结束时间
            current['end'] = next_ts['end']
        else:
            # 不合并，但检查间隔是否过小
            if gap < min_gap and gap > 0:
                # 间隔过小，调整当前片段的结束时间使其与下一个片段相连
                current['end'] = next_ts['start']
            
            # 保存当前片段，开始新片段
            merged.append(current)
            current = next_ts.copy()
    
    # 添加最后一个片段
    merged.append(current)
    
    return merged


if __name__ == '__main__':
    # 测试时间转换
    print("=" * 60)
    print("测试 seconds_to_ass_time:")
    print("=" * 60)
    test_cases = [0.5, 3.2, 150.75, 3661.25]
    
    for seconds in test_cases:
        ass_time = seconds_to_ass_time(seconds)
        print(f"{seconds}秒 -> {ass_time}")
        
        # 反向转换验证
        back_seconds = ass_time_to_seconds(ass_time)
        print(f"  验证: {ass_time} -> {back_seconds}秒")
        assert abs(back_seconds - seconds) < 0.01, "转换不一致！"
    
    print("\n✓ 时间转换测试通过！")
    
    # 测试时间戳合并
    print("\n" + "=" * 60)
    print("测试 merge_close_timestamps:")
    print("=" * 60)
    
    # 创建一个简单的配置对象用于测试
    class TestConfig:
        def __init__(self, gap_threshold=1.0, min_gap=0.5, max_duration=15.0):
            self.merge_gap_threshold = gap_threshold
            self.merge_min_gap = min_gap
            self.merge_max_duration = max_duration
    
    # 测试1：正常合并
    print("\n【测试1：正常合并】")
    test_timestamps_1 = [
        {'start': 0.5, 'end': 2.0},
        {'start': 2.5, 'end': 4.0},   # 间隔0.5秒，应该被合并
        {'start': 4.8, 'end': 6.0},   # 间隔0.8秒，应该被合并
        {'start': 8.0, 'end': 10.0},  # 间隔2.0秒，不应该合并
        {'start': 10.5, 'end': 12.0}, # 间隔0.5秒，应该被合并
    ]
    
    print("原始时间戳:")
    for i, ts in enumerate(test_timestamps_1, 1):
        print(f"  {i}. {ts['start']:.1f}s - {ts['end']:.1f}s")
    
    config_1 = TestConfig(gap_threshold=1.0)
    merged_1 = merge_close_timestamps(test_timestamps_1, config=config_1)
    
    print(f"\n合并后 (阈值=1.0秒):")
    for i, ts in enumerate(merged_1, 1):
        duration = ts['end'] - ts['start']
        print(f"  {i}. {ts['start']:.1f}s - {ts['end']:.1f}s (时长: {duration:.1f}s)")
    
    assert len(merged_1) == 2, "测试1失败"
    print("✓ 测试1通过")
    
    # 测试2：超过最大时长不合并
    print("\n【测试2：超过最大时长不合并】")
    test_timestamps_2 = [
        {'start': 0.0, 'end': 14.0},   # 时长14秒
        {'start': 14.5, 'end': 16.0},  # 间隔0.5秒，但前面已经14秒
        {'start': 16.8, 'end': 18.0},  # 间隔0.8秒
    ]
    
    print("原始时间戳:")
    for i, ts in enumerate(test_timestamps_2, 1):
        duration = ts['end'] - ts['start']
        print(f"  {i}. {ts['start']:.1f}s - {ts['end']:.1f}s (时长: {duration:.1f}s)")
    
    config_2 = TestConfig(gap_threshold=1.0, max_duration=15.0)
    merged_2 = merge_close_timestamps(test_timestamps_2, config=config_2)
    
    print(f"\n合并后 (最大时长=15.0秒):")
    for i, ts in enumerate(merged_2, 1):
        duration = ts['end'] - ts['start']
        print(f"  {i}. {ts['start']:.1f}s - {ts['end']:.1f}s (时长: {duration:.1f}s)")
    
    assert len(merged_2) == 2, "测试2失败"
    assert merged_2[0]['end'] == 14.0, "测试2失败：第一个片段不应该合并"
    assert merged_2[1]['start'] == 14.5 and merged_2[1]['end'] == 18.0, "测试2失败：第二三个片段应该合并"
    print("✓ 测试2通过")
    
    # 测试3：间隔过小时调整时间戳
    print("\n【测试3：间隔过小时调整时间戳】")
    test_timestamps_3 = [
        {'start': 0.0, 'end': 14.0},   # 时长14秒
        {'start': 14.3, 'end': 16.0},  # 间隔0.3秒 < min_gap(0.5)
        {'start': 18.0, 'end': 20.0},  # 间隔2.0秒，不调整
    ]
    
    print("原始时间戳:")
    for i, ts in enumerate(test_timestamps_3, 1):
        next_gap = ""
        if i < len(test_timestamps_3):
            gap = test_timestamps_3[i]['start'] - ts['end'] if i < len(test_timestamps_3) else 0
            next_gap = f" (间隔: {gap:.1f}s)"
        print(f"  {i}. {ts['start']:.1f}s - {ts['end']:.1f}s{next_gap}")
    
    config_3 = TestConfig(gap_threshold=1.0, min_gap=0.5, max_duration=15.0)
    merged_3 = merge_close_timestamps(test_timestamps_3, config=config_3)
    
    print(f"\n调整后 (min_gap=0.5秒):")
    for i, ts in enumerate(merged_3, 1):
        duration = ts['end'] - ts['start']
        print(f"  {i}. {ts['start']:.1f}s - {ts['end']:.1f}s (时长: {duration:.1f}s)")
    
    assert merged_3[0]['end'] == 14.3, f"测试3失败：第一个片段应该延长到14.3，实际为{merged_3[0]['end']}"
    assert merged_3[1]['start'] == 14.3, "测试3失败：第二个片段应该从14.3开始"
    print("✓ 测试3通过")
    
    # 测试4：无配置对象，使用默认值
    print("\n【测试4：无配置对象，使用默认值】")
    test_timestamps_4 = [
        {'start': 0.0, 'end': 2.0},
        {'start': 2.5, 'end': 4.0},  # 间隔0.5秒，使用默认阈值1.0，应该合并
    ]
    
    merged_4 = merge_close_timestamps(test_timestamps_4, config=None)
    
    assert len(merged_4) == 1, "测试4失败：应该合并为1个片段"
    assert merged_4[0]['start'] == 0.0 and merged_4[0]['end'] == 4.0, "测试4失败：合并结果不正确"
    print("✓ 测试4通过")
    
    print("\n✓ 所有时间戳合并测试通过！")
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)

