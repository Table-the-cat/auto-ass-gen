"""
文件IO工具
处理配置文件读取和ASS文件写入
"""
import json
import yaml
import os
from pathlib import Path


class ConfigReader:
    """配置文件读取器，支持JSON和YAML格式"""
    
    @staticmethod
    def read_config(config_path):
        """
        读取配置文件
        
        Args:
            config_path: 配置文件路径，支持.json, .yaml, .yml格式
            
        Returns:
            dict: 配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 不支持的文件格式
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        file_ext = os.path.splitext(config_path)[1].lower()
        
        if file_ext == '.json':
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif file_ext in ['.yaml', '.yml']:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            raise ValueError(f"不支持的配置文件格式: {file_ext}")
    
    @staticmethod
    def write_config(config_path, config_dict):
        """
        写入配置文件
        
        Args:
            config_path: 配置文件路径
            config_dict: 配置字典
        """
        file_ext = os.path.splitext(config_path)[1].lower()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(config_path) or '.', exist_ok=True)
        
        if file_ext == '.json':
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
        elif file_ext in ['.yaml', '.yml']:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, allow_unicode=True, default_flow_style=False)
        else:
            raise ValueError(f"不支持的配置文件格式: {file_ext}")


class ASSWriter:
    """ASS字幕文件写入器"""
    
    @staticmethod
    def write_ass_file(output_path, timestamps, title="自动生成字幕", 
                       resolution=(1280, 720), style_config=None):
        """
        写入ASS字幕文件
        
        Args:
            output_path: 输出ASS文件路径
            timestamps: 时间戳列表，格式为 [{'start': 'H:MM:SS.ss', 'end': 'H:MM:SS.ss'}, ...]
            title: 字幕标题
            resolution: 视频分辨率 (宽, 高)
            style_config: 样式配置字典，如果为None则使用默认样式
        """
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        # 默认样式配置
        if style_config is None:
            style_config = {
                'Name': 'Default',
                'Fontname': 'Microsoft YaHei',
                'Fontsize': 48,
                'PrimaryColour': '&H00FFFFFF',  # 白色
                'SecondaryColour': '&H000000FF',  # 红色
                'OutlineColour': '&H00000000',  # 黑色边框
                'BackColour': '&H80000000',  # 半透明黑色背景
                'Bold': 0,
                'Italic': 0,
                'Underline': 0,
                'StrikeOut': 0,
                'ScaleX': 100,
                'ScaleY': 100,
                'Spacing': 0,
                'Angle': 0,
                'BorderStyle': 1,
                'Outline': 2,
                'Shadow': 3,
                'Alignment': 2,  # 底部居中
                'MarginL': 10,
                'MarginR': 10,
                'MarginV': 25,
                'Encoding': 1
            }
        
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            # 写入脚本信息
            f.write("[Script Info]\n")
            f.write("; 由 auto-ass-gen 自动生成\n")
            f.write(f"Title: {title}\n")
            f.write("ScriptType: v4.00+\n")
            f.write(f"PlayResX: {resolution[0]}\n")
            f.write(f"PlayResY: {resolution[1]}\n")
            f.write("Timer: 100.0000\n")
            f.write("\n")
            
            # 写入样式定义
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
                   "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
                   "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
                   "Alignment, MarginL, MarginR, MarginV, Encoding\n")
            
            style_line = (f"Style: {style_config['Name']},{style_config['Fontname']},"
                         f"{style_config['Fontsize']},{style_config['PrimaryColour']},"
                         f"{style_config['SecondaryColour']},{style_config['OutlineColour']},"
                         f"{style_config['BackColour']},{style_config['Bold']},"
                         f"{style_config['Italic']},{style_config['Underline']},"
                         f"{style_config['StrikeOut']},{style_config['ScaleX']},"
                         f"{style_config['ScaleY']},{style_config['Spacing']},"
                         f"{style_config['Angle']},{style_config['BorderStyle']},"
                         f"{style_config['Outline']},{style_config['Shadow']},"
                         f"{style_config['Alignment']},{style_config['MarginL']},"
                         f"{style_config['MarginR']},{style_config['MarginV']},"
                         f"{style_config['Encoding']}\n")
            f.write(style_line)
            f.write("\n")
            
            # 写入事件（字幕）
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            
            for i, ts in enumerate(timestamps):
                # Dialogue: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text
                dialogue_line = (f"Dialogue: 0,{ts['start']},{ts['end']},Default,,"
                               f"0,0,0,,Test SubTitle {i}\n")
                f.write(dialogue_line)
        
        print(f"ASS字幕文件已生成: {output_path}")


if __name__ == '__main__':
    # 测试配置读写
    print("测试配置文件读写...")
    test_config = {
        'input_path': 'test.mp4',
        'output_path': 'output/test.wav',
        'sample_rate': 16000
    }
    
    # 写入JSON配置
    ConfigReader.write_config('test_config.json', test_config)
    read_config = ConfigReader.read_config('test_config.json')
    print(f"读取的配置: {read_config}")
    
    # 测试ASS文件写入
    print("\n测试ASS文件写入...")
    test_timestamps = [
        {'start': '0:00:00.50', 'end': '0:00:03.20'},
        {'start': '0:00:04.10', 'end': '0:00:07.80'},
        {'start': '0:00:09.00', 'end': '0:00:12.50'}
    ]
    ASSWriter.write_ass_file('test_output.ass', test_timestamps)
    print("测试完成！")

