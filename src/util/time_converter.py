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


def pre_process(timestamps, config=None):
    """
    预处理时间戳，调整间隔过小的语音片段
    
    Args:
        timestamps: 原始时间戳列表，格式为 [{'start': float, 'end': float}, ...]
        config: 配置对象，包含参数配置。如果为None，使用默认值
        
    Returns:
        list: 调整后的时间戳列表
        
    配置参数说明（通过config对象读取）：
        - merge_min_gap: 最小间隔（秒），小于此值时调整时间戳使其相连，默认0.5秒
    """
    if not timestamps:
        return []
    
    # 从配置对象读取参数，如果没有配置则使用默认值
    if config is not None:
        min_gap = getattr(config, 'merge_min_gap', 0.5)
    else:
        # 默认值
        min_gap = 0.5
    
    # 按开始时间排序（确保顺序正确）
    sorted_timestamps = sorted(timestamps, key=lambda x: x['start'])
    
    processed = []
    current = sorted_timestamps[0].copy()
    
    for i in range(1, len(sorted_timestamps)):
        next_ts = sorted_timestamps[i]
        
        # 计算与下一个片段的间隔
        gap = next_ts['start'] - current['end']
        
        # 检查间隔是否过小
        if gap < min_gap and gap > 0:
            # 间隔过小，调整当前片段的结束时间使其与下一个片段相连
            current['end'] = next_ts['start']
        
        # 保存当前片段，开始新片段
        processed.append(current)
        current = next_ts.copy()
    
    # 添加最后一个片段
    processed.append(current)
    
    return processed


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
    
    # 测试时间戳预处理
    print("\n" + "=" * 60)
    print("测试 pre_process:")
    print("=" * 60)
    
    # 创建一个简单的配置对象用于测试
    class TestConfig:
        def __init__(self, min_gap=0.5):
            self.merge_min_gap = min_gap
    
    # 测试1：间隔过小时调整时间戳
    print("\n【测试1：间隔过小时调整时间戳】")
    test_timestamps_1 = [
        {'start': 0.0, 'end': 2.0},
        {'start': 2.3, 'end': 4.0},   # 间隔0.3秒 < min_gap(0.5)，应该调整
        {'start': 5.0, 'end': 7.0},   # 间隔1.0秒 > min_gap，不应该调整
        {'start': 7.2, 'end': 9.0},   # 间隔0.2秒 < min_gap(0.5)，应该调整
    ]
    
    print("原始时间戳:")
    for i, ts in enumerate(test_timestamps_1, 1):
        if i < len(test_timestamps_1):
            gap = test_timestamps_1[i]['start'] - ts['end']
            print(f"  {i}. {ts['start']:.1f}s - {ts['end']:.1f}s (间隔: {gap:.1f}s)")
        else:
            print(f"  {i}. {ts['start']:.1f}s - {ts['end']:.1f}s")
    
    config_1 = TestConfig(min_gap=0.5)
    processed_1 = pre_process(test_timestamps_1, config=config_1)
    
    print(f"\n调整后 (min_gap=0.5秒):")
    for i, ts in enumerate(processed_1, 1):
        if i < len(processed_1):
            gap = processed_1[i]['start'] - ts['end']
            print(f"  {i}. {ts['start']:.1f}s - {ts['end']:.1f}s (间隔: {gap:.1f}s)")
        else:
            print(f"  {i}. {ts['start']:.1f}s - {ts['end']:.1f}s")
    
    assert processed_1[0]['end'] == 2.3, f"测试1失败：第一个片段应该延长到2.3，实际为{processed_1[0]['end']}"
    assert processed_1[1]['start'] == 2.3, "测试1失败：第二个片段应该从2.3开始"
    assert processed_1[2]['end'] == 7.0, "测试1失败：第三个片段不应该调整"
    assert processed_1[2]['start'] == 5.0, "测试1失败：第三个片段应该从5.0开始"
    assert processed_1[3]['end'] == 9.0, "测试1失败：第四个片段结束时间不应该变"
    print("✓ 测试1通过")
    
    # 测试2：无配置对象，使用默认值
    print("\n【测试2：无配置对象，使用默认值】")
    test_timestamps_2 = [
        {'start': 0.0, 'end': 2.0},
        {'start': 2.3, 'end': 4.0},  # 间隔0.3秒 < 默认min_gap(0.5)，应该调整
    ]
    
    processed_2 = pre_process(test_timestamps_2, config=None)
    
    assert len(processed_2) == 2, "测试2失败：应该有2个片段"
    assert processed_2[0]['end'] == 2.3, f"测试2失败：第一个片段应该延长到2.3，实际为{processed_2[0]['end']}"
    print("✓ 测试2通过")
    
    # 测试3：间隔为0或负数的情况不调整
    print("\n【测试3：间隔为0或负数不调整】")
    test_timestamps_3 = [
        {'start': 0.0, 'end': 2.0},
        {'start': 2.0, 'end': 4.0},   # 间隔为0，不应该调整
        {'start': 5.0, 'end': 7.0},
    ]
    
    processed_3 = pre_process(test_timestamps_3, config=None)
    
    assert processed_3[0]['end'] == 2.0, "测试3失败：间隔为0时不应该调整"
    print("✓ 测试3通过")
    
    print("\n✓ 所有时间戳预处理测试通过！")
    print("\n" + "=" * 60)
    print("所有测试通过！")
    print("=" * 60)

