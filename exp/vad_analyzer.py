"""
VAD分析器
用于分析Silero VAD的原始输出概率值和时间戳
直接使用src模块的VAD处理器
"""
import torch
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
import sys

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from vad import VADProcessor
    from util import AudioExtractor
    SILERO_AVAILABLE = True
except ImportError:
    SILERO_AVAILABLE = False
    print("警告: VAD模块不可用")


def extract_audio_from_video(video_path: str, output_wav: str, 
                             ffmpeg_path: str = "ffmpeg",
                             sample_rate: int = 16000) -> bool:
    """
    从视频文件中提取音频
    
    Args:
        video_path: 视频文件路径
        output_wav: 输出WAV文件路径
        ffmpeg_path: FFmpeg可执行文件路径
        sample_rate: 采样率
        
    Returns:
        bool: 是否成功
    """
    try:
        extractor = AudioExtractor(ffmpeg_path=ffmpeg_path)
        return extractor.extract_audio(video_path, output_wav, sample_rate)
    except Exception as e:
        print(f"音频提取失败: {e}")
        return False


class VADAnalyzer:
    """VAD分析器，使用src/vad模块"""
    
    def __init__(self, use_onnx: bool = True, threshold: float = 0.5,
                 min_speech_duration_ms: int = 250,
                 max_speech_duration_s: float = 15.0,
                 min_silence_duration_ms: int = 1000,
                 speech_pad_ms: int = 30):
        """
        初始化VAD分析器
        
        Args:
            use_onnx: 是否使用ONNX模型
            threshold: 语音检测阈值
            min_speech_duration_ms: 最小语音持续时间
            max_speech_duration_s: 最大语音持续时间
            min_silence_duration_ms: 最小静音持续时间
            speech_pad_ms: 语音前后填充时间
        """
        if not SILERO_AVAILABLE:
            raise ImportError("VAD模块不可用")
        
        self.vad_processor = VADProcessor(
            use_onnx=use_onnx,
            threshold=threshold,
            min_speech_duration_ms=min_speech_duration_ms,
            max_speech_duration_s=max_speech_duration_s,
            min_silence_duration_ms=min_silence_duration_ms,
            speech_pad_ms=speech_pad_ms
        )
        self.sampling_rate = 16000
    
    def detect_speech(self, audio_path: str) -> List[Dict[str, float]]:
        """
        检测语音片段
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            List[Dict]: 时间戳列表
        """
        return self.vad_processor.detect_speech(audio_path, 
                                               sampling_rate=self.sampling_rate,
                                               return_seconds=True)
    
    def create_with_threshold(self, threshold: float) -> 'VADAnalyzer':
        """
        创建使用指定阈值的新分析器实例
        
        Args:
            threshold: 新的阈值
            
        Returns:
            VADAnalyzer: 新的分析器实例
        """
        return VADAnalyzer(
            use_onnx=self.vad_processor.use_onnx,
            threshold=threshold,
            min_speech_duration_ms=self.vad_processor.min_speech_duration_ms,
            max_speech_duration_s=self.vad_processor.max_speech_duration_s,
            min_silence_duration_ms=self.vad_processor.min_silence_duration_ms,
            speech_pad_ms=self.vad_processor.speech_pad_ms
        )


if __name__ == '__main__':
    print("VAD分析器模块")
    print("=" * 60)
    print("功能:")
    print("  1. 从视频文件提取音频")
    print("  2. 使用VAD检测语音片段")
    print("  3. 支持不同阈值的VAD配置")
    print("\n使用示例:")
    print("  # 提取音频")
    print("  extract_audio_from_video('video.mp4', 'audio.wav')")
    print("  ")
    print("  # 创建VAD分析器")
    print("  analyzer = VADAnalyzer(threshold=0.5)")
    print("  timestamps = analyzer.detect_speech('audio.wav')")
    print("  ")
    print("  # 使用不同阈值")
    print("  analyzer2 = analyzer.create_with_threshold(0.3)")
    print("  timestamps2 = analyzer2.detect_speech('audio.wav')")

