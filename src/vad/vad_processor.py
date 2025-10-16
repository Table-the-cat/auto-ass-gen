"""
语音活动检测模块
基于Silero VAD实现语音检测功能
"""
import torch
import torchaudio
import warnings
from pathlib import Path

try:
    from silero_vad import load_silero_vad, get_speech_timestamps
    SILERO_AVAILABLE = True
except ImportError:
    warnings.warn(
        "无法导入silero_vad，请安装: pip install silero-vad\n"
        "或者从源码安装: pip install git+https://github.com/snakers4/silero-vad.git"
    )
    SILERO_AVAILABLE = False


def read_audio(path: str, sampling_rate: int = 16000) -> torch.Tensor:
    """
    读取音频文件并转换为指定采样率
    兼容新版本的torchaudio (2.x+)
    
    Args:
        path: 音频文件路径
        sampling_rate: 目标采样率
        
    Returns:
        torch.Tensor: 单声道音频张量
    """
    # 尝试不同的后端加载音频
    # torchaudio 2.x 的 load() 函数不再接受 backend 参数
    # 需要使用 torchaudio.backend 来设置
    
    backends_to_try = []
    
    # 检查可用的后端
    try:
        import soundfile
        backends_to_try.append('soundfile')
    except ImportError:
        pass
    
    # 添加其他可能的后端
    backends_to_try.extend(['sox', 'sox_io'])
    
    # 尝试加载音频
    wav = None
    sr = None
    last_error = None
    
    for backend_name in backends_to_try:
        try:
            # 设置后端
            torchaudio.set_audio_backend(backend_name)
            # 加载音频
            wav, sr = torchaudio.load(path)
            break
        except Exception as e:
            last_error = e
            continue
    
    # 如果所有后端都失败，尝试直接使用 soundfile
    if wav is None:
        try:
            import soundfile as sf
            import numpy as np
            
            # 使用 soundfile 直接读取
            data, sr = sf.read(path, dtype='float32')
            
            # 转换为 torch tensor
            if len(data.shape) == 1:
                # 单声道
                wav = torch.from_numpy(data).unsqueeze(0)
            else:
                # 多声道，转置为 (channels, samples)
                wav = torch.from_numpy(data.T)
                
        except Exception as e:
            raise RuntimeError(
                f"无法读取音频文件: {path}\n"
                f"最后的错误: {last_error}\n"
                f"请确保已安装 soundfile: pip install soundfile"
            ) from e
    
    # 转换为单声道
    if wav.size(0) > 1:
        wav = wav.mean(dim=0, keepdim=True)
    
    # 重采样到目标采样率
    if sr != sampling_rate:
        resampler = torchaudio.transforms.Resample(
            orig_freq=sr,
            new_freq=sampling_rate
        )
        wav = resampler(wav)
    
    # 返回一维张量
    return wav.squeeze(0)


class VADProcessor:
    """语音活动检测处理器"""
    
    def __init__(self, use_onnx=True, threshold=0.5, min_speech_duration_ms=250,
                 max_speech_duration_s=float('inf'), min_silence_duration_ms=100,
                 speech_pad_ms=30):
        """
        初始化VAD处理器
        
        Args:
            use_onnx: 是否使用ONNX模型（推荐）
            threshold: 语音检测阈值，默认0.5
            min_speech_duration_ms: 最小语音持续时间（毫秒）
            max_speech_duration_s: 最大语音持续时间（秒）
            min_silence_duration_ms: 最小静音持续时间（毫秒）
            speech_pad_ms: 语音片段前后填充时间（毫秒）
        """
        if not SILERO_AVAILABLE:
            raise ImportError("Silero VAD不可用，请检查安装")
        
        self.use_onnx = use_onnx
        self.threshold = threshold
        self.min_speech_duration_ms = min_speech_duration_ms
        self.max_speech_duration_s = max_speech_duration_s
        self.min_silence_duration_ms = min_silence_duration_ms
        self.speech_pad_ms = speech_pad_ms
        
        # 加载模型
        print(f"加载Silero VAD模型 (ONNX: {use_onnx})...")
        self.model = load_silero_vad(onnx=use_onnx)
        print("模型加载成功")
    
    def detect_speech(self, audio_path, sampling_rate=16000, return_seconds=True):
        """
        检测音频中的语音片段
        
        Args:
            audio_path: 音频文件路径（wav格式，16kHz采样率）
            sampling_rate: 采样率，默认16000Hz
            return_seconds: 是否返回秒数（True）还是样本数（False）
            
        Returns:
            list: 语音时间戳列表
                格式: [{'start': 0.5, 'end': 3.2}, {'start': 4.1, 'end': 7.8}, ...]
                start和end单位为秒（如果return_seconds=True）
        """
        print(f"读取音频文件: {audio_path}")
        
        # 读取音频
        wav = read_audio(audio_path, sampling_rate=sampling_rate)
        
        print(f"音频长度: {len(wav)/sampling_rate:.2f}秒")
        print("开始语音检测...")
        
        # 检测语音
        speech_timestamps = get_speech_timestamps(
            wav,
            self.model,
            threshold=self.threshold,
            sampling_rate=sampling_rate,
            min_speech_duration_ms=self.min_speech_duration_ms,
            max_speech_duration_s=self.max_speech_duration_s,
            min_silence_duration_ms=self.min_silence_duration_ms,
            speech_pad_ms=self.speech_pad_ms,
            return_seconds=return_seconds
        )
        
        print(f"检测到 {len(speech_timestamps)} 个语音片段")
        
        return speech_timestamps
    
    def detect_speech_from_tensor(self, wav_tensor, sampling_rate=16000, return_seconds=True):
        """
        从音频张量检测语音片段
        
        Args:
            wav_tensor: 音频张量 (torch.Tensor)
            sampling_rate: 采样率
            return_seconds: 是否返回秒数
            
        Returns:
            list: 语音时间戳列表
        """
        speech_timestamps = get_speech_timestamps(
            wav_tensor,
            self.model,
            threshold=self.threshold,
            sampling_rate=sampling_rate,
            min_speech_duration_ms=self.min_speech_duration_ms,
            max_speech_duration_s=self.max_speech_duration_s,
            min_silence_duration_ms=self.min_silence_duration_ms,
            speech_pad_ms=self.speech_pad_ms,
            return_seconds=return_seconds
        )
        
        return speech_timestamps


if __name__ == '__main__':
    # 测试代码
    if SILERO_AVAILABLE:
        print("初始化VAD处理器...")
        processor = VADProcessor(use_onnx=True)
        print("✓ VAD处理器初始化成功")
        print("\n提示: 请提供音频文件路径进行测试")
        print("示例: processor.detect_speech('path/to/audio.wav')")
    else:
        print("✗ Silero VAD不可用")
        print("请安装: pip install silero-vad")

