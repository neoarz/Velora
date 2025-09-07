#!/usr/bin/env python3

# PyInstaller 
import sys
import os

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and run the app
from Velora.app import VeloraApp

def main():
    try:
        app = VeloraApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
