<div align="center"> 

# Velora

**A terminal wrapper for [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpeg](https://github.com/FFmpeg/FFmpeg)**


<img src="assets/screenshot.png" alt="Velora Screenshot" width="100%" />


</div>

<br>
<br>

> [!NOTE]
> **TLDR: Windows Sucks**
> 
> Developing this entire project in linux and macos, I have no intention of giving any support to windows unless someone gives a PR for it. If you are on Windows and would like you use this software, it works on [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) from my testing. (Ubuntu and Arch)


## Features

- **Multi-platform support** - Download from YouTube, Vimeo, SoundCloud, TikTok, Instagram, and more
- **Audio extraction** - Extract audio only in MP3, AAC, FLAC formats
- **Playlist downloads** - Download entire playlists with ease
- **Beautiful interface** - Clean, colorful terminal UI with gradient ASCII art
- **Real-time progress** - Live download progress with speed and ETA
- **Format conversion** - Multiple video formats (MP4, MOV, MKV, AVI) using FFmpeg
- **Video preview** - Get video information before downloading
- **Post-processing** - Trim, resize, and extract thumbnails
- **Error handling** - Helpful error messages and recovery options
- **Quality control** - Automatic or custom resolution selection

## Installation

### Quick Install (Recommended)

Download the latest binary from our [releases page](https://github.com/yourusername/Velora/releases):

#### macOS
```bash
# Download and install
curl -L https://github.com/yourusername/Velora/releases/latest/download/velora-macos -o velora
chmod +x velora
sudo mv velora /usr/local/bin/

# Install FFmpeg dependency
brew install ffmpeg
```

#### Linux
```bash
# Download and install
curl -L https://github.com/yourusername/Velora/releases/latest/download/velora-linux -o velora
chmod +x velora
sudo mv velora /usr/local/bin/

# Install FFmpeg dependency
sudo apt update && sudo apt install -y ffmpeg  # Ubuntu/Debian
# OR
sudo yum install ffmpeg                         # CentOS/RHEL
# OR  
sudo pacman -S ffmpeg                          # Arch Linux
```

> **Note:** Windows is not currently supported. Use WSL (Windows Subsystem for Linux) if you're on Windows.

### Build from Source

If you prefer to build from source or contribute to development:

#### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

#### macOS
```bash
# Install FFmpeg and clone repository
brew install ffmpeg
git clone https://github.com/yourusername/Velora.git
cd Velora

# Set up virtual environment and install dependencies
python3 -m venv velora_env
source velora_env/bin/activate
pip install -r requirements.txt
```

#### Linux (Ubuntu/Debian)
```bash
# Install FFmpeg and clone repository
sudo apt update && sudo apt install -y ffmpeg python3-venv
git clone https://github.com/yourusername/Velora.git
cd Velora

# Set up virtual environment and install dependencies
python3 -m venv velora_env
source velora_env/bin/activate
pip install -r requirements.txt
```

For other Linux distributions, replace `apt` with your package manager (`yum`, `pacman`, `zypper`).

## Usage

### Running Velora

#### Binary Installation
```bash
velora
```

#### From Source
```bash
python -m Velora
```

### How to Use

1. **Select your action** from the main menu
2. **Enter the URL** you want to download
3. **Choose your format** (video or audio)
4. **Watch the progress** in real-time
5. **Enjoy your content!**

## Supported Platforms

Velora works with any site supported by yt-dlp, including:

| Platform | Video | Audio | Playlists |
|----------|-------|-------|-----------|
| YouTube | ✅ | ✅ | ✅ |
| Vimeo | ✅ | ✅ | ✅ |
| SoundCloud | ✅ | ✅ | ✅ |
| TikTok | ✅ | ✅ | ❌ |
| Instagram | ✅ | ✅ | ❌ |
| And 1000+ more... | ✅ | ✅ | Varies |

## Troubleshooting

<details>
<summary><strong>FFmpeg Issues</strong></summary>

If you encounter video conversion errors:
- Verify FFmpeg installation: `ffmpeg -version`
- Reinstall FFmpeg through your package manager
- Check if FFmpeg is in your system PATH
</details>

<details>
<summary><strong>Download Issues</strong></summary>

If downloads fail:
- Check your internet connection
- Verify the URL is correct and accessible
- Some videos may be region-restricted or private
- Try a different video format if conversion fails
- Update yt-dlp: `pip install --upgrade yt-dlp`
</details>

<details>
<summary><strong>Virtual Environment Issues (Source builds)</strong></summary>

For source installations:
- Ensure you're using `python3` instead of `python`
- Verify the virtual environment was created successfully
- Update pip: `pip install --upgrade pip`
- Install wheel: `pip install wheel`
</details>

<details>
<summary><strong>Permission Errors</strong></summary>

If you get permission errors:
- Make sure the binary has execute permissions: `chmod +x velora`
- On Linux/macOS: Try running installation commands with `sudo`
- Ensure you have write permissions to the installation directory
</details>

## Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you find Velora useful, please consider:
- Starring this repository
- Reporting bugs in [Issues](https://github.com/yourusername/Velora/issues)
- Suggesting features in [Discussions](https://github.com/yourusername/Velora/discussions)

---

<div align="center">
Made with ❤️ by the Velora team
</div>

