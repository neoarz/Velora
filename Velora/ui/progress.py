#!/usr/bin/env python3

import sys
import time
import threading

class ProgressBar:
    def __init__(self, width=50, style="▰▱"):
        self.width = width
        self.style = style
        self.current = 0
        self.total = 100
        self.message = ""

    def update(self, current=None, total=None, message=""):
        if current is not None:
            self.current = current
        if total is not None:
            self.total = total
        if message:
            self.message = message

        self._draw()

    def _draw(self):
        if self.total == 0:
            percentage = 0
        else:
            percentage = min(100, (self.current / self.total) * 100)

        filled = int(self.width * percentage / 100)
        bar = self.style[0] * filled + self.style[1] * (self.width - filled)

        # Colors based on progress
        if percentage < 25:
            color = "\033[31m"  # Red
        elif percentage < 50:
            color = "\033[33m"  # Yellow
        elif percentage < 75:
            color = "\033[32m"  # Green
        else:
            color = "\033[36m"  # Cyan

        reset = "\033[0m"

        sys.stdout.write('\r')
        sys.stdout.write(f"  {color}[{bar}]{reset} {percentage:5.1f}% {self.message}")
        sys.stdout.flush()

    def finish(self, message="Complete"):
        self.update(100, 100, message)
        sys.stdout.write('\n')
        sys.stdout.flush()

    def simulate_progress(self, duration=5, steps=20):
        step_time = duration / steps
        for i in range(steps + 1):
            progress = (i / steps) * 100
            self.update(progress, 100, f"Processing... {i}/{steps}")
            time.sleep(step_time)
        self.finish("Done!")

class Spinner:
    """Simple spinner for indeterminate progress"""

    def __init__(self, message="Loading..."):
        self.message = message
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 2) + '\r')
        sys.stdout.flush()

    def _spin(self):
        i = 0
        while self.running:
            char = self.spinner_chars[i % len(self.spinner_chars)]
            sys.stdout.write(f'\r{char} {self.message}')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
