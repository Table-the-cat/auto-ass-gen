"""
自动生成ASS字幕文件的主程序

功能流程：
1. 读取配置文件
2. 使用FFmpeg提取音频并转换为16kHz的wav文件
3. 使用Silero VAD检测语音片段
4. 将检测结果转换为ASS格式并保存
"""
import os
import sys
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from config import load_config
from util import AudioExtractor, seconds_to_ass_time, pre_process, ASSWriter
from vad import VADProcessor


class ASSGenerator:
    """ASS字幕生成器"""
    
    def __init__(self, config):
        """
        初始化ASS字幕生成器
        
        Args:
            config: 配置对象
        """
        self.config = config
        
    def generate(self):
        """
        执行完整的ASS字幕生成流程
        
        Returns:
            bool: 是否成功生成
        """
        print("=" * 60)
        print("自动ASS字幕生成工具")
        print("=" * 60)
        
        # 步骤1: 音频提取
        print("\n[步骤 1/3] 音频提取")
        print("-" * 60)
        if not self._extract_audio():
            print("错误: 音频提取失败")
            return False
        
        # 步骤2: 语音检测
        print("\n[步骤 2/3] 语音活动检测")
        print("-" * 60)
        timestamps = self._detect_speech()
        if timestamps is None or len(timestamps) == 0:
            print("警告: 未检测到语音片段")
            return False
        
        # 步骤3: 生成ASS文件
        print("\n[步骤 3/3] 生成ASS字幕文件")
        print("-" * 60)
        if not self._generate_ass(timestamps):
            print("错误: ASS文件生成失败")
            return False
        
        print("\n" + "=" * 60)
        print("✓ ASS字幕生成完成！")
        print(f"输出文件: {self.config.output_ass}")
        print("=" * 60)
        return True
    
    def _extract_audio(self):
        """
        提取音频
        
        Returns:
            bool: 是否成功
        """
        input_file = self.config.input_file
        output_wav = self.config.output_wav
        sample_rate = self.config.sample_rate
        
        print(f"输入文件: {input_file}")
        print(f"输出WAV: {output_wav}")
        print(f"采样率: {sample_rate}Hz")
        
        # 检查输入文件是否存在
        if not os.path.exists(input_file):
            print(f"错误: 输入文件不存在: {input_file}")
            return False
        
        # 创建音频提取器
        extractor = AudioExtractor(ffmpeg_path=self.config.ffmpeg_path)
        
        # 检查FFmpeg是否可用
        if not extractor.check_ffmpeg_available():
            print("错误: FFmpeg不可用，请确保已安装FFmpeg并添加到系统PATH")
            return False
        
        try:
            # 提取音频
            extractor.extract_audio(input_file, output_wav, sample_rate)
            return True
        except Exception as e:
            print(f"错误: {str(e)}")
            return False
    
    def _detect_speech(self):
        """
        检测语音片段
        
        Returns:
            list: 语音时间戳列表（秒），如果失败返回None
        """
        output_wav = self.config.output_wav
        
        # 检查音频文件是否存在
        if not os.path.exists(output_wav):
            print(f"错误: 音频文件不存在: {output_wav}")
            return None
        
        try:
            # 创建VAD处理器
            vad = VADProcessor(
                use_onnx=self.config.use_onnx,
                threshold=self.config.vad_threshold,
                min_speech_duration_ms=self.config.min_speech_duration_ms,
                max_speech_duration_s=self.config.max_speech_duration_s,
                min_silence_duration_ms=self.config.min_silence_duration_ms,
                speech_pad_ms=self.config.speech_pad_ms
            )
            
            # 检测语音
            timestamps = vad.detect_speech(
                output_wav,
                sampling_rate=self.config.sample_rate,
                return_seconds=True
            )
            
            # 显示检测结果
            print(f"\n检测到 {len(timestamps)} 个语音片段:")
            for i, ts in enumerate(timestamps[:5]):  # 只显示前5个
                print(f"  片段 {i+1}: {ts['start']:.2f}s - {ts['end']:.2f}s "
                      f"(持续 {ts['end']-ts['start']:.2f}s)")
            if len(timestamps) > 5:
                print(f"  ... 以及其他 {len(timestamps)-5} 个片段")
            
            return timestamps
            
        except Exception as e:
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generate_ass(self, timestamps):
        """
        生成ASS字幕文件
        
        Args:
            timestamps: 语音时间戳列表（秒）
            
        Returns:
            bool: 是否成功
        """
        output_ass = self.config.output_ass
        
        # 检查output_ass是否为目录路径
        output_path = Path(output_ass)
        if output_path.is_dir() or (not output_path.suffix and not output_path.exists()):
            # 如果是目录或者没有扩展名且不存在（可能是目录），则使用输入文件名
            input_path = Path(self.config.input_file)
            output_filename = input_path.stem + '.ass'  # 使用输入文件名（不含扩展名）+ .ass
            output_ass = str(output_path / output_filename)
            
            # 更新config中的output_ass，以便后续打印正确的路径
            self.config.output_ass = output_ass
            
            # 如果目录不存在，创建它
            output_path.mkdir(parents=True, exist_ok=True)
            
            print(f"检测到输出路径为目录，自动生成文件名: {output_filename}")
        
        try:
            # 预处理时间戳，调整间隔过小的语音片段
            processed_timestamps = pre_process(timestamps, config=self.config)
            
            print(f"\n时间戳预处理配置:")
            print(f"  - 最小间隔: {self.config.merge_min_gap}秒")
            print(f"\n预处理结果:")
            print(f"  - 片段数量: {len(processed_timestamps)} 个")
            
            # 转换时间格式
            ass_timestamps = []
            for ts in processed_timestamps:
                ass_ts = {
                    'start': seconds_to_ass_time(ts['start']),
                    'end': seconds_to_ass_time(ts['end'])
                }
                ass_timestamps.append(ass_ts)
            
            # 写入ASS文件
            ASSWriter.write_ass_file(
                output_ass,
                ass_timestamps,
                title=self.config.subtitle_title,
                resolution=self.config.resolution,
                style_config=self.config.style_config
            )
            
            return True
            
        except Exception as e:
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='自动生成ASS字幕文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认配置
  python main.py
  
  # 使用自定义配置文件
  python main.py -c my_config.yaml
  
  # 直接指定输入输出文件
  python main.py -i input.mp4 -o output.ass
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        type=str,
        default=None,
        help='配置文件路径（支持.yaml/.yml/.json格式）'
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        default=None,
        help='输入视频/音频文件路径（覆盖配置文件中的设置）'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='输出ASS字幕文件路径（覆盖配置文件中的设置）'
    )
    
    parser.add_argument(
        '-w', '--wav',
        type=str,
        default=None,
        help='输出WAV音频文件路径（覆盖配置文件中的设置）'
    )
    
    args = parser.parse_args()
    
    try:
        # 加载配置
        config = load_config(args.config)
        
        # 命令行参数覆盖配置文件
        if args.input:
            config._config['paths']['input_file'] = args.input
        if args.output:
            config._config['paths']['output_ass'] = args.output
        if args.wav:
            config._config['paths']['output_wav'] = args.wav
        
        # 创建生成器并执行
        generator = ASSGenerator(config)
        success = generator.generate()
        
        # 返回状态码
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

