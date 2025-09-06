#!/usr/bin/env python3

import subprocess
import os
import sys
import ffmpeg
from pathlib import Path
from .ffmpeg_utils import FFmpegUtils

class Downloader:
    def __init__(self, config):
        self.config = config
        self.yt_dlp_path = self._find_yt_dlp()
        self.ffmpeg = FFmpegUtils()

    def _find_yt_dlp(self):
        # Try common locations
        common_paths = [
            'yt-dlp',
            './yt-dlp',
            '/usr/local/bin/yt-dlp',
            '/usr/bin/yt-dlp',
            'yt-dlp.exe',  
        ]

        for path in common_paths:
            if self._check_yt_dlp(path):
                return path

        # Check if it's in PATH
        try:
            subprocess.run(['yt-dlp', '--version'],
                         capture_output=True, check=True)
            return 'yt-dlp'
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[ERROR] yt-dlp not found. Please install yt-dlp:")
            print("   pip install yt-dlp")
            print("   or visit: https://github.com/yt-dlp/yt-dlp")
            sys.exit(1)

    def _check_yt_dlp(self, path):
        try:
            subprocess.run([path, '--version'],
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_format_options(self, choice):
        formats = {
            1: ['-f', 'bestvideo+bestaudio/best'],  # Best quality video + audio (no resolution limit)
            2: ['-x', '--audio-format', 'mp3', '--audio-quality', '192K'],  # Audio MP3
            3: ['-x', '--audio-format', 'best', '--audio-quality', '0'],  # Best audio
            4: ['-f', 'bestvideo+bestaudio/best', '--remux-video', 'mp4'],  # Video MP4 (no resolution limit)
            5: []  # Custom (will prompt for options)
        }
        return formats.get(choice, [])

    def _create_download_dir(self):
        download_dir = Path.home() / "Downloads" / "Velora"
        download_dir.mkdir(parents=True, exist_ok=True)
        return download_dir

    def download_with_options(self, url, resolution="best", include_audio=True, output_format="mp4", audio_only=False):
        """Download video with specific resolution, audio, and format options"""
        try:
            # Validate URL before attempting download
            if not self._is_valid_url(url):
                print("[ERROR] Invalid video URL. Please check the URL and try again.")
                return False
            
            download_dir = self._create_download_dir()
            
            # Handle audio-only downloads
            if audio_only:
                return self._download_audio_only(url, download_dir, output_format)
            
            # Build format string based on options
            format_opts = self._build_format_string(resolution, include_audio, output_format)

            # Base command
            cmd = [
                self.yt_dlp_path,
                '--no-playlist',  # Download single video
                '-o', str(download_dir / '%(title)s.%(ext)s'),  # Output template
                '--progress',
                '--no-warnings',
            ]

            # Add format options
            if format_opts:
                cmd.extend(format_opts)

            # Add URL
            cmd.append(url)

            print(f"Downloading to: {download_dir}")
            print(f"URL: {url}")
            print(f"Resolution: {resolution}")
            print(f"Audio: {'Yes' if include_audio else 'No'}")
            print(f"Format: {output_format.upper()}")
            print("Starting download...\n")

            # Run yt-dlp
            result = subprocess.run(
                cmd,
                cwd=str(download_dir),
                capture_output=False,  # Show progress in real-time
                text=True
            )

            if result.returncode == 0:
                print("\n[SUCCESS] Download completed successfully!")
                
                # Handle MOV format post-processing if needed
                if hasattr(self, '_desired_format') and self._desired_format == 'mov':
                    success = self._convert_to_mov(download_dir)
                    if not success:
                        print("[WARNING] MOV conversion failed, but original download succeeded")
                
                self._show_download_info(download_dir)
                return True
            else:
                print(f"\n[ERROR] Download failed with exit code: {result.returncode}")
                print("[ERROR] Download failed. Please check the URL and try again.")
                return False

        except Exception as e:
            print(f"\n[ERROR] Error during download: {e}")
            return False

    def _download_audio_only(self, url, download_dir, audio_format="mp3"):
        """Download audio only from video"""
        try:
            # Base command for audio extraction
            cmd = [
                self.yt_dlp_path,
                '--no-playlist',  # Download single video
                '-x',  # Extract audio
                '--audio-format', audio_format,
                '--audio-quality', '192K',  # Good quality
                '-o', str(download_dir / '%(title)s.%(ext)s'),  # Output template
                '--progress',
                '--no-warnings',
                url
            ]

            print(f"Downloading audio to: {download_dir}")
            print(f"URL: {url}")
            print(f"Format: {audio_format.upper()}")
            print("Starting audio download...\n")

            # Run yt-dlp
            result = subprocess.run(
                cmd,
                cwd=str(download_dir),
                capture_output=False,  # Show progress in real-time
                text=True
            )

            if result.returncode == 0:
                print("\n[SUCCESS] Audio download completed successfully!")
                self._show_download_info(download_dir)
                return True
            else:
                print(f"\n[ERROR] Audio download failed with exit code: {result.returncode}")
                print("[ERROR] Download failed. Please check the URL and try again.")
                return False

        except Exception as e:
            print(f"\n[ERROR] Error during audio download: {e}")
            return False

    def _convert_to_mov(self, download_dir):
        """Convert downloaded MP4 files to MOV format using FFmpeg"""
        try:
            # Find the most recently downloaded MP4 file
            mp4_files = list(download_dir.glob("*.mp4"))
            if not mp4_files:
                print("[WARNING] No MP4 file found for MOV conversion")
                return False
            
            # Get the most recent file
            latest_mp4 = max(mp4_files, key=lambda x: x.stat().st_mtime)
            mov_path = latest_mp4.with_suffix('.mov')
            
            print(f"Converting {latest_mp4.name} to MOV format...")
            
            # Use FFmpeg for conversion
            if self.ffmpeg.is_available():
                success = self._ffmpeg_convert_to_mov(str(latest_mp4), str(mov_path))
                if success:
                    # Remove the original MP4 file
                    latest_mp4.unlink()
                    print(f"[SUCCESS] Converted to {mov_path.name}")
                    return True
                else:
                    print("[ERROR] FFmpeg conversion to MOV failed")
                    return False
            else:
                print("[ERROR] FFmpeg not available for MOV conversion")
                return False
                
        except Exception as e:
            print(f"[ERROR] MOV conversion failed: {e}")
            return False

    def _ffmpeg_convert_to_mov(self, input_path, output_path):
        """Convert video to MOV format using FFmpeg with proper codec settings"""
        try:
            # Use stream copy for fast conversion when possible
            # MOV container typically works well with H.264 video and AAC audio
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(
                stream, 
                output_path,
                vcodec='copy',  # Copy video stream without re-encoding
                acodec='copy',  # Copy audio stream without re-encoding
                movflags='faststart'  # Optimize for web streaming
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            return True
            
        except Exception as e:
            # Stream copy failed, this is normal for some videos
            print("[INFO] Fast conversion not possible, re-encoding video for MOV compatibility...")
            
            # Fallback: Re-encode with H.264 and AAC (more compatible)
            try:
                stream = ffmpeg.input(input_path)
                stream = ffmpeg.output(
                    stream, 
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    crf=23,  # Good quality
                    preset='medium',
                    movflags='faststart'
                )
                
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
                return True
                
            except Exception as e2:
                print(f"[ERROR] FFmpeg MOV conversion failed: {e2}")
                return False

    def _build_format_string(self, resolution, include_audio, output_format="mp4"):
        """Build yt-dlp format string based on resolution, audio preferences, and output format"""
        # Build format selection based on resolution and audio
        if resolution == "best":
            if include_audio:
                format_string = 'bestvideo+bestaudio/best'
            else:
                format_string = 'bestvideo'
        else:
            # Specific resolution (1080p, 720p, 480p, 360p, 144p)
            height = resolution.replace('p', '')
            if include_audio:
                format_string = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
            else:
                format_string = f'bestvideo[height<={height}]'
        
        # Build command options
        cmd_opts = ['-f', format_string]
        
        # Store the desired output format for post-processing
        self._desired_format = output_format.lower() if output_format else 'mp4'
        
        # For MOV format, don't use --remux-video as it often fails
        # We'll handle MOV conversion using FFmpeg post-processing instead
        if output_format and output_format.lower() != 'webm' and output_format.lower() != 'mov':
            # Use --remux-video for container format conversion (no re-encoding)
            if output_format.lower() in ['mp4', 'mkv', 'avi']:
                cmd_opts.extend(['--remux-video', output_format.lower()])
            else:
                # For other formats, use --recode-video (re-encoding)
                cmd_opts.extend(['--recode-video', output_format.lower()])
        
        return cmd_opts

    def _show_download_info(self, download_dir):
        try:
            files = list(download_dir.glob("*"))
            if files:
                recent_files = sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
                print("Recent downloads:")
                for file in recent_files:
                    size = file.stat().st_size
                    size_mb = size / (1024 * 1024)
                    print(f"   • {file.name} ({size_mb:.1f} MB)")
        except Exception:
            pass  # Don't show download info if there's an error

    def get_video_info(self, url):
        try:
            # Basic URL validation
            if not self._is_valid_url(url):
                return {'error': 'invalid_url', 'message': 'Invalid video URL. Please check the URL and try again.'}
            
            cmd = [
                self.yt_dlp_path,
                '--no-download',
                '--print-json',
                '--no-warnings',
                url
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            import json
            info = json.loads(result.stdout)
            
            # Extract platform/source information
            platform = self._get_platform_from_url(url)
            if not platform:
                # Try to get it from yt-dlp info
                extractor = info.get('extractor', '')
                if extractor:
                    platform = self._format_platform_name(extractor)
                else:
                    platform = 'Unknown'
            
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration_string', 'Unknown'),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 'Unknown'),
                'platform': platform
            }

        except subprocess.CalledProcessError as e:
            # Handle yt-dlp specific errors
            if e.stderr:
                error_msg = e.stderr.strip()
                if "is not a valid URL" in error_msg or "Unsupported URL" in error_msg:
                    return {'error': 'invalid_url', 'message': 'Invalid video URL. Please check the URL and try again.'}
                elif "Video unavailable" in error_msg or "Private video" in error_msg:
                    return {'error': 'unavailable', 'message': 'Video is unavailable or private. Please try a different URL.'}
                elif "not found" in error_msg or "404" in error_msg:
                    return {'error': 'not_found', 'message': 'Video not found. Please check the URL and try again.'}
                else:
                    return {'error': 'unknown', 'message': f'Could not access video: {error_msg}'}
            return {'error': 'unknown', 'message': 'Could not get video info. Please check the URL and try again.'}
        except Exception as e:
            return {'error': 'unknown', 'message': f'Could not get video info: {str(e)}'}

    def _is_valid_url(self, url):
        """Basic URL validation"""
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        if not url:
            return False
            
        # Check if it looks like a URL
        if not (url.startswith('http://') or url.startswith('https://') or url.startswith('www.')):
            return False
            
        # Check for common video platforms
        valid_domains = [
            'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
            'twitch.tv', 'facebook.com', 'instagram.com', 'tiktok.com',
            'twitter.com', 'x.com', 'reddit.com', 'soundcloud.com'
        ]
        
        return any(domain in url.lower() for domain in valid_domains)

    def _get_platform_from_url(self, url):
        """Extract platform name from URL"""
        url_lower = url.lower()
        
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'YouTube'
        elif 'vimeo.com' in url_lower:
            return 'Vimeo'
        elif 'dailymotion.com' in url_lower:
            return 'Dailymotion'
        elif 'twitch.tv' in url_lower:
            return 'Twitch'
        elif 'facebook.com' in url_lower:
            return 'Facebook'
        elif 'instagram.com' in url_lower:
            return 'Instagram'
        elif 'tiktok.com' in url_lower:
            return 'TikTok'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'Twitter/X'
        elif 'reddit.com' in url_lower:
            return 'Reddit'
        elif 'soundcloud.com' in url_lower:
            return 'SoundCloud'
        else:
            return None

    def _format_platform_name(self, extractor):
        """Format platform name from yt-dlp extractor name"""
        extractor_lower = extractor.lower()
        
        platform_map = {
            'youtube': 'YouTube',
            'vimeo': 'Vimeo',
            'dailymotion': 'Dailymotion',
            'twitch': 'Twitch',
            'facebook': 'Facebook',
            'instagram': 'Instagram',
            'tiktok': 'TikTok',
            'twitter': 'Twitter/X',
            'reddit': 'Reddit',
            'soundcloud': 'SoundCloud',
            'generic': 'Web Video'
        }
        
        for key, value in platform_map.items():
            if key in extractor_lower:
                return value
        
        # If no match, capitalize the extractor name
        return extractor.capitalize()

    def post_process_video(self, file_path, operation, **kwargs):
        """Post-process downloaded video using FFmpeg"""
        if not self.ffmpeg.is_available():
            print("[WARNING] FFmpeg not available. Skipping post-processing.")
            return False
        
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"[ERROR] File not found: {file_path}")
            return False
        
        if operation == 'convert':
            output_path = file_path.with_suffix(f".{kwargs.get('format', 'mp4')}")
            return self.ffmpeg.convert_video(
                str(file_path), str(output_path),
                codec=kwargs.get('codec', 'libx264'),
                quality=kwargs.get('quality', 'medium')
            )
        
        elif operation == 'extract_audio':
            output_path = file_path.with_suffix(f".{kwargs.get('format', 'mp3')}")
            return self.ffmpeg.extract_audio(
                str(file_path), str(output_path),
                format=kwargs.get('format', 'mp3'),
                quality=kwargs.get('quality', '192k')
            )
        
        elif operation == 'resize':
            output_path = file_path.with_stem(f"{file_path.stem}_resized")
            return self.ffmpeg.resize_video(
                str(file_path), str(output_path),
                width=kwargs.get('width', 1280),
                height=kwargs.get('height'),
                maintain_aspect=kwargs.get('maintain_aspect', True)
            )
        
        elif operation == 'trim':
            output_path = file_path.with_stem(f"{file_path.stem}_trimmed")
            return self.ffmpeg.trim_video(
                str(file_path), str(output_path),
                start_time=kwargs.get('start_time', '0'),
                duration=kwargs.get('duration'),
                end_time=kwargs.get('end_time')
            )
        
        elif operation == 'thumbnail':
            output_path = file_path.with_suffix('.jpg')
            return self.ffmpeg.get_thumbnail(
                str(file_path), str(output_path),
                time=kwargs.get('time', '00:00:01')
            )
        
        elif operation == 'gif':
            output_path = file_path.with_suffix('.gif')
            return self.ffmpeg.create_gif(
                str(file_path), str(output_path),
                start_time=kwargs.get('start_time', '0'),
                duration=kwargs.get('duration', '10'),
                fps=kwargs.get('fps', 15),
                width=kwargs.get('width', 320)
            )
        
        else:
            print(f"[ERROR] Unknown operation: {operation}")
            return False
    
    def get_detailed_video_info(self, file_path):
        """Get detailed video information using FFmpeg"""
        if not self.ffmpeg.is_available():
            print("[WARNING] FFmpeg not available. Limited video info.")
            return {}
        
        return self.ffmpeg.get_video_info(file_path)
    
    def batch_process_videos(self, directory, operation, **kwargs):
        """Batch process all videos in a directory"""
        directory = Path(directory)
        if not directory.exists():
            print(f"[ERROR] Directory not found: {directory}")
            return False
        
        video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
        video_files = [f for f in directory.iterdir() 
                      if f.suffix.lower() in video_extensions]
        
        if not video_files:
            print(f"[INFO] No video files found in: {directory}")
            return True
        
        print(f"[INFO] Processing {len(video_files)} video files...")
        
        success_count = 0
        for video_file in video_files:
            print(f"Processing: {video_file.name}")
            if self.post_process_video(video_file, operation, **kwargs):
                success_count += 1
        
        print(f"[INFO] Successfully processed {success_count}/{len(video_files)} files")
        return success_count == len(video_files)
    
    def optimize_for_web(self, file_path, target_size_mb=None):
        """Optimize video for web streaming"""
        if not self.ffmpeg.is_available():
            print("[WARNING] FFmpeg not available. Cannot optimize for web.")
            return False
        
        file_path = Path(file_path)
        output_path = file_path.with_stem(f"{file_path.stem}_web")
        
        # Get video info to calculate optimal settings
        info = self.get_detailed_video_info(str(file_path))
        if not info:
            print("[WARNING] Could not get video info for optimization")
            return False
        
        # Calculate target bitrate if size limit is specified
        if target_size_mb and 'duration' in info:
            target_bitrate = int((target_size_mb * 8 * 1024) / info['duration']) # kbps
            target_bitrate = max(target_bitrate, 500)  # Minimum 500kbps
        else:
            target_bitrate = 2000  # Default 2Mbps
        
        # Optimize settings for web
        return self.ffmpeg.convert_video(
            str(file_path), str(output_path),
            codec='libx264',
            quality='medium'
        )

    def get_playlist_info(self, url):
        """Get playlist information"""
        try:
            # Basic URL validation
            if not self._is_valid_url(url):
                return {'error': 'invalid_url', 'message': 'Invalid playlist URL. Please check the URL and try again.'}
            
            cmd = [
                self.yt_dlp_path,
                '--flat-playlist',
                '--print-json',
                '--no-warnings',
                url
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            import json
            lines = result.stdout.strip().split('\n')
            if not lines or not lines[0]:
                return {'error': 'empty', 'message': 'No playlist information found.'}
            
            # Get first entry for playlist info
            first_entry = json.loads(lines[0])
            
            # Count total videos
            video_count = len([line for line in lines if line.strip()])
            
            # Extract platform/source information
            platform = self._get_platform_from_url(url)
            if not platform:
                platform = 'Unknown'
            
            return {
                'title': first_entry.get('playlist_title', first_entry.get('title', 'Unknown Playlist')),
                'video_count': video_count,
                'uploader': first_entry.get('uploader', first_entry.get('channel', 'Unknown')),
                'platform': platform
            }

        except subprocess.CalledProcessError as e:
            if e.stderr:
                error_msg = e.stderr.strip()
                if "is not a valid URL" in error_msg or "Unsupported URL" in error_msg:
                    return {'error': 'invalid_url', 'message': 'Invalid playlist URL. Please check the URL and try again.'}
                elif "Private" in error_msg or "unavailable" in error_msg:
                    return {'error': 'unavailable', 'message': 'Playlist is unavailable or private. Please try a different URL.'}
                else:
                    return {'error': 'unknown', 'message': f'Could not access playlist: {error_msg}'}
            return {'error': 'unknown', 'message': 'Could not get playlist info. Please check the URL and try again.'}
        except Exception as e:
            return {'error': 'unknown', 'message': f'Could not get playlist info: {str(e)}'}

    def download_playlist(self, url, download_type="video"):
        """Download entire playlist"""
        try:
            # Validate URL before attempting download
            if not self._is_valid_url(url):
                print("[ERROR] Invalid playlist URL. Please check the URL and try again.")
                return False
            
            download_dir = self._create_download_dir()
            
            # Create playlist-specific subdirectory
            playlist_dir = download_dir / "Playlists" / f"playlist_{int(__import__('time').time())}"
            playlist_dir.mkdir(parents=True, exist_ok=True)
            
            if download_type == "audio":
                return self._download_playlist_audio(url, playlist_dir)
            elif download_type == "custom":
                return self._download_playlist_custom(url, playlist_dir)
            else:  # video
                return self._download_playlist_video(url, playlist_dir)

        except Exception as e:
            print(f"\n[ERROR] Error during playlist download: {e}")
            return False

    def _download_playlist_video(self, url, playlist_dir):
        """Download playlist as videos"""
        try:
            cmd = [
                self.yt_dlp_path,
                '--yes-playlist',
                '-f', 'bestvideo+bestaudio/best',
                '--remux-video', 'mp4',
                '-o', str(playlist_dir / '%(playlist_index)s - %(title)s.%(ext)s'),
                '--progress',
                '--no-warnings',
                url
            ]

            print(f"Downloading playlist videos to: {playlist_dir}")
            print(f"URL: {url}")
            print("Format: MP4")
            print("Starting playlist download...\n")

            result = subprocess.run(
                cmd,
                cwd=str(playlist_dir),
                capture_output=False,
                text=True
            )

            if result.returncode == 0:
                print("\n[SUCCESS] Playlist video download completed successfully!")
                self._show_download_info(playlist_dir)
                return True
            else:
                print(f"\n[ERROR] Playlist download failed with exit code: {result.returncode}")
                return False

        except Exception as e:
            print(f"\n[ERROR] Error during playlist video download: {e}")
            return False

    def _download_playlist_audio(self, url, playlist_dir):
        """Download playlist as audio only"""
        try:
            cmd = [
                self.yt_dlp_path,
                '--yes-playlist',
                '-x',
                '--audio-format', 'mp3',
                '--audio-quality', '192K',
                '-o', str(playlist_dir / '%(playlist_index)s - %(title)s.%(ext)s'),
                '--progress',
                '--no-warnings',
                url
            ]

            print(f"Downloading playlist audio to: {playlist_dir}")
            print(f"URL: {url}")
            print("Format: MP3")
            print("Starting playlist audio download...\n")

            result = subprocess.run(
                cmd,
                cwd=str(playlist_dir),
                capture_output=False,
                text=True
            )

            if result.returncode == 0:
                print("\n[SUCCESS] Playlist audio download completed successfully!")
                self._show_download_info(playlist_dir)
                return True
            else:
                print(f"\n[ERROR] Playlist audio download failed with exit code: {result.returncode}")
                return False

        except Exception as e:
            print(f"\n[ERROR] Error during playlist audio download: {e}")
            return False

    def _download_playlist_custom(self, url, playlist_dir):
        """Download playlist with custom options"""
        # For now, default to video download
        # This can be expanded later to ask for custom format options
        print("[INFO] Custom format selection not yet implemented. Using MP4 video format.")
        return self._download_playlist_video(url, playlist_dir)
