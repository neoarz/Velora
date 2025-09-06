#!/usr/bin/env python3

import os
import sys
import subprocess
import ffmpeg
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

class FFmpegUtils:
    """Utility class for FFmpeg operations and video processing"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.ffprobe_path = self._find_ffprobe()
    
    def _find_ffmpeg(self) -> str:
        """Find FFmpeg executable"""
        common_paths = [
            'ffmpeg',
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
            'ffmpeg.exe'
        ]
        
        for path in common_paths:
            if self._check_executable(path):
                return path
        
        # Check if it's in PATH
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
            return 'ffmpeg'
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[WARNING] FFmpeg not found. Some features may be limited.")
            print("Install FFmpeg: https://ffmpeg.org/download.html")
            return None
    
    def _find_ffprobe(self) -> str:
        """Find FFprobe executable"""
        common_paths = [
            'ffprobe',
            '/usr/bin/ffprobe', 
            '/usr/local/bin/ffprobe',
            'ffprobe.exe'
        ]
        
        for path in common_paths:
            if self._check_executable(path):
                return path
        
        # Check if it's in PATH
        try:
            subprocess.run(['ffprobe', '-version'],
                         capture_output=True, check=True)
            return 'ffprobe'
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def _check_executable(self, path: str) -> bool:
        """Check if executable exists and works"""
        try:
            subprocess.run([path, '-version'],
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def is_available(self) -> bool:
        """Check if FFmpeg is available"""
        return self.ffmpeg_path is not None
    
    def get_video_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed video information using FFprobe"""
        if not self.ffprobe_path:
            return {}
        
        try:
            probe = ffmpeg.probe(file_path)
            video_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'video'), None)
            audio_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'audio'), None)
            
            info = {
                'format': probe['format']['format_name'],
                'duration': float(probe['format']['duration']),
                'size': int(probe['format']['size']),
                'bitrate': int(probe['format']['bit_rate'])
            }
            
            if video_stream:
                info.update({
                    'video_codec': video_stream['codec_name'],
                    'width': int(video_stream['width']),
                    'height': int(video_stream['height']),
                    'fps': eval(video_stream['r_frame_rate']),
                    'video_bitrate': int(video_stream.get('bit_rate', 0))
                })
            
            if audio_stream:
                info.update({
                    'audio_codec': audio_stream['codec_name'],
                    'audio_bitrate': int(audio_stream.get('bit_rate', 0)),
                    'sample_rate': int(audio_stream['sample_rate']),
                    'channels': int(audio_stream['channels'])
                })
            
            return info
            
        except Exception as e:
            print(f"[WARNING] Could not get video info: {e}")
            return {}
    
    def convert_video(self, input_path: str, output_path: str, 
                     codec: str = 'libx264', 
                     quality: str = 'medium',
                     audio_codec: str = 'aac') -> bool:
        """Convert video to different format/codec"""
        if not self.is_available():
            print("[ERROR] FFmpeg not available for conversion")
            return False
        
        try:
            stream = ffmpeg.input(input_path)
            
            # Video encoding options based on quality
            video_opts = self._get_video_encoding_options(codec, quality)
            audio_opts = {'acodec': audio_codec}
            
            stream = ffmpeg.output(stream, output_path, **video_opts, **audio_opts)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            print(f"[SUCCESS] Converted video to: {output_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Video conversion failed: {e}")
            return False
    
    def extract_audio(self, input_path: str, output_path: str, 
                     format: str = 'mp3', quality: str = '192k') -> bool:
        """Extract audio from video file"""
        if not self.is_available():
            print("[ERROR] FFmpeg not available for audio extraction")
            return False
        
        try:
            stream = ffmpeg.input(input_path)
            
            audio_opts = {
                'acodec': 'libmp3lame' if format == 'mp3' else 'libvorbis',
                'audio_bitrate': quality,
                'vn': None  # No video
            }
            
            stream = ffmpeg.output(stream, output_path, **audio_opts)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            print(f"[SUCCESS] Extracted audio to: {output_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Audio extraction failed: {e}")
            return False
    
    def trim_video(self, input_path: str, output_path: str,
                  start_time: str, duration: str = None, end_time: str = None) -> bool:
        """Trim video to specified time range"""
        if not self.is_available():
            print("[ERROR] FFmpeg not available for trimming")
            return False
        
        try:
            stream = ffmpeg.input(input_path, ss=start_time)
            
            if duration:
                stream = ffmpeg.output(stream, output_path, t=duration, c='copy')
            elif end_time:
                stream = ffmpeg.output(stream, output_path, to=end_time, c='copy')
            else:
                stream = ffmpeg.output(stream, output_path, c='copy')
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            print(f"[SUCCESS] Trimmed video to: {output_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Video trimming failed: {e}")
            return False
    
    def resize_video(self, input_path: str, output_path: str,
                    width: int, height: int = None, 
                    maintain_aspect: bool = True) -> bool:
        """Resize video to specified dimensions"""
        if not self.is_available():
            print("[ERROR] FFmpeg not available for resizing")
            return False
        
        try:
            stream = ffmpeg.input(input_path)
            
            if maintain_aspect and height is None:
                # Calculate height maintaining aspect ratio
                scale_filter = f'scale={width}:-1'
            elif maintain_aspect and width is None:
                scale_filter = f'scale=-1:{height}'
            else:
                scale_filter = f'scale={width}:{height}'
            
            stream = ffmpeg.filter(stream, 'scale', scale_filter)
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            print(f"[SUCCESS] Resized video to: {output_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Video resizing failed: {e}")
            return False
    
    def merge_videos(self, video_paths: List[str], output_path: str) -> bool:
        """Merge multiple videos into one"""
        if not self.is_available():
            print("[ERROR] FFmpeg not available for merging")
            return False
        
        if len(video_paths) < 2:
            print("[ERROR] Need at least 2 videos to merge")
            return False
        
        try:
            # Create input streams
            inputs = [ffmpeg.input(path) for path in video_paths]
            
            # Concatenate videos
            joined = ffmpeg.concat(*inputs, v=1, a=1)
            stream = ffmpeg.output(joined, output_path)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            print(f"[SUCCESS] Merged videos to: {output_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Video merging failed: {e}")
            return False
    
    def add_watermark(self, input_path: str, output_path: str,
                     watermark_path: str, position: str = 'bottom-right',
                     opacity: float = 0.5) -> bool:
        """Add watermark to video"""
        if not self.is_available():
            print("[ERROR] FFmpeg not available for watermarking")
            return False
        
        try:
            main = ffmpeg.input(input_path)
            watermark = ffmpeg.input(watermark_path)
            
            # Position mapping
            positions = {
                'top-left': '10:10',
                'top-right': 'W-w-10:10',
                'bottom-left': '10:H-h-10',
                'bottom-right': 'W-w-10:H-h-10',
                'center': '(W-w)/2:(H-h)/2'
            }
            
            pos = positions.get(position, positions['bottom-right'])
            
            # Apply watermark with opacity
            watermark = ffmpeg.filter(watermark, 'format', 'yuva420p')
            watermark = ffmpeg.filter(watermark, 'colorchannelmixer', aa=opacity)
            
            stream = ffmpeg.overlay(main, watermark, x=pos.split(':')[0], y=pos.split(':')[1])
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            print(f"[SUCCESS] Added watermark to: {output_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Watermarking failed: {e}")
            return False
    
    def _get_video_encoding_options(self, codec: str, quality: str) -> Dict[str, Any]:
        """Get video encoding options based on codec and quality"""
        options = {'vcodec': codec}
        
        if codec == 'libx264':
            quality_map = {
                'low': {'crf': 28, 'preset': 'fast'},
                'medium': {'crf': 23, 'preset': 'medium'},
                'high': {'crf': 18, 'preset': 'slow'},
                'ultra': {'crf': 15, 'preset': 'veryslow'}
            }
        elif codec == 'libx265':
            quality_map = {
                'low': {'crf': 32, 'preset': 'fast'},
                'medium': {'crf': 28, 'preset': 'medium'},
                'high': {'crf': 23, 'preset': 'slow'},
                'ultra': {'crf': 18, 'preset': 'veryslow'}
            }
        else:
            return options
        
        options.update(quality_map.get(quality, quality_map['medium']))
        return options
    
    def create_gif(self, input_path: str, output_path: str,
                  start_time: str = '0', duration: str = '10',
                  fps: int = 15, width: int = 320) -> bool:
        """Create GIF from video"""
        if not self.is_available():
            print("[ERROR] FFmpeg not available for GIF creation")
            return False
        
        try:
            stream = ffmpeg.input(input_path, ss=start_time, t=duration)
            stream = ffmpeg.filter(stream, 'fps', fps=fps, round='up')
            stream = ffmpeg.filter(stream, 'scale', width, -1)
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            print(f"[SUCCESS] Created GIF: {output_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] GIF creation failed: {e}")
            return False
    
    def get_thumbnail(self, input_path: str, output_path: str,
                     time: str = '00:00:01') -> bool:
        """Extract thumbnail from video at specified time"""
        if not self.is_available():
            print("[ERROR] FFmpeg not available for thumbnail extraction")
            return False
        
        try:
            stream = ffmpeg.input(input_path, ss=time)
            stream = ffmpeg.output(stream, output_path, vframes=1)
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            print(f"[SUCCESS] Extracted thumbnail to: {output_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Thumbnail extraction failed: {e}")
            return False
