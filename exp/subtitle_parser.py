"""
字幕文件解析器
支持解析ASS、SRT等格式的字幕文件，提取时间戳
"""
import re
from pathlib import Path
from typing import List, Dict, Tuple


def ass_time_to_seconds(time_str: str) -> float:
    """
    将ASS时间格式转换为秒
    
    Args:
        time_str: ASS格式时间字符串，例如 "0:02:30.50"
        
    Returns:
        float: 秒数
    """
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    sec_parts = parts[2].split('.')
    seconds = int(sec_parts[0])
    centiseconds = int(sec_parts[1]) if len(sec_parts) > 1 else 0
    
    return hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0


def srt_time_to_seconds(time_str: str) -> float:
    """
    将SRT时间格式转换为秒
    
    Args:
        time_str: SRT格式时间字符串，例如 "00:02:30,500"
        
    Returns:
        float: 秒数
    """
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    
    return hours * 3600 + minutes * 60 + seconds


class SubtitleParser:
    """字幕解析器基类"""
    
    @staticmethod
    def parse_file(file_path: str) -> List[Dict[str, float]]:
        """
        解析字幕文件，返回时间戳列表
        
        Args:
            file_path: 字幕文件路径
            
        Returns:
            List[Dict]: 时间戳列表，格式 [{'start': float, 'end': float}, ...]
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == '.ass':
            return SubtitleParser.parse_ass(file_path)
        elif suffix == '.srt':
            return SubtitleParser.parse_srt(file_path)
        else:
            raise ValueError(f"不支持的字幕格式: {suffix}")
    
    @staticmethod
    def parse_ass(file_path: str) -> List[Dict[str, float]]:
        """
        解析ASS字幕文件
        
        Args:
            file_path: ASS文件路径
            
        Returns:
            List[Dict]: 时间戳列表
        """
        timestamps = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
        
        in_events = False
        for line in lines:
            line = line.strip()
            
            if line.startswith('[Events]'):
                in_events = True
                continue
            
            if in_events and line.startswith('Dialogue:'):
                # ASS格式: Dialogue: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
                parts = line.split(',', 9)
                if len(parts) >= 3:
                    start_time = ass_time_to_seconds(parts[1].strip())
                    end_time = ass_time_to_seconds(parts[2].strip())
                    timestamps.append({'start': start_time, 'end': end_time})
        
        return sorted(timestamps, key=lambda x: x['start'])
    
    @staticmethod
    def parse_srt(file_path: str) -> List[Dict[str, float]]:
        """
        解析SRT字幕文件
        
        Args:
            file_path: SRT文件路径
            
        Returns:
            List[Dict]: 时间戳列表
        """
        timestamps = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        
        # SRT格式使用空行分隔每个字幕块
        blocks = content.strip().split('\n\n')
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 2:
                # 第二行是时间戳，格式: 00:02:30,500 --> 00:02:33,100
                time_line = lines[1]
                match = re.match(r'(\S+)\s*-->\s*(\S+)', time_line)
                if match:
                    start_str, end_str = match.groups()
                    start_time = srt_time_to_seconds(start_str)
                    end_time = srt_time_to_seconds(end_str)
                    timestamps.append({'start': start_time, 'end': end_time})
        
        return sorted(timestamps, key=lambda x: x['start'])
    
    @staticmethod
    def extract_gaps(timestamps: List[Dict[str, float]]) -> List[float]:
        """
        提取相邻字幕之间的间隔
        
        Args:
            timestamps: 时间戳列表
            
        Returns:
            List[float]: 间隔列表（秒）
        """
        gaps = []
        for i in range(len(timestamps) - 1):
            gap = timestamps[i + 1]['start'] - timestamps[i]['end']
            if gap > 0:  # 排除重叠和零间隔
                gaps.append(gap)
        return gaps
    
    @staticmethod
    def find_merged_timestamps(timestamps: List[Dict[str, float]], 
                               tolerance: float = 0.05) -> List[float]:
        """
        找到首尾相连的字幕的连接点时间戳
        
        Args:
            timestamps: 时间戳列表
            tolerance: 容差（秒），小于此值视为相连
            
        Returns:
            List[float]: 连接点时间戳列表
        """
        merge_points = []
        for i in range(len(timestamps) - 1):
            gap = timestamps[i + 1]['start'] - timestamps[i]['end']
            if abs(gap) <= tolerance:
                # 首尾相连，记录连接点（A的end时间）
                merge_points.append(timestamps[i]['end'])
        return merge_points


if __name__ == '__main__':
    # 测试代码
    print("字幕解析器模块")
    print("=" * 60)
    print("功能:")
    print("  1. 解析ASS/SRT字幕文件")
    print("  2. 提取时间戳")
    print("  3. 分析间隔和连接点")
    print("\n使用示例:")
    print("  parser = SubtitleParser()")
    print("  timestamps = parser.parse_file('subtitle.ass')")
    print("  gaps = parser.extract_gaps(timestamps)")
    print("  merge_points = parser.find_merged_timestamps(timestamps)")

