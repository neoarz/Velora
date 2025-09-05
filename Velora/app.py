#!/usr/bin/env python3

import sys
import os
from .ui.ascii import ascii
from .ui.menu import Menu
from .ui.progress import ProgressBar, Spinner
from .downloader import Downloader
from .config import Config

class VeloraApp:
    def __init__(self):
        self.config = Config()
        self.downloader = Downloader(self.config)
        self.menu = Menu()
        self.progress = ProgressBar()

    def show_welcome(self):
        self.menu.clear_screen()
        print(ascii)
        print("\nWelcome to Velora, monkey.\n")

    def show_main_menu(self):
        print("1. Download a video")
        print("2. Download audio only")
        print("3. Download playlist")
        print("4. Settings")
        print()
        print("Choose an Option or do 'q' to exit..", end=" ")

    def get_menu_choice(self):
        while True:
            choice = input().strip().lower()
            if choice == 'q':
                return 'quit'
            elif choice in ['1', '2', '3', '4']:
                return choice
            else:
                print("Please enter a number 1-4 or 'q' to quit:", end=" ")

    def get_url_input(self):
        self.menu.print_info("Enter the URL to download:")
        print("(YouTube, Instagram, TikTok, and more see full list here: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)")
        print()
        while True:
            url = input("URL: ").strip()
            if url:
                return url
            self.menu.print_error("Please enter a valid URL.")

    def show_download_options(self):
        self.menu.print_header("Download Format Options")

        options = [
            ("Best quality (video + audio)", "High quality video with audio"),
            ("Audio only (MP3)", "Extract audio as MP3 file"),
            ("Audio only (best quality)", "Extract audio in best available format"),
            ("Video only (MP4)", "Download video without audio"),
            ("Custom options", "Advanced format selection")
        ]

        for i, (option, desc) in enumerate(options, 1):
            self.menu.print_option(i, option, desc)

        return self.menu.get_choice("Select format", 1, 5)

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
                self.show_main_menu()
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
                elif choice == '4':
                    self.handle_settings()

                # Ask to continue (return to main menu)
                if choice != 'quit' and not self.ask_continue():
                    print("\nGoodbye!")
                    break

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            self.menu.print_error(f"An error occurred: {e}")
            sys.exit(1)

    def handle_download_video(self):
        print("\nDownload Video Selected")
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

    def handle_settings(self):
        print("\nSettings Selected")
        print("Settings functionality coming soon!")

    def ask_continue(self):
        return self.menu.confirm_action("Return to main menu?")
