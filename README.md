# Velora

A beautiful terminal wrapper for yt-dlp with an easy-to-use interface.

## What it does

- Download videos from YouTube, Vimeo, SoundCloud, and many more
- Extract audio only (MP3 format)
- Download playlists
- Clean, colorful terminal interface

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Windows

1. Open Command Prompt or PowerShell
2. Clone or download the repository:
   ```
   git clone https://github.com/yourusername/Velora.git
   cd Velora
   ```

3. Create a virtual environment:
   ```
   python -m venv velora_env
   ```

4. Activate the virtual environment:
   ```
   velora_env\Scripts\activate
   ```

5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### macOS

1. Open Terminal
2. Clone or download the repository:
   ```
   git clone https://github.com/yourusername/Velora.git
   cd Velora
   ```

3. Create a virtual environment:
   ```
   python3 -m venv velora_env
   ```

4. Activate the virtual environment:
   ```
   source velora_env/bin/activate
   ```

5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Linux

1. Open your terminal
2. Clone or download the repository:
   ```
   git clone https://github.com/yourusername/Velora.git
   cd Velora
   ```

3. Create a virtual environment:
   ```
   python3 -m venv velora_env
   ```

4. Activate the virtual environment:
   ```
   source velora_env/bin/activate
   ```

5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

After installation, run Velora using:

```
python -m Velora
```

### How to Use

1. Choose from the menu options
2. Enter the URL you want to download
3. Select your preferred format
4. Watch the download progress

## Features

- Beautiful gradient ASCII art
- Real-time download progress
- Multiple format options
- Video information preview
- Error handling with helpful messages

## Supported Platforms

Velora can download content from:
- YouTube
- Vimeo
- SoundCloud
- TikTok
- Instagram
- And many more (any site supported by yt-dlp)

## Troubleshooting

### Virtual Environment Issues

If you encounter issues with the virtual environment:

**Windows:**
- Make sure you're using the correct activation command
- Check that the virtual environment path is correct

**macOS/Linux:**
- Ensure you're using `python3` instead of `python`
- Verify the virtual environment was created successfully

### Permission Errors

If you get permission errors:
- On macOS/Linux: Make sure the script has execute permissions
- Try running with `sudo` if necessary (not recommended for Python packages)

### Dependencies Issues

If installation fails:
- Update pip: `pip install --upgrade pip`
- Install wheel: `pip install wheel`
- Try installing in a fresh virtual environment

## Contributing

Feel free to submit issues and pull requests to help improve Velora.

