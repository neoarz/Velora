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
        """Clear the screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def show_url_input_modal(self):
        """Simple modal for URL input"""
        if RICH_AVAILABLE:
            return self._show_rich_modal()
        else:
            return self._show_simple_modal()
    
    def _show_rich_modal(self):
        """Rich version of the modal - modern style"""
        from rich.panel import Panel
        from rich.text import Text
        from rich.align import Align
        from rich import box
        from rich.console import Group
        # Add some vertical space
        self.console.print("\n\n")
        # Title and hint
        title = Text("Enter URL Below", style="bold white")
        hint = Text("Paste your video URL and press Enter", style="dim white")
        # Build modal content using Group
        modal_content = Group(
            Align.left(Text("\n"), vertical="top"),
            Align.left(title, vertical="top"),
            Align.left(hint, vertical="top"),
        )
        # Show modal content directly, no box
        self.console.print(modal_content)
        # Input inside modal
        url = self.console.input("[bold bright_blue]> [/bold bright_blue]")
        return url.strip() if url else None
    
    def _show_simple_modal(self):
        """Fallback version without Rich - modern input style"""
        # Add some vertical space
        print("\n\n")
        width = 64
        title = "Enter URL Below"
        hint = "Paste your video URL and press Enter"
        # Centered title and hint
        print(title.center(width))
        print(hint.center(width))
        # Input prompt below
        url = input("> ").strip()
        return url if url else None

    def show_video_info_modal(self, info: dict | None):
        """Display video information in a right-aligned Rich panel (or plain fallback).

        This does NOT clear the screen — it prints the modal below existing content so
        the menu/options remain visible.
        """
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
                # Handle error cases
                error_msg = "Could not retrieve video information"
                if info and 'message' in info:
                    error_msg = info['message']
                table.add_row("Error:", error_msg)
                panel = Panel(Padding(table, (0, 1)), title="Error", border_style="red", width=60)

            # Add minimal vertical spacing
            self.console.print("\n")
            # Left-align the panel so it appears on the left side as a side modal
            # Use left justification so it doesn't clear existing content on the right
            self.console.print(panel, justify="left")
            # Add space after video info
            self.console.print("\n")
        else:
            # Plain fallback: print without clearing the screen
            # Add a blank line to separate the info from previous content
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
            # Add space after video info
            print()

    def show_playlist_info_modal(self, info: dict | None):
        """Display playlist information in a right-aligned Rich panel (or plain fallback).

        This does NOT clear the screen — it prints the modal below existing content so
        the menu/options remain visible.
        """
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
                # Handle error cases
                error_msg = "Could not retrieve playlist information"
                if info and 'message' in info:
                    error_msg = info['message']
                table.add_row("Error:", error_msg)
                panel = Panel(Padding(table, (0, 1)), title="Error", border_style="red", width=60)

            # Add minimal vertical spacing
            self.console.print("\n")
            # Left-align the panel so it appears on the left side as a side modal
            # Use left justification so it doesn't clear existing content on the right
            self.console.print(panel, justify="left")
            # Add space after playlist info
            self.console.print("\n")
        else:
            # Plain fallback: print without clearing the screen
            # Add a blank line to separate the info from previous content
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
            # Add space after playlist info
            print()
