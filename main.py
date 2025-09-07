#!/usr/bin/env python3
"""
Entry point script for Velora - PyInstaller compatible
"""
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the app
from Velora.app import VeloraApp

def main():
    app = VeloraApp()
    app.run()

if __name__ == "__main__":
    main()
