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
