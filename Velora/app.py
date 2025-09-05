#!/usr/bin/env python3

import sys
import os
from .ui.ascii import ascii
from .ui.menu import Menu
from .ui.modal import Modal
from .ui.progress import ProgressBar, Spinner
from .downloader import Downloader
from .config import Config

class VeloraApp:
    def __init__(self):
        self.config = Config()
        self.downloader = Downloader(self.config)
        self.menu = Menu()
        self.modal = Modal()
        self.progress = ProgressBar()

    def show_welcome(self):
        from .ui.ascii import INFO_MESSAGE
        self.menu.clear_screen()
        print(ascii)
        print(f"\n{INFO_MESSAGE}")

    def show_main_menu(self):
        options = [
            "Download Video",
            "Download Audio Only", 
            "Download Playlist",
            "Quit"
        ]
        
        choice = self.menu.interactive_menu(options, "Velora - Main Menu", show_ascii=True)
        return str(choice + 1)  # Convert to 1-based indexing for compatibility

    def get_menu_choice(self):
        choice = self.show_main_menu()
        if choice == '4':  # Quit option
            return 'quit'
        return choice

    def get_url_input(self):
        return self.modal.show_url_input_modal()

    def show_download_options(self):
        options = [
            "Best quality (video + audio)",
            "Audio only (MP3)", 
            "Audio only (best quality)",
            "Video only (MP4)",
            "Custom options"
        ]
        
        choice = self.menu.interactive_menu(options, "Download Format Options")
        return choice + 1  # Convert to 1-based indexing for compatibility

    def show_video_info(self, url):
        spinner = Spinner("Getting video info...")
        spinner.start()

        info = self.downloader.get_video_info(url)

        spinner.stop()

        if info:
            print("\nVideo Information:")
            print(f"   Title: {info['title']}")
            print(f"   Duration: {info['duration']}")
            print(f"   Uploader: {info['uploader']}")
            print(f"   Views: {info['view_count']}")
            print(f"   Available formats: {info['formats']}")
            print()
        else:
            self.menu.print_warning("Could not retrieve video information")

    def run(self):
        try:
            self.show_welcome()

            while True:
                choice = self.get_menu_choice()

                if choice == 'quit':
                    print("\nGoodbye!")
                    break
                elif choice == '1':
                    self.handle_download_video()
                elif choice == '2':
                    self.handle_download_audio()
                elif choice == '3':
                    self.handle_download_playlist()

                # Ask to continue (return to main menu)
                if choice != 'quit':
                    input("\nPress Enter to return to main menu...")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            self.menu.print_error(f"An error occurred: {e}")
            sys.exit(1)

    def handle_download_video(self):
        url = self.get_url_input()
        self.show_video_info(url)
        format_choice = self.show_download_options()
        print(f"\nStarting download...")
        print(f"   URL: {url}")
        print(f"   Format: {format_choice}")
        print()
        success = self.downloader.download(url, format_choice)
        if success:
            self.menu.print_success("Download completed successfully!")
        else:
            self.menu.print_error("Download failed. Please check the URL and try again.")

    def handle_download_audio(self):
        print("\nDownload Audio Only Selected")
        url = self.get_url_input()
        self.show_video_info(url)
        # Force audio format selection
        print(f"\nStarting audio download...")
        print(f"   URL: {url}")
        print()
        success = self.downloader.download(url, 2)  # Audio only MP3
        if success:
            self.menu.print_success("Audio download completed successfully!")
        else:
            self.menu.print_error("Download failed. Please check the URL and try again.")

    def handle_download_playlist(self):
        print("\nDownload Playlist Selected")
        print("Playlist functionality coming soon!")

    def ask_continue(self):
        return self.menu.confirm_action("Return to main menu?")
