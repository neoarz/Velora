#!/usr/bin/env python3

import subprocess
import os
import sys
from pathlib import Path
from .ffmpeg_utils import FFmpegUtils

try:
    import ffmpeg
    FFMPEG_PYTHON_AVAILABLE = True
except ImportError:
    FFMPEG_PYTHON_AVAILABLE = False

class Downloader:
    def __init__(self, config):
        self.config = config
        self.yt_dlp_path = self._find_yt_dlp()
        self.ffmpeg = FFmpegUtils()

    def _find_yt_dlp(self):
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
            1: ['-f', 'bestvideo+bestaudio/best'],
            2: ['-x', '--audio-format', 'mp3', '--audio-quality', '192K'],
            3: ['-x', '--audio-format', 'best', '--audio-quality', '0'],
            4: ['-f', 'bestvideo+bestaudio/best', '--remux-video', 'mp4'],
            5: []
        }
        return formats.get(choice, [])

    def _create_download_dir(self):
        download_dir = Path.home() / "Downloads" / "Velora"
        download_dir.mkdir(parents=True, exist_ok=True)
        return download_dir

    def _add_ffmpeg_location_to_cmd(self, cmd):
        if self.ffmpeg.ffmpeg_path and self.ffmpeg.ffmpeg_path is not None and self.ffmpeg.ffmpeg_path != "None":
            cmd.extend(['--ffmpeg-location', self.ffmpeg.ffmpeg_path])
        return cmd

    def download_with_options(self, url, resolution="best", include_audio=True, output_format="mp4", audio_only=False):
        try:
            if not self._is_valid_url(url):
                print("[ERROR] Invalid video URL. Please check the URL and try again.")
                return False
            download_dir = self._create_download_dir()
            if audio_only:
                return self._download_audio_only(url, download_dir, output_format)
            is_instagram = 'instagram.com' in url.lower()
            is_tiktok = 'tiktok.com' in url.lower()
            if is_instagram and self._needs_instagram_downscaling(resolution):
                success = self._download_instagram_with_downscaling(url, resolution, include_audio, output_format, download_dir)
                if success:
                    return True
                else:
                    print("[INFO] Instagram downscaling failed, trying regular download...")

            elif is_tiktok and self._needs_tiktok_downscaling(resolution):
                success = self._download_tiktok_with_downscaling(url, resolution, include_audio, output_format, download_dir)
                if success:
                    return True
                else:
                    print("[INFO] TikTok downscaling failed, trying regular download...")



            return self._download_video_fallback(url, download_dir, resolution, include_audio, output_format)

        except Exception as e:
            print(f"\n[ERROR] Error during download: {e}")
            return False

    def _download_video_fallback(self, url, download_dir, resolution="best", include_audio=True, output_format="mp4"):
        try:
            print(f"Downloading to: {download_dir}")
            print(f"URL: {url}")
            print(f"Resolution: {resolution}")
            print(f"Audio: {'Yes' if include_audio else 'No'}")
            print(f"Format: {output_format.upper()}")
            print("Starting download...\n")


            cmd = [
                self.yt_dlp_path,
                '--no-playlist',
                '-f', 'best',
                '-o', str(download_dir / '%(title)s.%(ext)s'),
                '--progress',
                '--no-warnings',
                url
            ]


            cmd = self._add_ffmpeg_location_to_cmd(cmd)

            result = subprocess.run(
                cmd,
                cwd=str(download_dir),
                capture_output=False,
                text=True
            )

            if result.returncode != 0:
                print(f"[ERROR] Video download failed with exit code: {result.returncode}")
                return False


            video_files = []
            for ext in ['*.mp4', '*.mkv', '*.webm', '*.avi', '*.mov']:
                video_files.extend(download_dir.glob(ext))

            if not video_files:
                print("[ERROR] No video file found after download")
                return False


            latest_video = max(video_files, key=lambda f: f.stat().st_mtime)
            print(f"[INFO] Downloaded: {latest_video.name}")


            success = True

            if not include_audio and self.ffmpeg.is_available():
                print("[INFO] Removing audio track...")
                no_audio_path = latest_video.with_stem(f"{latest_video.stem}_no_audio")
                if self._remove_audio_with_ffmpeg(str(latest_video), str(no_audio_path)):
                    latest_video.unlink()
                    latest_video = no_audio_path
                    print("[SUCCESS] Audio track removed")
                else:
                    print("[WARNING] Failed to remove audio, keeping original")


            current_ext = latest_video.suffix.lower().lstrip('.')
            target_ext = output_format.lower()
            if current_ext != target_ext and self.ffmpeg.is_available():
                print(f"[INFO] Converting to {output_format.upper()} format...")
                converted_path = latest_video.with_suffix(f'.{target_ext}')
                if self._convert_video_format(str(latest_video), str(converted_path), output_format):
                    latest_video.unlink()
                    print(f"[SUCCESS] Converted to {output_format.upper()}")
                else:
                    print(f"[WARNING] Format conversion failed, keeping original {current_ext.upper()}")

            print("\n[SUCCESS] Download completed successfully!")
            self._show_download_info(download_dir)
            return True

        except Exception as e:
            print(f"[ERROR] Fallback video download failed: {e}")
            return False

    def _needs_instagram_downscaling(self, resolution):
        if resolution == "best":
            return False


        low_res_targets = ["480p", "360p", "144p"]
        return resolution in low_res_targets

    def _needs_tiktok_downscaling(self, resolution):
        if resolution == "best":
            return False


        return resolution in ["1080p", "720p", "480p", "360p", "144p"]

    def _download_instagram_with_downscaling(self, url, target_resolution, include_audio, output_format, download_dir):
        try:
            print(f"[INFO] Instagram detected - downloading at best quality for downscaling to {target_resolution}")

            format_strategies = [
                'best[ext=mp4]',
                'best',
                'bestvideo+bestaudio/best',
                None
            ]
            temp_file = None
            for strategy in format_strategies:
                try:

                    temp_template = str(download_dir / 'temp_%(title)s.%(ext)s')
                    cmd = [
                        self.yt_dlp_path,
                        '--no-playlist',
                        '-o', temp_template,
                        '--progress',
                        '--no-warnings',
                    ]

                    if strategy:
                        cmd.extend(['-f', strategy])

                    if not include_audio:

                        if strategy and 'bestvideo' not in strategy:
                            cmd.extend(['--no-audio'])
                    cmd.append(url)
                    print(f"Trying format strategy: {strategy or 'default'}")
                    result = subprocess.run(
                        cmd,
                        cwd=str(download_dir),
                        capture_output=False,
                        text=True
                    )
                    if result.returncode == 0:

                        temp_files = list(download_dir.glob("temp_*"))
                        if temp_files:
                            temp_file = temp_files[0]
                            print(f"Successfully downloaded: {temp_file.name}")
                            break
                    else:
                        print(f"Strategy failed with exit code: {result.returncode}")
                        continue
                except Exception as e:
                    print(f"Strategy '{strategy}' failed: {e}")
                    continue
            if not temp_file:
                print("[ERROR] All download strategies failed")
                return False

            target_height = int(target_resolution.replace('p', ''))

            final_name = temp_file.name.replace('temp_', '')
            final_path = download_dir / final_name
            print(f"Downscaling to {target_resolution} using FFmpeg...")

            if self.ffmpeg.is_available():
                success = self._ffmpeg_downscale_video(str(temp_file), str(final_path), target_height)
                if success:

                    temp_file.unlink()
                    print(f"[SUCCESS] Instagram video downscaled to {target_resolution}")

                    if not include_audio:
                        print("Removing audio from downscaled Instagram video...")
                        self._remove_audio_from_specific_file(final_path)

                    if output_format and output_format.lower() != 'mp4':
                        print(f"Converting downscaled Instagram video to {output_format.upper()} format...")
                        self._convert_specific_file_to_format(final_path, output_format)
                    print(f"[SUCCESS] Instagram video processing completed!")
                    self._show_download_info(download_dir)
                    return True
                else:
                    print("[ERROR] FFmpeg downscaling failed")

                    fallback_path = download_dir / final_name
                    temp_file.rename(fallback_path)
                    print(f"[INFO] Keeping high-resolution version: {fallback_path}")

                    if not include_audio:
                        print("Removing audio from original Instagram video...")
                        self._remove_audio_from_specific_file(fallback_path)
                    if output_format and output_format.lower() != 'mp4':
                        print(f"Converting original Instagram video to {output_format.upper()} format...")
                        self._convert_specific_file_to_format(fallback_path, output_format)
                    return True
            else:
                print("[ERROR] FFmpeg not available for downscaling")

                fallback_path = download_dir / final_name
                temp_file.rename(fallback_path)
                print(f"[INFO] Keeping high-resolution version: {fallback_path}")

                if not include_audio:
                    print("Removing audio from original Instagram video...")
                    self._remove_audio_from_specific_file(fallback_path)
                if output_format and output_format.lower() != 'mp4':
                    print(f"Converting original Instagram video to {output_format.upper()} format...")
                    self._convert_specific_file_to_format(fallback_path, output_format)
                return True
        except Exception as e:
            print(f"[ERROR] Instagram downscaling failed: {e}")
            return False

    def _ffmpeg_downscale_video(self, input_path, output_path, target_height):
        try:

            return self.ffmpeg.downscale_video(input_path, output_path, target_height)
        except Exception as e:
            print(f"[ERROR] FFmpeg downscaling failed: {e}")
            return False

    def _download_tiktok_with_downscaling(self, url, target_resolution, include_audio, output_format, download_dir):
        try:
            print(f"[INFO] TikTok detected - downloading at best quality for downscaling to {target_resolution}")

            temp_filename = f"temp_tiktok_{hash(url) % 10000}"
            temp_path = download_dir / f"{temp_filename}.%(ext)s"

            format_opts = self._build_format_string("best", include_audio, output_format)
            cmd = [
                self.yt_dlp_path,
                '--no-playlist',
                '-o', str(temp_path),
                '--progress',
                '--no-warnings',
            ]
            if format_opts:
                cmd.extend(format_opts)
            cmd.append(url)
            result = subprocess.run(cmd, cwd=str(download_dir), capture_output=False, text=True)
            if result.returncode == 0:

                temp_files = list(download_dir.glob(f"{temp_filename}.*"))
                if not temp_files:
                    print("[ERROR] Could not find downloaded TikTok file")
                    return False
                temp_file = temp_files[0]

                target_height = int(target_resolution.replace('p', ''))

                original_name = temp_file.name.replace(temp_filename, "").lstrip('.')

                try:
                    info_cmd = [self.yt_dlp_path, '--get-title', '--no-warnings', url]
                    title_result = subprocess.run(info_cmd, capture_output=True, text=True)
                    if title_result.returncode == 0:
                        clean_title = "".join(c for c in title_result.stdout.strip() if c.isalnum() or c in (' ', '-', '_')).strip()
                        final_name = f"{clean_title}.{temp_file.suffix.lstrip('.')}"
                    else:
                        final_name = f"tiktok_video_{target_resolution}.{temp_file.suffix.lstrip('.')}"
                except:
                    final_name = f"tiktok_video_{target_resolution}.{temp_file.suffix.lstrip('.')}"
                final_path = download_dir / final_name

                print(f"Downscaling to {target_resolution} using FFmpeg...")
                if self.ffmpeg.is_available():
                    success = self._ffmpeg_downscale_video(str(temp_file), str(final_path), target_height)
                    if success:

                        temp_file.unlink()
                        print(f"[SUCCESS] TikTok video downscaled to {target_resolution}")

                        if not include_audio:
                            print("Removing audio from downscaled TikTok video...")
                            self._remove_audio_from_specific_file(final_path)

                        if output_format and output_format.lower() != 'mp4':
                            print(f"Converting downscaled TikTok video to {output_format.upper()} format...")
                            self._convert_specific_file_to_format(final_path, output_format)
                        return True
                    else:

                        temp_file.rename(final_path)
                        print(f"[WARNING] Downscaling failed, keeping original quality")

                        if not include_audio:
                            print("Removing audio from original TikTok video...")
                            self._remove_audio_from_specific_file(final_path)
                        if output_format and output_format.lower() != 'mp4':
                            print(f"Converting original TikTok video to {output_format.upper()} format...")
                            self._convert_specific_file_to_format(final_path, output_format)
                        return True
                else:
                    print("[ERROR] FFmpeg not available for downscaling")

                    temp_file.rename(final_path)
                    print(f"[INFO] Keeping original resolution version: {final_path}")

                    if not include_audio:
                        print("Removing audio from original TikTok video...")
                        self._remove_audio_from_specific_file(final_path)
                    if output_format and output_format.lower() != 'mp4':
                        print(f"Converting original TikTok video to {output_format.upper()} format...")
                        self._convert_specific_file_to_format(final_path, output_format)
                    return True
            else:
                print(f"[ERROR] TikTok download failed with exit code: {result.returncode}")
                return False
        except Exception as e:
            print(f"[ERROR] TikTok downscaling failed: {e}")
            return False

    def _download_audio_only(self, url, download_dir, audio_format="mp3"):
        try:

            cmd = [
                self.yt_dlp_path,
                '--no-playlist',
                '-x',
                '--audio-format', audio_format,
                '--audio-quality', '192K',
                '-o', str(download_dir / '%(title)s.%(ext)s'),
                '--progress',
                '--no-warnings',
                '--ignore-errors',
                '--no-abort-on-error',
                '--prefer-ffmpeg',
                url
            ]


            cmd = self._add_ffmpeg_location_to_cmd(cmd)

            print(f"Downloading audio to: {download_dir}")
            print(f"URL: {url}")
            print(f"Format: {audio_format.upper()}")
            print("Starting audio download...\n")


            result = subprocess.run(
                cmd,
                cwd=str(download_dir),
                capture_output=False,
                text=True
            )

            if result.returncode == 0:
                print("\n[SUCCESS] Audio download completed successfully!")
                self._show_download_info(download_dir)
                return True
            else:
                print(f"\n[ERROR] Audio download failed with exit code: {result.returncode}")

                print("[INFO] Trying fallback method: download video then extract audio...")
                return self._download_audio_fallback(url, download_dir, audio_format)

        except Exception as e:
            print(f"\n[ERROR] Error during audio download: {e}")
            print("[INFO] Trying fallback method...")
            return self._download_audio_fallback(url, download_dir, audio_format)

    def _download_audio_fallback(self, url, download_dir, audio_format="mp3"):
        try:
            print("[INFO] Downloading video first...")

            cmd = [
                self.yt_dlp_path,
                '--no-playlist',
                '-f', 'best',
                '-o', str(download_dir / '%(title)s.%(ext)s'),
                '--progress',
                '--no-warnings',
                url
            ]

            cmd = self._add_ffmpeg_location_to_cmd(cmd)
            result = subprocess.run(
                cmd,
                cwd=str(download_dir),
                capture_output=False,
                text=True
            )
            if result.returncode != 0:
                print(f"[ERROR] Video download failed with exit code: {result.returncode}")
                return False

            video_files = []
            for ext in ['*.mp4', '*.mkv', '*.webm', '*.avi', '*.mov']:
                video_files.extend(download_dir.glob(ext))
            if not video_files:
                print("[ERROR] No video file found after download")
                return False

            latest_video = max(video_files, key=lambda f: f.stat().st_mtime)

            if self.ffmpeg.is_available():
                print(f"[INFO] Extracting audio from {latest_video.name}...")
                audio_output = latest_video.with_suffix(f'.{audio_format}')
                success = self.ffmpeg.extract_audio(
                    str(latest_video),
                    str(audio_output),
                    format=audio_format,
                    quality='192k'
                )
                if success:

                    try:
                        latest_video.unlink()
                        print(f"[INFO] Removed original video file: {latest_video.name}")
                    except Exception as e:
                        print(f"[WARNING] Could not remove original video file: {e}")
                    print("\n[SUCCESS] Audio extraction completed successfully!")
                    return True
                else:
                    print("[ERROR] Audio extraction failed")
                    return False
            else:
                print("[ERROR] FFmpeg not available for audio extraction")
                print("[INFO] Video file saved as: " + str(latest_video))
                return False
        except Exception as e:
            print(f"[ERROR] Fallback audio download failed: {e}")
            return False

    def _remove_audio_with_ffmpeg(self, input_path, output_path):
        try:
            if not self.ffmpeg.is_available():
                return False
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'copy',
                '-an',
                output_path,
                '-y'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] Failed to remove audio: {e}")
            return False

    def _convert_video_format(self, input_path, output_path, target_format):
        try:
            if not self.ffmpeg.is_available():
                return False
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-crf', '23',
                output_path,
                '-y'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] Failed to convert format: {e}")
            return False

    def _convert_to_format(self, download_dir, target_format):
        try:

            video_files = []
            for ext in ['*.mp4', '*.mkv', '*.webm', '*.avi', '*.mov']:
                video_files.extend(download_dir.glob(ext))
            if not video_files:
                print(f"[WARNING] No video file found for {target_format.upper()} conversion")
                return False

            latest_video = max(video_files, key=lambda x: x.stat().st_mtime)
            current_ext = latest_video.suffix.lower().lstrip('.')
            target_ext = target_format.lower()

            if current_ext == target_ext:
                print(f"[INFO] {latest_video.name} is already in {target_format.upper()} format.")
                return True
            target_path = latest_video.with_suffix(f'.{target_ext}')
            print(f"Converting {latest_video.name} to {target_format.upper()} format...")

            if self.ffmpeg.is_available():
                if target_format.lower() == 'mov':
                    success = self._ffmpeg_convert_to_mov(str(latest_video), str(target_path))
                else:
                    success = self._ffmpeg_convert_to_format(str(latest_video), str(target_path), target_format.lower())
                if success:

                    latest_video.unlink()
                    print(f"[SUCCESS] Converted to {target_path.name}")
                    return True
                else:
                    print(f"[ERROR] FFmpeg conversion to {target_format.upper()} failed")
                    return False
            else:
                print(f"[ERROR] FFmpeg not available for {target_format.upper()} conversion")
                return False
        except Exception as e:
            print(f"[ERROR] {target_format.upper()} conversion failed: {e}")
            return False

    def _convert_to_mov(self, download_dir):
        return self._convert_to_format(download_dir, 'mov')
        try:

            mp4_files = list(download_dir.glob("*.mp4"))
            if not mp4_files:
                print("[WARNING] No MP4 file found for MOV conversion")
                return False

            latest_mp4 = max(mp4_files, key=lambda x: x.stat().st_mtime)
            mov_path = latest_mp4.with_suffix('.mov')
            print(f"Converting {latest_mp4.name} to MOV format...")

            if self.ffmpeg.is_available():
                success = self._ffmpeg_convert_to_mov(str(latest_mp4), str(mov_path))
                if success:

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

    def _remove_audio_from_downloaded_files(self, download_dir):
        if not self.ffmpeg.is_available():
            print("[WARNING] FFmpeg not available. Cannot remove audio from video.")
            return False

        try:

            video_files = []
            for ext in ['*.mp4', '*.mkv', '*.webm', '*.avi', '*.mov']:
                video_files.extend(download_dir.glob(ext))
            if not video_files:
                print("[INFO] No video files found to process.")
                return True

            latest_video = max(video_files, key=lambda x: x.stat().st_mtime)

            video_info = self.ffmpeg.get_video_info(str(latest_video))
            if not video_info or 'audio_codec' not in video_info:
                print(f"[INFO] {latest_video.name} appears to have no audio stream.")
                return True
            print(f"Removing audio from {latest_video.name}...")

            output_path = latest_video.with_stem(f"{latest_video.stem}_no_audio")

            success = self._ffmpeg_remove_audio(str(latest_video), str(output_path))
            if success:

                latest_video.unlink()
                output_path.rename(latest_video)
                print(f"[SUCCESS] Audio removed from {latest_video.name}")
                return True
            else:
                print("[ERROR] Failed to remove audio")
                return False
        except Exception as e:
            print(f"[ERROR] Audio removal failed: {e}")
            return False

    def _ffmpeg_remove_audio(self, input_path, output_path):
        try:
            if FFMPEG_PYTHON_AVAILABLE:
                import ffmpeg

                stream = ffmpeg.input(input_path)
                stream = ffmpeg.output(stream, output_path, vcodec='copy', an=None)
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
                return True
            else:

                cmd = [
                    self.ffmpeg.ffmpeg_path,
                    '-i', input_path,
                    '-c:v', 'copy',
                    '-an',
                    '-y',
                    output_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] FFmpeg audio removal failed: {e}")
            return False

    def _remove_audio_from_specific_file(self, file_path):
        if not self.ffmpeg.is_available():
            print("[WARNING] FFmpeg not available. Cannot remove audio from video.")
            return False

        try:
            file_path = Path(file_path)

            video_info = self.ffmpeg.get_video_info(str(file_path))
            if not video_info or 'audio_codec' not in video_info:
                print(f"[INFO] {file_path.name} appears to have no audio stream.")
                return True
            print(f"Removing audio from {file_path.name}...")

            output_path = file_path.with_stem(f"{file_path.stem}_no_audio")

            success = self._ffmpeg_remove_audio(str(file_path), str(output_path))
            if success:

                file_path.unlink()
                output_path.rename(file_path)
                print(f"[SUCCESS] Audio removed from {file_path.name}")
                return True
            else:
                print("[ERROR] Failed to remove audio")
                return False
        except Exception as e:
            print(f"[ERROR] Audio removal failed: {e}")
            return False

    def _convert_specific_file_to_format(self, file_path, target_format):
        try:
            file_path = Path(file_path)
            target_format = target_format.lower()
            current_ext = file_path.suffix.lower().lstrip('.')
            if current_ext == target_format:
                print(f"[INFO] {file_path.name} is already in {target_format.upper()} format.")
                return True
            new_path = file_path.with_suffix(f'.{target_format}')
            print(f"Converting {file_path.name} to {target_format.upper()} format...")
            if not self.ffmpeg.is_available():
                print("[ERROR] FFmpeg not available for format conversion")
                return False

            if target_format == 'mov':
                success = self._ffmpeg_convert_to_mov(str(file_path), str(new_path))
            else:
                success = self._ffmpeg_convert_to_format(str(file_path), str(new_path), target_format)
            if success:

                file_path.unlink()
                print(f"[SUCCESS] Converted to {new_path.name}")
                return True
            else:
                print(f"[ERROR] FFmpeg conversion to {target_format.upper()} failed")
                return False
        except Exception as e:
            print(f"[ERROR] Format conversion failed: {e}")
            return False

    def _ffmpeg_convert_to_format(self, input_path, output_path, target_format):
        try:
            if FFMPEG_PYTHON_AVAILABLE:
                import ffmpeg

                if target_format == 'mkv':

                    try:
                        stream = ffmpeg.input(input_path)
                        stream = ffmpeg.output(stream, output_path, vcodec='copy', acodec='copy')
                        ffmpeg.run(stream, overwrite_output=True, quiet=True)
                        return True
                    except:

                        stream = ffmpeg.input(input_path)
                        stream = ffmpeg.output(stream, output_path, vcodec='libx264', acodec='aac')
                        ffmpeg.run(stream, overwrite_output=True, quiet=True)
                        return True
                elif target_format == 'webm':

                    stream = ffmpeg.input(input_path)
                    stream = ffmpeg.output(stream, output_path, vcodec='libvpx-vp9', acodec='libopus', crf=30)
                    ffmpeg.run(stream, overwrite_output=True, quiet=True)
                    return True
                elif target_format == 'mp4':

                    try:

                        stream = ffmpeg.input(input_path)
                        stream = ffmpeg.output(stream, output_path, vcodec='copy', acodec='copy', movflags='faststart')
                        ffmpeg.run(stream, overwrite_output=True, quiet=True)
                        return True
                    except:

                        stream = ffmpeg.input(input_path)
                        stream = ffmpeg.output(stream, output_path, vcodec='libx264', acodec='aac', movflags='faststart')
                        ffmpeg.run(stream, overwrite_output=True, quiet=True)
                        return True

            return self._subprocess_convert_to_format(input_path, output_path, target_format)
        except Exception as e:
            print(f"[ERROR] FFmpeg format conversion failed: {e}")
            return self._subprocess_convert_to_format(input_path, output_path, target_format)

    def _subprocess_convert_to_format(self, input_path, output_path, target_format):
        try:
            if target_format == 'mkv':
                cmd = [
                    self.ffmpeg.ffmpeg_path, '-i', input_path,
                    '-c:v', 'copy', '-c:a', 'copy', '-y', output_path
                ]
            elif target_format == 'webm':
                cmd = [
                    self.ffmpeg.ffmpeg_path, '-i', input_path,
                    '-c:v', 'libvpx-vp9', '-c:a', 'libopus', '-crf', '30', '-y', output_path
                ]
            elif target_format == 'mp4':
                cmd = [
                    self.ffmpeg.ffmpeg_path, '-i', input_path,
                    '-c:v', 'libx264', '-c:a', 'aac', '-movflags', 'faststart', '-y', output_path
                ]
            else:
                return False
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] Subprocess format conversion failed: {e}")
            return False

    def _convert_thumbnail_format(self, input_path, target_format):
        try:
            if target_format == "original":
                return input_path

            current_ext = input_path.suffix.lower().lstrip('.')
            if current_ext == target_format.lower():
                print(f"[INFO] Thumbnail is already in {target_format.upper()} format, no conversion needed.")
                return input_path

            output_path = input_path.with_suffix(f'.{target_format}')

            if not self.ffmpeg.is_available():
                print("[WARNING] FFmpeg not available for thumbnail conversion")
                print("[INFO] Keeping original thumbnail format")
                return input_path
            if FFMPEG_PYTHON_AVAILABLE:
                import ffmpeg
                print(f"[INFO] Converting from {current_ext.upper()} to {target_format.upper()}...")

                if target_format == 'jpg':
                    stream = ffmpeg.input(str(input_path))
                    stream = ffmpeg.output(stream, str(output_path), q=2)
                    ffmpeg.run(stream, overwrite_output=True, quiet=True)
                elif target_format == 'png':
                    stream = ffmpeg.input(str(input_path))
                    stream = ffmpeg.output(stream, str(output_path))
                    ffmpeg.run(stream, overwrite_output=True, quiet=True)
                elif target_format == 'webp':
                    stream = ffmpeg.input(str(input_path))
                    stream = ffmpeg.output(stream, str(output_path), quality=80)
                    ffmpeg.run(stream, overwrite_output=True, quiet=True)

                if output_path.exists() and output_path.stat().st_size > 0:
                    input_path.unlink()
                    return output_path
                else:
                    print(f"[WARNING] Conversion to {target_format.upper()} failed - output file not created")
                    return input_path
            else:

                return self._subprocess_convert_thumbnail(input_path, target_format)
        except Exception as e:
            print(f"[WARNING] Thumbnail format conversion failed: {e}")
            print("[INFO] Keeping original thumbnail format")
            return input_path

    def _subprocess_convert_thumbnail(self, input_path, target_format):
        try:
            output_path = input_path.with_suffix(f'.{target_format}')
            print(f"[INFO] Using FFmpeg subprocess for conversion...")
            if target_format == 'jpg':
                cmd = [
                    self.ffmpeg.ffmpeg_path, '-i', str(input_path),
                    '-q:v', '2', '-y', str(output_path)
                ]
            elif target_format == 'png':
                cmd = [
                    self.ffmpeg.ffmpeg_path, '-i', str(input_path),
                    '-y', str(output_path)
                ]
            elif target_format == 'webp':
                cmd = [
                    self.ffmpeg.ffmpeg_path, '-i', str(input_path),
                    '-quality', '80', '-y', str(output_path)
                ]
            else:
                print(f"[WARNING] Unsupported format: {target_format}")
                return input_path
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 0:
                input_path.unlink()
                print(f"[SUCCESS] Successfully converted to {target_format.upper()}")
                return output_path
            else:
                if result.stderr:
                    print(f"[WARNING] FFmpeg conversion error: {result.stderr.strip()}")
                else:
                    print(f"[WARNING] FFmpeg conversion failed with exit code: {result.returncode}")
                print("[INFO] Keeping original thumbnail format")
                return input_path
        except Exception as e:
            print(f"[WARNING] Subprocess thumbnail conversion failed: {e}")
            print("[INFO] Keeping original thumbnail format")
            return input_path

    def _ffmpeg_convert_to_mov(self, input_path, output_path):
        try:
            if FFMPEG_PYTHON_AVAILABLE:

                try:


                    stream = ffmpeg.input(input_path)
                    stream = ffmpeg.output(
                        stream, 
                        output_path,
                        vcodec='copy',
                        acodec='copy',
                        movflags='faststart'
                    )
                    ffmpeg.run(stream, overwrite_output=True, quiet=True)
                    return True
                except Exception as e:

                    print("[INFO] Fast conversion not possible, re-encoding video for MOV compatibility...")

                    try:
                        stream = ffmpeg.input(input_path)
                        stream = ffmpeg.output(
                            stream, 
                            output_path,
                            vcodec='libx264',
                            acodec='aac',
                            crf=23,
                            preset='medium',
                            movflags='faststart'
                        )
                        ffmpeg.run(stream, overwrite_output=True, quiet=True)
                        return True
                    except Exception as e2:
                        print(f"[ERROR] FFmpeg MOV conversion failed: {e2}")


            if not self.ffmpeg.is_available():
                print("[ERROR] FFmpeg not available for MOV conversion")
                return False

            cmd = [
                self.ffmpeg.ffmpeg_path,
                '-i', input_path,
                '-c:v', 'copy',
                '-c:a', 'copy',
                '-movflags', 'faststart',
                '-y',
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return True
            else:

                print("[INFO] Fast conversion failed, re-encoding for MOV compatibility...")
                cmd = [
                    self.ffmpeg.ffmpeg_path,
                    '-i', input_path,
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-crf', '23',
                    '-preset', 'medium',
                    '-movflags', 'faststart',
                    '-y',
                    output_path
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] MOV conversion failed: {e}")
            return False

    def _build_format_string(self, resolution, include_audio, output_format="mp4"):

        if resolution == "best":
            if include_audio:
                format_string = 'bestvideo+bestaudio/best'
            else:

                format_string = 'bestvideo/best'
        else:

            height = resolution.replace('p', '')
            if include_audio:
                format_string = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
            else:

                format_string = f'bestvideo[height<={height}]/best[height<={height}]/best'

        cmd_opts = ['-f', format_string]

        self._desired_format = output_format.lower() if output_format else 'mp4'


        if output_format and output_format.lower() not in ['webm', 'mov']:

            if output_format.lower() in ['mp4', 'mkv']:
                cmd_opts.extend(['--remux-video', output_format.lower()])
            else:

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
            pass

    def get_video_info(self, url):
        try:

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

            platform = self._get_platform_from_url(url)
            if not platform:

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
        if not url or not isinstance(url, str):
            return False
        url = url.strip()
        if not url:
            return False

        if not (url.startswith('http://') or url.startswith('https://') or url.startswith('www.')):
            return False

        valid_domains = [
            'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
            'twitch.tv', 'facebook.com', 'instagram.com', 'tiktok.com',
            'twitter.com', 'x.com', 'reddit.com', 'soundcloud.com'
        ]
        return any(domain in url.lower() for domain in valid_domains)

    def _get_platform_from_url(self, url):
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

        return extractor.capitalize()

    def post_process_video(self, file_path, operation, **kwargs):
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
        if not self.ffmpeg.is_available():
            print("[WARNING] FFmpeg not available. Limited video info.")
            return {}
        return self.ffmpeg.get_video_info(file_path)
    def batch_process_videos(self, directory, operation, **kwargs):
        directory = Path(directory)
        if not directory.exists():
            print(f"[ERROR] Directory not found: {directory}")
            return False
        video_extensions = {'.mp4', '.mkv', '.mov', '.wmv', '.flv', '.webm'}
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
        if not self.ffmpeg.is_available():
            print("[WARNING] FFmpeg not available. Cannot optimize for web.")
            return False
        file_path = Path(file_path)
        output_path = file_path.with_stem(f"{file_path.stem}_web")

        info = self.get_detailed_video_info(str(file_path))
        if not info:
            print("[WARNING] Could not get video info for optimization")
            return False

        if target_size_mb and 'duration' in info:
            target_bitrate = int((target_size_mb * 8 * 1024) / info['duration'])
            target_bitrate = max(target_bitrate, 500)
        else:
            target_bitrate = 2000

        return self.ffmpeg.convert_video(
            str(file_path), str(output_path),
            codec='libx264',
            quality='medium'
        )

    def get_playlist_info(self, url):
        try:

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

            first_entry = json.loads(lines[0])

            video_count = len([line for line in lines if line.strip()])

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
        try:

            if not self._is_valid_url(url):
                print("[ERROR] Invalid playlist URL. Please check the URL and try again.")
                return False
            download_dir = self._create_download_dir()

            playlist_dir = download_dir / "Playlists" / f"playlist_{int(__import__('time').time())}"
            playlist_dir.mkdir(parents=True, exist_ok=True)
            if download_type == "audio":
                return self._download_playlist_audio(url, playlist_dir)
            elif download_type == "custom":
                return self._download_playlist_custom(url, playlist_dir)
            else:
                return self._download_playlist_video(url, playlist_dir)

        except Exception as e:
            print(f"\n[ERROR] Error during playlist download: {e}")
            return False

    def download_playlist_with_options(self, url, download_type, resolution="best", include_audio=True, output_format="mp4"):
        try:

            if not self._is_valid_url(url):
                print("[ERROR] Invalid playlist URL. Please check the URL and try again.")
                return False
            download_dir = self._create_download_dir()

            playlist_dir = download_dir / "Playlists" / f"playlist_{int(__import__('time').time())}"
            playlist_dir.mkdir(parents=True, exist_ok=True)
            if download_type == "video":
                return self._download_playlist_video_with_options(url, playlist_dir, resolution, include_audio, output_format)
            else:

                return self.download_playlist(url, download_type)

        except Exception as e:
            print(f"\n[ERROR] Error during playlist download: {e}")
            return False

    def _download_playlist_video(self, url, playlist_dir):
        try:
            print(f"Downloading playlist videos to: {playlist_dir}")
            print(f"URL: {url}")
            print("Format: MP4")
            print("Starting playlist download...\n")


            cmd = [
                self.yt_dlp_path,
                '--yes-playlist',
                '-f', 'best',
                '-o', str(playlist_dir / '%(playlist_index)s - %(title)s.%(ext)s'),
                '--progress',
                '--no-warnings',
                url
            ]


            cmd = self._add_ffmpeg_location_to_cmd(cmd)

            result = subprocess.run(
                cmd,
                cwd=str(playlist_dir),
                capture_output=False,
                text=True
            )

            if result.returncode == 0:
                print("\n[SUCCESS] Playlist video download completed successfully!")

                video_files = []
                for ext in ['*.mkv', '*.webm', '*.avi', '*.mov']:
                    video_files.extend(playlist_dir.glob(ext))
                if video_files and self.ffmpeg.is_available():
                    print(f"[INFO] Converting {len(video_files)} videos to MP4 format...")
                    converted_count = 0
                    for video_file in video_files:
                        if video_file.suffix.lower() != '.mp4':
                            mp4_output = video_file.with_suffix('.mp4')
                            print(f"[INFO] Converting: {video_file.name}")
                            if self._convert_video_format(str(video_file), str(mp4_output), 'mp4'):
                                video_file.unlink()
                                converted_count += 1
                            else:
                                print(f"[WARNING] Failed to convert {video_file.name}")
                    if converted_count > 0:
                        print(f"[SUCCESS] Converted {converted_count} videos to MP4")
                self._show_download_info(playlist_dir)
                return True
            else:
                print(f"\n[ERROR] Playlist video download failed with exit code: {result.returncode}")
                return False

        except Exception as e:
            print(f"\n[ERROR] Error during playlist video download: {e}")
            return False

    def _download_playlist_video_with_options(self, url, playlist_dir, resolution="best", include_audio=True, output_format="mp4"):
        try:

            if resolution == "best":
                if include_audio:
                    format_string = 'bestvideo+bestaudio/best'
                else:
                    format_string = 'bestvideo'
            else:

                height = resolution.replace('p', '')
                if include_audio:
                    format_string = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
                else:
                    format_string = f'bestvideo[height<={height}]'

            cmd = [
                self.yt_dlp_path,
                '--yes-playlist',
                '-f', format_string,
                '-o', str(playlist_dir / '%(playlist_index)s - %(title)s.%(ext)s'),
                '--progress',
                '--no-warnings',
            ]


            if output_format and output_format.lower() not in ['webm', 'mov']:
                if output_format.lower() in ['mp4', 'mkv']:
                    cmd.extend(['--remux-video', output_format.lower()])
                else:
                    cmd.extend(['--recode-video', output_format.lower()])

            cmd.append(url)

            print(f"Downloading playlist videos to: {playlist_dir}")
            print(f"URL: {url}")
            print(f"Resolution: {resolution}")
            print(f"Audio: {'Yes' if include_audio else 'No'}")
            print(f"Format: {output_format.upper()}")
            print("Starting playlist download...\n")

            result = subprocess.run(
                cmd,
                cwd=str(playlist_dir),
                capture_output=False,
                text=True
            )

            if result.returncode == 0:

                if output_format and output_format.lower() == 'mov':
                    print("\nConverting videos to MOV format...")
                    self._convert_playlist_to_mov(playlist_dir)
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
        try:
            print(f"Downloading playlist audio to: {playlist_dir}")
            print(f"URL: {url}")
            print("Format: MP3")
            print("Starting playlist audio download...\n")


            cmd = [
                self.yt_dlp_path,
                '--yes-playlist',
                '-f', 'best',
                '-o', str(playlist_dir / '%(playlist_index)s - %(title)s.%(ext)s'),
                '--progress',
                '--no-warnings',
                url
            ]


            cmd = self._add_ffmpeg_location_to_cmd(cmd)

            result = subprocess.run(
                cmd,
                cwd=str(playlist_dir),
                capture_output=False,
                text=True
            )

            if result.returncode != 0:
                print(f"\n[ERROR] Playlist video download failed with exit code: {result.returncode}")
                return False


            video_files = []
            for ext in ['*.mp4', '*.mkv', '*.webm', '*.avi', '*.mov']:
                video_files.extend(playlist_dir.glob(ext))

            if not video_files:
                print("[ERROR] No video files found after playlist download")
                return False

            print(f"\n[INFO] Found {len(video_files)} videos. Extracting audio...")


            success_count = 0
            for video_file in video_files:
                print(f"[INFO] Extracting audio from: {video_file.name}")
                if self.ffmpeg.is_available():
                    audio_output = video_file.with_suffix('.mp3')
                    success = self.ffmpeg.extract_audio(
                        str(video_file),
                        str(audio_output),
                        format='mp3',
                        quality='192k'
                    )
                    if success:

                        try:
                            video_file.unlink()
                            success_count += 1
                        except Exception as e:
                            print(f"[WARNING] Could not remove video file {video_file.name}: {e}")
                            success_count += 1
                    else:
                        print(f"[ERROR] Failed to extract audio from {video_file.name}")
                else:
                    print("[ERROR] FFmpeg not available for audio extraction")
                    break

            if success_count > 0:
                print(f"\n[SUCCESS] Successfully extracted audio from {success_count}/{len(video_files)} videos!")
                self._show_download_info(playlist_dir)
                return True
            else:
                print("\n[ERROR] Failed to extract audio from any videos")
                return False

        except Exception as e:
            print(f"\n[ERROR] Error during playlist audio download: {e}")
            return False

    def _download_playlist_custom(self, url, playlist_dir):


        print("[INFO] Custom format selection not yet implemented. Using MP4 video format.")
        return self._download_playlist_video(url, playlist_dir)

    def _convert_playlist_to_mov(self, playlist_dir):
        try:
            mp4_files = list(playlist_dir.glob("*.mp4"))
            if not mp4_files:
                print("[WARNING] No MP4 files found for MOV conversion")
                return False
            converted_count = 0
            for mp4_file in mp4_files:
                mov_path = mp4_file.with_suffix('.mov')
                print(f"Converting {mp4_file.name} to MOV...")
                if self.ffmpeg.is_available():
                    success = self._ffmpeg_convert_to_mov(str(mp4_file), str(mov_path))
                    if success:
                        mp4_file.unlink()
                        converted_count += 1
                    else:
                        print(f"[WARNING] Failed to convert {mp4_file.name}")
                else:
                    print("[ERROR] FFmpeg not available for MOV conversion")
                    return False
            print(f"[INFO] Successfully converted {converted_count}/{len(mp4_files)} files to MOV")
            return converted_count > 0
        except Exception as e:
            print(f"[ERROR] Playlist MOV conversion failed: {e}")
            return False

    def download_thumbnail(self, url, target_format="original"):
        try:
            print("[INFO] Preparing to download thumbnail...")

            download_dir = self._create_download_dir()

            cmd = [
                self.yt_dlp_path,
                '--write-thumbnail',
                '--skip-download',
                '--no-write-info-json',
                '--output', str(download_dir / '%(title)s.%(ext)s'),
                '--verbose',
                url
            ]


            cmd = self._add_ffmpeg_location_to_cmd(cmd)

            print(f"[INFO] Downloading thumbnail from: {url}")
            print(f"[INFO] Saving to: {download_dir}")
            from .ui.progress import Spinner
            spinner = Spinner("Downloading thumbnail...")
            spinner.start()
            result = subprocess.run(cmd, capture_output=True, cwd=str(download_dir), errors='replace')
            spinner.stop()
            if result.returncode == 0:

                thumbnail_files = []

                patterns = [
                    "*.jpg", "*.jpeg", "*.png", "*.webp", "*.gif", "*.image",
                    "*.JPG", "*.JPEG", "*.PNG", "*.WEBP", "*.GIF", "*.IMAGE"
                ]
                for pattern in patterns:
                    thumbnail_files.extend(download_dir.glob(pattern))

                for pattern in patterns:
                    thumbnail_files.extend(download_dir.rglob(pattern))

                unique_thumbnails = list(set(thumbnail_files))
                if unique_thumbnails:

                    latest_thumbnail = max(unique_thumbnails, key=lambda x: x.stat().st_mtime)

                    if target_format != "original":
                        current_ext = latest_thumbnail.suffix.lower().lstrip('.')
                        if current_ext == target_format.lower():
                            print(f"[INFO] Thumbnail is already in {target_format.upper()} format!")
                        else:
                            print(f"[INFO] Converting thumbnail from {current_ext.upper()} to {target_format.upper()} format...")
                            converted_thumbnail = self._convert_thumbnail_format(latest_thumbnail, target_format)
                            if converted_thumbnail != latest_thumbnail:
                                latest_thumbnail = converted_thumbnail
                                print(f"[SUCCESS] Thumbnail converted to {target_format.upper()} format!")
                    print(f"[SUCCESS] Thumbnail downloaded successfully!")
                    print(f"[INFO] Saved as: {latest_thumbnail.name}")
                    print(f"[INFO] Location: {latest_thumbnail.parent}")
                    return True
                else:

                    print("[DEBUG] Files found in download directory:")
                    all_files = list(download_dir.glob("*"))
                    if all_files:
                        for file in all_files:
                            print(f"[DEBUG] - {file.name}")
                    else:
                        print("[DEBUG] No files found in download directory")

                    if result.stdout:
                        try:
                            stdout_text = result.stdout.decode('utf-8', errors='replace') if isinstance(result.stdout, bytes) else str(result.stdout)
                            print(f"[DEBUG] yt-dlp output: {stdout_text}")
                        except:
                            print("[DEBUG] yt-dlp output: (unable to decode)")
                    print("[WARNING] Thumbnail download completed but file not found")
                    return False
            else:
                print(f"[ERROR] Thumbnail download failed with exit code: {result.returncode}")
                if result.stderr:
                    try:
                        stderr_text = result.stderr.decode('utf-8', errors='replace') if isinstance(result.stderr, bytes) else str(result.stderr)
                        print(f"[ERROR] {stderr_text}")
                    except:
                        print("[ERROR] (unable to decode error message)")
                return False
        except Exception as e:
            print(f"[ERROR] Error during thumbnail download: {e}")
            return False
