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
            'yt-dlp.exe',  # Windows
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
            1: ['-f', 'best[height<=1080]'],  # Best quality video + audio
            2: ['-x', '--audio-format', 'mp3', '--audio-quality', '192K'],  # Audio MP3
            3: ['-x', '--audio-format', 'best', '--audio-quality', '0'],  # Best audio
            4: ['-f', 'best[height<=1080]', '--remux-video', 'mp4'],  # Video MP4
            5: []  # Custom (will prompt for options)
        }
        return formats.get(choice, [])

    def _create_download_dir(self):
        download_dir = Path.home() / "Downloads" / "Velora"
        download_dir.mkdir(parents=True, exist_ok=True)
        return download_dir

    def download(self, url, format_choice):
        try:
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
                    print(f"Error: {result.stderr}")
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
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration_string', 'Unknown'),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 'Unknown'),
                'formats': len(info.get('formats', []))
            }

        except Exception as e:
            print(f"[ERROR] Could not get video info: {e}")
            return None
