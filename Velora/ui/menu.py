#!/usr/bin/env python3

import os

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
