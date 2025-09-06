#!/usr/bin/env python3

import os

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.align import Align
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class Modal:
    def __init__(self):
        if RICH_AVAILABLE:
            self.console = Console()
    
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_url_input_modal(self):
        if RICH_AVAILABLE:
            return self._show_rich_modal("Enter URL Below", "Paste your video URL and press Enter")
        else:
            return self._show_simple_modal("Enter URL Below", "Paste your video URL and press Enter")
    
    def show_playlist_url_input_modal(self):
        if RICH_AVAILABLE:
            return self._show_rich_modal("Enter Playlist URL Below", "Paste your playlist URL and press Enter")
        else:
            return self._show_simple_modal("Enter Playlist URL Below", "Paste your playlist URL and press Enter")
    
    def _show_rich_modal(self, title_text="Enter URL Below", hint_text="Paste your video URL and press Enter"):
        from rich.panel import Panel
        from rich.text import Text
        from rich.align import Align
        from rich import box
        from rich.console import Group
        self.console.print("\n\n")
        title = Text(title_text, style="bold white")
        hint = Text(hint_text, style="dim white")
        modal_content = Group(
            Align.left(Text("\n"), vertical="top"),
            Align.left(title, vertical="top"),
            Align.left(hint, vertical="top"),
        )
        self.console.print(modal_content)
        url = self.console.input("[bold bright_blue]> [/bold bright_blue]")
        return url.strip() if url else None
    
    def _show_simple_modal(self, title_text="Enter URL Below", hint_text="Paste your video URL and press Enter"):
        print("\n\n")
        width = 64
        print(title_text.center(width))
        print(hint_text.center(width))
        url = input("> ").strip()
        return url if url else None

    def show_video_info_modal(self, info: dict | None):
        if RICH_AVAILABLE:
            from rich.panel import Panel
            from rich.table import Table
            from rich.padding import Padding

            table = Table.grid(padding=(0, 1))
            table.add_column(justify="right", style="bold cyan", no_wrap=True)
            table.add_column(justify="left")

            if info and 'error' not in info:
                table.add_row("Title:", info.get('title', 'Unknown'))
                table.add_row("Duration:", info.get('duration', 'Unknown'))
                table.add_row("Uploader:", info.get('uploader', 'Unknown'))
                table.add_row("Views:", str(info.get('view_count', 'Unknown')))
                table.add_row("Platform:", info.get('platform', 'Unknown'))
                panel = Panel(Padding(table, (0, 1)), title="Video Info", border_style="cyan", width=60)
            else:
                error_msg = "Could not retrieve video information"
                if info and 'message' in info:
                    error_msg = info['message']
                table.add_row("Error:", error_msg)
                panel = Panel(Padding(table, (0, 1)), title="Error", border_style="red", width=60)

            self.console.print("\n")
            self.console.print(panel, justify="left")
            self.console.print("\n")
        else:
            print()
            if info and 'error' not in info:
                print("\nVideo Information:")
                print(f"   Title: {info.get('title', 'Unknown')}")
                print(f"   Duration: {info.get('duration', 'Unknown')}")
                print(f"   Uploader: {info.get('uploader', 'Unknown')}")
                print(f"   Views: {info.get('view_count', 'Unknown')}")
                print(f"   Platform: {info.get('platform', 'Unknown')}")
            else:
                error_msg = "Could not retrieve video information"
                if info and 'message' in info:
                    error_msg = info['message']
                print(f"\nError: {error_msg}")
            print()

    def show_playlist_info_modal(self, info: dict | None):
        if RICH_AVAILABLE:
            from rich.panel import Panel
            from rich.table import Table
            from rich.padding import Padding

            table = Table.grid(padding=(0, 1))
            table.add_column(justify="right", style="bold cyan", no_wrap=True)
            table.add_column(justify="left")

            if info and 'error' not in info:
                table.add_row("Title:", info.get('title', 'Unknown'))
                table.add_row("Videos:", str(info.get('video_count', 'Unknown')))
                table.add_row("Uploader:", info.get('uploader', 'Unknown'))
                table.add_row("Platform:", info.get('platform', 'Unknown'))
                panel = Panel(Padding(table, (0, 1)), title="Playlist Info", border_style="cyan", width=60)
            else:
                error_msg = "Could not retrieve playlist information"
                if info and 'message' in info:
                    error_msg = info['message']
                table.add_row("Error:", error_msg)
                panel = Panel(Padding(table, (0, 1)), title="Error", border_style="red", width=60)

            self.console.print("\n")
            self.console.print(panel, justify="left")
            self.console.print("\n")
        else:
            print()
            if info and 'error' not in info:
                print("\nPlaylist Information:")
                print(f"   Title: {info.get('title', 'Unknown')}")
                print(f"   Videos: {info.get('video_count', 'Unknown')}")
                print(f"   Uploader: {info.get('uploader', 'Unknown')}")
                print(f"   Platform: {info.get('platform', 'Unknown')}")
            else:
                error_msg = "Could not retrieve playlist information"
                if info and 'message' in info:
                    error_msg = info['message']
                print(f"\nError: {error_msg}")
            print()
