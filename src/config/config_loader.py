"""
配置加载器
加载和验证配置文件
"""
import os
import sys
from pathlib import Path

# 添加父目录到路径以便导入util模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from util.file_io import ConfigReader


class Config:
    """配置类"""
    
    def __init__(self, config_dict):
        """
        从配置字典初始化配置对象
        
        Args:
            config_dict: 配置字典
        """
        self._config = config_dict
        
    def get(self, key_path, default=None):
        """
        获取配置值，支持点号分隔的路径
        
        Args:
            key_path: 配置键路径，例如 "vad.threshold"
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    @property
    def input_file(self):
        return self.get('paths.input_file')
    
    @property
    def output_wav(self):
        return self.get('paths.output_wav')
    
    @property
    def output_ass(self):
        return self.get('paths.output_ass')
    
    @property
    def sample_rate(self):
        return self.get('audio.sample_rate', 16000)
    
    @property
    def ffmpeg_path(self):
       path = self.get('audio.ffmpeg_path', 'ffmpeg')
       # 如果配置文件中显式设置为None或空字符串，使用默认值'ffmpeg'
       return path if path else 'ffmpeg'
    
    @property
    def use_onnx(self):
        return self.get('vad.use_onnx', True)
    
    @property
    def vad_threshold(self):
        return self.get('vad.threshold', 0.5)
    
    @property
    def min_speech_duration_ms(self):
        return self.get('vad.min_speech_duration_ms', 250)
    
    @property
    def max_speech_duration_s(self):
        value = self.get('vad.max_speech_duration_s', float('inf'))
        # 处理YAML中的.inf表示
        if value == '.inf':
            return float('inf')
        return float(value)
    
    @property
    def min_silence_duration_ms(self):
        return self.get('vad.min_silence_duration_ms', 100)
    
    @property
    def speech_pad_ms(self):
        return self.get('vad.speech_pad_ms', 30)
    
    @property
    def subtitle_title(self):
        return self.get('subtitle.title', '自动生成字幕')
    
    @property
    def resolution(self):
        width = self.get('subtitle.resolution.width', 1280)
        height = self.get('subtitle.resolution.height', 720)
        return (width, height)
    
    @property
    def merge_gap_threshold(self):
        """时间戳合并间隔阈值（秒）"""
        return self.get('subtitle.merge_gap_threshold', 1.0)
    
    @property
    def merge_min_gap(self):
        """时间戳最小间隔（秒）"""
        return self.get('subtitle.merge_min_gap', 0.5)
    
    @property
    def merge_max_duration(self):
        """单个字幕最大时长（秒）"""
        return self.get('subtitle.merge_max_duration', 15.0)
    
    @property
    def style_config(self):
        """获取ASS样式配置"""
        style = self.get('subtitle.style', {})
        if not style:
            return None
        
        # 转换为ASS格式的配置
        return {
            'Name': style.get('name', 'Default'),
            'Fontname': style.get('fontname', 'Microsoft YaHei'),
            'Fontsize': style.get('fontsize', 48),
            'PrimaryColour': style.get('primary_colour', '&H00FFFFFF'),
            'SecondaryColour': style.get('secondary_colour', '&H000000FF'),
            'OutlineColour': style.get('outline_colour', '&H00000000'),
            'BackColour': style.get('back_colour', '&H80000000'),
            'Bold': style.get('bold', 0),
            'Italic': style.get('italic', 0),
            'Underline': style.get('underline', 0),
            'StrikeOut': style.get('strikeout', 0),
            'ScaleX': style.get('scale_x', 100),
            'ScaleY': style.get('scale_y', 100),
            'Spacing': style.get('spacing', 0),
            'Angle': style.get('angle', 0),
            'BorderStyle': style.get('border_style', 1),
            'Outline': style.get('outline', 2),
            'Shadow': style.get('shadow', 3),
            'Alignment': style.get('alignment', 2),
            'MarginL': style.get('margin_l', 10),
            'MarginR': style.get('margin_r', 10),
            'MarginV': style.get('margin_v', 25),
            'Encoding': style.get('encoding', 1)
        }


def load_config(config_path=None):
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，如果为None则使用默认配置
        
    Returns:
        Config: 配置对象
    """
    if config_path is None:
        # 使用默认配置文件
        config_path = Path(__file__).parent / 'default_config.yaml'
    
    config_dict = ConfigReader.read_config(str(config_path))
    return Config(config_dict)


if __name__ == '__main__':
    # 测试配置加载
    config = load_config()
    
    print("配置加载测试:")
    print(f"输入文件: {config.input_file}")
    print(f"输出WAV: {config.output_wav}")
    print(f"输出ASS: {config.output_ass}")
    print(f"采样率: {config.sample_rate}")
    print(f"VAD阈值: {config.vad_threshold}")
    print(f"使用ONNX: {config.use_onnx}")
    print(f"分辨率: {config.resolution}")
    print(f"字幕标题: {config.subtitle_title}")

