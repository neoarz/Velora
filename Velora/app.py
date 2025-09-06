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
        
        choice = self.menu.interactive_menu(options, "Velora - Main Menu", show_ascii=True, show_instructions=True)
        return str(choice + 1)  # Convert to 1-based indexing for compatibility

    def get_menu_choice(self):
        choice = self.show_main_menu()
        if choice == '4':  # Quit option
            return 'quit'
        return choice

    def get_url_input(self):
        return self.modal.show_url_input_modal()
    
    def get_playlist_url_input(self):
        return self.modal.show_playlist_url_input_modal()

    def show_download_options(self, clear_screen=True):
        options = [
            "Best quality (video + audio)",
            "Audio only (MP3)", 
            "Audio only (best quality)",
            "Video only (MP4)",
            "Custom options"
        ]
        # default behavior clears screen; caller can override
        choice = self.menu.interactive_menu(options, "Download Format Options", clear_screen=clear_screen)
        return choice + 1  # Convert to 1-based indexing for compatibility

    def show_video_info(self, url):
        spinner = Spinner("Getting video info...")
        spinner.start()

        info = self.downloader.get_video_info(url)

        spinner.stop()
        # Display info using the modal (Rich panel if available, plain fallback otherwise)
        try:
            self.modal.show_video_info_modal(info)
            # Return the info so calling methods can check for errors
            return info
        except Exception:
            if not info or 'error' in info:
                error_msg = "Could not retrieve video information"
                if info and 'message' in info:
                    error_msg = info['message']
                self.menu.print_warning(error_msg)
            return info

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
        while True:
            url = self.get_url_input()
            if not url:
                self.menu.print_warning("No URL provided. Returning to main menu.")
                return
                
            info = self.show_video_info(url)
            
            # Check if there was an error getting video info
            if info and 'error' in info:
                if info['error'] == 'invalid_url':
                    self.menu.print_error("Invalid video URL. Please try again with a valid URL.")
                    retry = self.menu.confirm_action("Would you like to try with a different URL?")
                    if retry:
                        continue
                    else:
                        return
                else:
                    self.menu.print_error(info.get('message', 'Could not access video.'))
                    retry = self.menu.confirm_action("Would you like to try with a different URL?")
                    if retry:
                        continue
                    else:
                        return
            
            # If we got here, video info was successful
            # Ask for resolution preference
            resolution = self.menu.select_resolution()
            
            # Ask if user wants to include audio
            include_audio = self.menu.ask_include_audio()
            
            # Ask for output format
            output_format = self.menu.select_format()
            
            success = self.downloader.download_with_options(url, resolution, include_audio, output_format)
            if success:
                self.menu.print_success("Download completed successfully!")
            else:
                self.menu.print_error("Download failed. Please check the URL and try again.")
            break

    def handle_download_audio(self):
        while True:
            url = self.get_url_input()
            if not url:
                self.menu.print_warning("No URL provided. Returning to main menu.")
                return
                
            info = self.show_video_info(url)
            
            # Check if there was an error getting video info
            if info and 'error' in info:
                if info['error'] == 'invalid_url':
                    self.menu.print_error("Invalid video URL. Please try again with a valid URL.")
                    retry = self.menu.confirm_action("Would you like to try with a different URL?")
                    if retry:
                        continue
                    else:
                        return
                else:
                    self.menu.print_error(info.get('message', 'Could not access video.'))
                    retry = self.menu.confirm_action("Would you like to try with a different URL?")
                    if retry:
                        continue
                    else:
                        return
            
            # If we got here, video info was successful
            # Download audio only as MP3 with best quality
            success = self.downloader.download_with_options(
                url=url,
                audio_only=True,
                output_format="mp3"
            )
            if success:
                self.menu.print_success("Audio download completed successfully!")
            else:
                self.menu.print_error("Download failed. Please check the URL and try again.")
            break

    def handle_download_playlist(self):
        while True:
            url = self.get_playlist_url_input()
            if not url:
                self.menu.print_warning("No URL provided. Returning to main menu.")
                return
            
            # Check if it's a playlist URL
            if not self._is_playlist_url(url):
                self.menu.print_error("This doesn't appear to be a playlist URL. Please check and try again.")
                retry = self.menu.confirm_action("Would you like to try with a different URL?")
                if retry:
                    continue
                else:
                    return
            
            # Get playlist info
            playlist_info = self.get_playlist_info(url)
            if playlist_info and 'error' in playlist_info:
                self.menu.print_error(playlist_info.get('message', 'Could not access playlist.'))
                retry = self.menu.confirm_action("Would you like to try with a different URL?")
                if retry:
                    continue
                else:
                    return
            
            # Show playlist options
            download_type = self.menu.select_playlist_type()
            if download_type is None:
                return
            
            # If video download is selected, ask for additional options
            if download_type == "video":
                resolution = self.menu.select_resolution()
                include_audio = self.menu.ask_include_audio()
                output_format = self.menu.select_format()
                
                # Start playlist download with options
                success = self.downloader.download_playlist_with_options(
                    url, download_type, resolution, include_audio, output_format
                )
            else:
                # For audio or custom, use simple download
                success = self.downloader.download_playlist(url, download_type)
            
            if success:
                self.menu.print_success("Playlist download completed successfully!")
            else:
                self.menu.print_error("Playlist download failed. Please check the URL and try again.")
            break

    def ask_continue(self):
        return self.menu.confirm_action("Return to main menu?")
    
    def _is_playlist_url(self, url):
        """Check if URL appears to be a playlist"""
        playlist_indicators = [
            'playlist', 'list=', 'album', 'mix', 'set',
            'channel', 'user/', 'c/', '@'
        ]
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in playlist_indicators)
    
    def get_playlist_info(self, url):
        """Get basic playlist information"""
        try:
            info = self.downloader.get_playlist_info(url)
            if info and 'error' not in info:
                # Display playlist info using modal
                self.modal.show_playlist_info_modal(info)
            return info
        except Exception as e:
            error_info = {'error': 'unknown', 'message': f'Could not get playlist info: {str(e)}'}
            self.modal.show_playlist_info_modal(error_info)
            return error_info
