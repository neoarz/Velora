#!/usr/bin/env python3

import os
import sys
import tty
import termios

try:
    from rich.console import Console
    from rich.text import Text
    from rich.align import Align
    RICH_AVAILABLE = True
except Exception:
    RICH_AVAILABLE = False


class Menu:
    def __init__(self):
        self.width = 60
        if RICH_AVAILABLE:
            self.console = Console()

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self, title):
        print("=" * self.width)
        print(f"{title:^{self.width}}")
        print("=" * self.width)

    def print_separator(self):
        print("-" * self.width)

    def print_option(self, number, text, description=""):
        if description:
            print(f"{number:2d}. {text}")
            print(f"    {description}")
        else:
            print(f"{number:2d}. {text}")

    def print_info(self, text):
        print(f"[INFO] {text}")

    def print_success(self, text):
        print(f"[SUCCESS] {text}")

    def print_error(self, text):
        print(f"[ERROR] {text}")

    def print_warning(self, text):
        print(f"[WARNING] {text}")

    def get_choice(self, prompt, min_val, max_val):
        while True:
            try:
                choice = int(input(f"\n{prompt} ({min_val}-{max_val}): "))
                if min_val <= choice <= max_val:
                    return choice
                print(f"Please enter a number between {min_val} and {max_val}.")
            except ValueError:
                print("Please enter a valid number.")

    def confirm_action(self, message):
        while True:
            response = input(f"\n{message} (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'")

    def clear_last_lines(self, num_lines):
        for _ in range(num_lines):
            print("\033[F\033[K", end="")

    def get_key(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch += sys.stdin.read(2)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def interactive_menu(self, options, title="Select an option", show_ascii=False, clear_screen=True, show_instructions=True):
        selected = 0
        max_index = len(options) - 1
        prev_printed_lines = 0
        print("\033[?25l", end="")
        sys.stdout.flush()
        try:
            while True:
                if clear_screen:
                    self.clear_screen()
                    prev_printed_lines = 0
                else:
                    if prev_printed_lines:
                        self.clear_last_lines(prev_printed_lines)

                if show_ascii:
                    from .ascii import ascii, INFO_MESSAGE
                    print(ascii)
                    print(INFO_MESSAGE)

                if RICH_AVAILABLE:
                    if not show_ascii:
                        self.console.print(Text(title, style="bold white"))

                    for i, option in enumerate(options):
                        if i == selected:
                            t = Text("▶ ", style="bold cyan")
                            t.append(option, style="bold underline bright_cyan")
                            self.console.print(t)
                        else:
                            t = Text("  ")
                            t.append(option, style="white")
                            self.console.print(t)

                    self.console.print()

                    if show_instructions:
                        self.console.print(Text("Use ↑/↓ arrow keys to navigate, Enter to select", style="dim"))

                    key = self.get_key()
                else:
                    print(f"{title}\n")
                    for i, option in enumerate(options):
                        if i == selected:
                            print(f"▶ {option}")
                        else:
                            print(f"  {option}")
                    print()
                    if show_instructions:
                        print("Use ↑/↓ arrow keys to navigate, Enter to select")
                    key = self.get_key()

                instruction_lines = 1 if show_instructions else 0
                prev_printed_lines = 1 + len(options) + 1 + instruction_lines

                if key == '\x1b[A':
                    selected = max(0, selected - 1)
                elif key == '\x1b[B':
                    selected = min(max_index, selected + 1)
                elif key == '\r' or key == '\n':
                    return selected
                elif key == '\x03':
                    raise KeyboardInterrupt
        finally:
            print("\033[?25h", end="")
            sys.stdout.flush()

    def select_resolution(self):
        options = [
            "Best Quality",
            "1080p",
            "720p",
            "480p",
            "360p",
            "144p"
        ]
        
        choice = self.interactive_menu(options, "Select Video Resolution", clear_screen=False, show_instructions=False)
        
        resolution_map = {
            0: "best",
            1: "1080p",
            2: "720p", 
            3: "480p",
            4: "360p",
            5: "144p"
        }
        
        return resolution_map.get(choice, "best")

    def ask_include_audio(self):
        options = [
            "Yes",
            "No"
        ]
        
        choice = self.interactive_menu(options, "Include audio with video?", clear_screen=False, show_instructions=False)
        return choice == 0

    def select_format(self):
        options = [
            "MP4",
            "MKV",
            "WEBM",
            "MOV"
        ]
        
        choice = self.interactive_menu(options, "Select output format", clear_screen=False, show_instructions=False)
        
        format_map = {
            0: "mp4",
            1: "mkv", 
            2: "webm",
            3: "mov"
        }
        
        return format_map.get(choice, "mp4")

    def select_thumbnail_format(self):
        options = [
            "Original Format",
            "JPG",
            "PNG", 
            "WEBP"
        ]
        
        choice = self.interactive_menu(options, "Select thumbnail format", clear_screen=False, show_instructions=False)
        
        format_map = {
            0: "original",
            1: "jpg",
            2: "png",
            3: "webp"
        }
        
        return format_map.get(choice, "original")

    def select_playlist_type(self):
        options = [
            "Download Videos (MP4)",
            "Download Audio Only (MP3)",
            "Custom Format"
        ]
        
        choice = self.interactive_menu(options, "Select playlist download type", clear_screen=False, show_instructions=False)
        
        if choice is None:
            return None
        
        playlist_type_map = {
            0: "video",
            1: "audio",
            2: "custom"
        }
        
        return playlist_type_map.get(choice, "video")
