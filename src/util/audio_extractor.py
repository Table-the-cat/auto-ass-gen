"""
音频提取工具
使用FFmpeg将视频/音频文件转换为16kHz采样率的wav文件
"""
import subprocess
import os
from pathlib import Path


class AudioExtractor:
    """音频提取器，使用FFmpeg进行音频提取和转换"""
    
    def __init__(self, ffmpeg_path='ffmpeg'):
        """
        初始化音频提取器
        
        Args:
            ffmpeg_path: FFmpeg可执行文件路径，默认为'ffmpeg'（假设在系统PATH中）
        """
        # 如果传入的是None或空字符串，使用默认值'ffmpeg'
        self.ffmpeg_path = ffmpeg_path if ffmpeg_path else 'ffmpeg'
        
    def extract_audio(self, input_path, output_path, sample_rate=16000):
        """
        从视频/音频文件中提取音频并转换为指定采样率的wav文件
        
        Args:
            input_path: 输入文件路径（视频或音频）
            output_path: 输出wav文件路径
            sample_rate: 采样率，默认16000Hz
            
        Returns:
            bool: 是否成功提取
            
        Raises:
            FileNotFoundError: 输入文件不存在
            RuntimeError: FFmpeg执行失败
        """
        # 检查输入文件是否存在
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 构建FFmpeg命令
        # -i: 输入文件
        # -ar: 设置采样率
        # -ac: 设置声道数为1（单声道）
        # -y: 覆盖输出文件
        # -vn: 不处理视频
        cmd = [
            self.ffmpeg_path,
            '-i', input_path,
            '-ar', str(sample_rate),
            '-ac', '1',
            '-y',
            '-vn',
            output_path
        ]
        
        try:
            # 执行FFmpeg命令
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # 检查输出文件是否成功生成
            if os.path.exists(output_path):
                print(f"音频提取成功: {output_path}")
                return True
            else:
                raise RuntimeError("FFmpeg执行完成但未生成输出文件")
                
        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg执行失败:\n{e.stderr}"
            raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"音频提取过程中发生错误: {str(e)}")
    
    def check_ffmpeg_available(self):
        """
        检查FFmpeg是否可用
        
        Returns:
            bool: FFmpeg是否可用
        """
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False


if __name__ == '__main__':
    # 测试代码
    extractor = AudioExtractor()
    if extractor.check_ffmpeg_available():
        print("FFmpeg 可用")
    else:
        print("FFmpeg 不可用，请确保已安装FFmpeg并添加到系统PATH")

