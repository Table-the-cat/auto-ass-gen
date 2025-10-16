"""
使用示例代码
展示如何在Python代码中使用各个模块
"""
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))


def example_1_basic_usage():
    """示例1：基本使用 - 完整流程"""
    print("=" * 60)
    print("示例1：基本使用 - 完整流程")
    print("=" * 60)
    
    from config import load_config
    from main import ASSGenerator
    
    # 加载配置
    config = load_config()
    
    # 修改配置（如果需要）
    config._config['paths']['input_file'] = 'input/my_video.mp4'
    config._config['paths']['output_ass'] = 'output/my_subtitle.ass'
    
    # 创建生成器并运行
    generator = ASSGenerator(config)
    success = generator.generate()
    
    if success:
        print("✓ 字幕生成成功！")
    else:
        print("✗ 字幕生成失败")


def example_2_audio_extraction():
    """示例2：仅提取音频"""
    print("\n" + "=" * 60)
    print("示例2：仅提取音频")
    print("=" * 60)
    
    from util import AudioExtractor
    
    # 创建音频提取器
    extractor = AudioExtractor()
    
    # 检查FFmpeg
    if not extractor.check_ffmpeg_available():
        print("错误: FFmpeg不可用")
        return
    
    # 提取音频
    input_file = 'input/video.mp4'
    output_wav = 'output/audio.wav'
    
    try:
        extractor.extract_audio(input_file, output_wav, sample_rate=16000)
        print(f"✓ 音频已提取到: {output_wav}")
    except Exception as e:
        print(f"✗ 提取失败: {e}")


def example_3_vad_only():
    """示例3：仅进行语音检测"""
    print("\n" + "=" * 60)
    print("示例3：仅进行语音检测")
    print("=" * 60)
    
    from vad import VADProcessor
    
    # 创建VAD处理器
    vad = VADProcessor(
        use_onnx=True,
        threshold=0.5,
        min_speech_duration_ms=250
    )
    
    # 检测语音
    audio_file = 'output/audio.wav'
    
    try:
        timestamps = vad.detect_speech(audio_file, return_seconds=True)
        
        print(f"检测到 {len(timestamps)} 个语音片段:")
        for i, ts in enumerate(timestamps, 1):
            duration = ts['end'] - ts['start']
            print(f"  片段 {i}: {ts['start']:.2f}s - {ts['end']:.2f}s "
                  f"(时长: {duration:.2f}s)")
        
        return timestamps
    except Exception as e:
        print(f"✗ 检测失败: {e}")
        return None


def example_4_time_conversion():
    """示例4：时间格式转换"""
    print("\n" + "=" * 60)
    print("示例4：时间格式转换")
    print("=" * 60)
    
    from util import seconds_to_ass_time, ass_time_to_seconds
    
    # 秒 -> ASS格式
    test_seconds = [0.5, 3.2, 150.75, 3661.25]
    
    print("秒数 -> ASS格式:")
    for seconds in test_seconds:
        ass_time = seconds_to_ass_time(seconds)
        print(f"  {seconds:8.2f}s -> {ass_time}")
    
    # ASS格式 -> 秒
    print("\nASS格式 -> 秒数:")
    test_times = ["0:00:00.50", "0:02:30.75", "1:01:01.25"]
    for time_str in test_times:
        seconds = ass_time_to_seconds(time_str)
        print(f"  {time_str:12s} -> {seconds:.2f}s")


def example_5_ass_generation():
    """示例5：生成ASS文件"""
    print("\n" + "=" * 60)
    print("示例5：生成ASS文件")
    print("=" * 60)
    
    from util import ASSWriter, seconds_to_ass_time
    
    # 准备时间戳数据（秒）
    timestamps_seconds = [
        {'start': 0.5, 'end': 3.2},
        {'start': 4.1, 'end': 7.8},
        {'start': 9.0, 'end': 12.5}
    ]
    
    # 转换为ASS格式
    timestamps_ass = []
    for ts in timestamps_seconds:
        timestamps_ass.append({
            'start': seconds_to_ass_time(ts['start']),
            'end': seconds_to_ass_time(ts['end'])
        })
    
    # 写入ASS文件
    output_path = 'output/example.ass'
    ASSWriter.write_ass_file(
        output_path,
        timestamps_ass,
        title="示例字幕",
        resolution=(1920, 1080)
    )
    
    print(f"✓ ASS文件已生成: {output_path}")


def example_6_custom_style():
    """示例6：自定义字幕样式"""
    print("\n" + "=" * 60)
    print("示例6：自定义字幕样式")
    print("=" * 60)
    
    from util import ASSWriter
    
    # 自定义样式配置
    custom_style = {
        'Name': 'Custom',
        'Fontname': 'Arial',
        'Fontsize': 64,
        'PrimaryColour': '&H00FFFF00',  # 青色
        'SecondaryColour': '&H00FF0000',  # 蓝色
        'OutlineColour': '&H00000000',   # 黑色边框
        'BackColour': '&H80000000',      # 半透明背景
        'Bold': 1,                       # 粗体
        'Italic': 0,
        'Underline': 0,
        'StrikeOut': 0,
        'ScaleX': 100,
        'ScaleY': 100,
        'Spacing': 0,
        'Angle': 0,
        'BorderStyle': 1,
        'Outline': 3,                    # 更粗的边框
        'Shadow': 4,                     # 更深的阴影
        'Alignment': 8,                  # 顶部居中
        'MarginL': 20,
        'MarginR': 20,
        'MarginV': 50,                   # 更大的垂直边距
        'Encoding': 1
    }
    
    # 示例时间戳
    timestamps = [
        {'start': '0:00:01.00', 'end': '0:00:05.00'},
        {'start': '0:00:06.00', 'end': '0:00:10.00'}
    ]
    
    # 生成ASS文件
    output_path = 'output/custom_style.ass'
    ASSWriter.write_ass_file(
        output_path,
        timestamps,
        title="自定义样式字幕",
        resolution=(1920, 1080),
        style_config=custom_style
    )
    
    print(f"✓ 自定义样式ASS文件已生成: {output_path}")


def example_7_batch_processing():
    """示例7：批量处理多个文件"""
    print("\n" + "=" * 60)
    print("示例7：批量处理多个文件")
    print("=" * 60)
    
    from pathlib import Path
    from config import load_config
    from main import ASSGenerator
    
    # 查找所有视频文件
    input_dir = Path('input')
    video_files = list(input_dir.glob('*.mp4')) + \
                  list(input_dir.glob('*.avi')) + \
                  list(input_dir.glob('*.mkv'))
    
    if not video_files:
        print("input/ 目录中没有找到视频文件")
        return
    
    print(f"找到 {len(video_files)} 个视频文件:")
    
    # 处理每个文件
    for video_file in video_files:
        print(f"\n处理: {video_file.name}")
        
        # 加载配置
        config = load_config()
        
        # 设置输入输出路径
        config._config['paths']['input_file'] = str(video_file)
        config._config['paths']['output_ass'] = f"output/{video_file.stem}.ass"
        config._config['paths']['output_wav'] = f"output/{video_file.stem}.wav"
        
        # 生成字幕
        generator = ASSGenerator(config)
        success = generator.generate()
        
        if success:
            print(f"  ✓ {video_file.name} 处理完成")
        else:
            print(f"  ✗ {video_file.name} 处理失败")


def example_8_config_usage():
    """示例8：配置文件的使用"""
    print("\n" + "=" * 60)
    print("示例8：配置文件的使用")
    print("=" * 60)
    
    from config import load_config
    from util import ConfigReader
    
    # 方法1：加载默认配置
    config1 = load_config()
    print("默认配置:")
    print(f"  输入文件: {config1.input_file}")
    print(f"  VAD阈值: {config1.vad_threshold}")
    
    # 方法2：加载自定义配置
    if Path('example_config.yaml').exists():
        config2 = load_config('example_config.yaml')
        print("\n自定义配置:")
        print(f"  输入文件: {config2.input_file}")
        print(f"  分辨率: {config2.resolution}")
    
    # 方法3：创建新配置
    new_config = {
        'paths': {
            'input_file': 'my_video.mp4',
            'output_ass': 'my_subtitle.ass'
        },
        'vad': {
            'threshold': 0.6
        }
    }
    
    # 保存配置
    ConfigReader.write_config('my_config.yaml', new_config)
    print("\n✓ 新配置已保存到 my_config.yaml")


def main():
    """运行所有示例"""
    print("\n" + "=" * 70)
    print(" 自动ASS字幕生成工具 - 使用示例")
    print("=" * 70)
    
    examples = [
        ("时间格式转换", example_4_time_conversion),
        ("生成ASS文件", example_5_ass_generation),
        ("自定义样式", example_6_custom_style),
        ("配置文件使用", example_8_config_usage),
        # 以下示例需要实际文件，可根据需要启用
        # ("音频提取", example_2_audio_extraction),
        # ("语音检测", example_3_vad_only),
        # ("完整流程", example_1_basic_usage),
        # ("批量处理", example_7_batch_processing),
    ]
    
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n✗ 示例 '{name}' 执行失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("示例演示完成！")
    print("=" * 70)
    print("\n提示:")
    print("- 部分示例需要实际的视频/音频文件才能运行")
    print("- 可以修改示例代码中的文件路径来测试")
    print("- 查看 快速开始.txt 了解更多使用方法")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()

