#!/usr/bin/env python3

import subprocess
import os
import sys
from pathlib import Path

class Downloader:
    def __init__(self, config):
        self.config = config
        self.yt_dlp_path = self._find_yt_dlp()

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

    def download_with_options(self, url, resolution="best", include_audio=True):
        """Download video with specific resolution and audio options"""
        try:
            # Validate URL before attempting download
            if not self._is_valid_url(url):
                print("[ERROR] Invalid video URL. Please check the URL and try again.")
                return False
            
            download_dir = self._create_download_dir()
            
            # Build format string based on options
            format_opts = self._build_format_string(resolution, include_audio)

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
                self._show_download_info(download_dir)
                return True
            else:
                print(f"\n[ERROR] Download failed with exit code: {result.returncode}")
                if result.stderr:
                    error_msg = result.stderr.strip()
                    if "is not a valid URL" in error_msg or "Unsupported URL" in error_msg:
                        print("[ERROR] Invalid video URL. Please check the URL and try again.")
                    elif "Video unavailable" in error_msg or "Private video" in error_msg:
                        print("[ERROR] Video is unavailable or private. Please try a different URL.")
                    elif "not found" in error_msg or "404" in error_msg:
                        print("[ERROR] Video not found. Please check the URL and try again.")
                    else:
                        print(f"Error: {error_msg}")
                return False

        except Exception as e:
            print(f"\n[ERROR] Error during download: {e}")
            return False

    def _build_format_string(self, resolution, include_audio):
        """Build yt-dlp format string based on resolution and audio preferences"""
        if resolution == "best":
            if include_audio:
                return ['-f', 'bestvideo+bestaudio/best']
            else:
                return ['-f', 'bestvideo']
        else:
            # Specific resolution (1080p, 720p, 480p, 360p, 144p)
            height = resolution.replace('p', '')
            if include_audio:
                return ['-f', f'bestvideo[height<={height}]+bestaudio/best[height<={height}]']
            else:
                return ['-f', f'bestvideo[height<={height}]']
        try:
            # Validate URL before attempting download
            if not self._is_valid_url(url):
                print("[ERROR] Invalid video URL. Please check the URL and try again.")
                return False
            
            download_dir = self._create_download_dir()
            format_opts = self._get_format_options(format_choice)

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
                self._show_download_info(download_dir)
                return True
            else:
                print(f"\n[ERROR] Download failed with exit code: {result.returncode}")
                if result.stderr:
                    error_msg = result.stderr.strip()
                    if "is not a valid URL" in error_msg or "Unsupported URL" in error_msg:
                        print("[ERROR] Invalid video URL. Please check the URL and try again.")
                    elif "Video unavailable" in error_msg or "Private video" in error_msg:
                        print("[ERROR] Video is unavailable or private. Please try a different URL.")
                    elif "not found" in error_msg or "404" in error_msg:
                        print("[ERROR] Video not found. Please check the URL and try again.")
                    else:
                        print(f"Error: {error_msg}")
                return False

        except Exception as e:
            print(f"\n[ERROR] Error during download: {e}")
            return False

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
