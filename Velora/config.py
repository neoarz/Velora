#!/usr/bin/env python3

import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".velora"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()
        self._load_config()

    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.settings = json.load(f)
            except Exception:
                self.settings = self._get_default_config()
        else:
            self.settings = self._get_default_config()
            self._save_config()

    def _get_default_config(self):
        return {
            "download_dir": str(Path.home() / "Downloads" / "Velora"),
            "audio_quality": "192K",
            "video_quality": "1080p",
            "audio_format": "mp3",
            "video_format": "mp4",
            "auto_open_folder": False,
            "show_progress": True,
            "max_downloads": 1
        }

    def _save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self._save_config()

    def update_download_dir(self, new_dir):
        if Path(new_dir).exists():
            self.set("download_dir", new_dir)
            return True
        return False
