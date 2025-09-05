#!/usr/bin/env python3

import os
import sys
import tty
import termios

class Menu:
    def __init__(self):
        self.width = 60

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
        """Clear the last n lines from the terminal"""
        for _ in range(num_lines):
            print("\033[F\033[K", end="")

    def get_key(self):
        """Get a single keypress from the user"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b':  # ESC sequence
                ch += sys.stdin.read(2)
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def interactive_menu(self, options, title="Select an option", show_ascii=False):
        """Interactive menu with arrow key navigation"""
        selected = 0
        max_index = len(options) - 1
        
        while True:
            # Clear screen and show header
            self.clear_screen()
            
            # Show ASCII art if requested (for main menu)
            if show_ascii:
                from .ascii import ascii, INFO_MESSAGE
                print(ascii)
                print(f"\n{INFO_MESSAGE}")
                print()
            else:
                print(f"{title}\n")
            
            # Display options with current selection highlighted
            for i, option in enumerate(options):
                if i == selected:
                    print(f"> {option}")
                else:
                    print(f"  {option}")
            
            print("\nUse ↑/↓ arrow keys to navigate, Enter to select")
            
            # Get user input
            key = self.get_key()
            
            if key == '\x1b[A':  # Up arrow
                selected = max(0, selected - 1)
            elif key == '\x1b[B':  # Down arrow
                selected = min(max_index, selected + 1)
            elif key == '\r' or key == '\n':  # Enter
                return selected
            elif key == '\x03':  # Ctrl+C
                raise KeyboardInterrupt
