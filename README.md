# Content Automation Video Generator

A Python-based tool that automatically generates engaging vertical video content by combining background videos with audio files and auto-generated captions. The tool uses speech recognition to create accurately timed captions, making your content more accessible and engaging.

## Features

- Generates vertical format videos (1080x1920) optimized for platforms like TikTok
- Automatically creates synchronized captions from audio
- Supports multiple video and audio formats
- Handles multiple audio files in batch processing
- Implements smooth transitions with fade effects
- Maintains high quality while processing

## Prerequisites

- Python 3.11
- ffmpeg
- ImageMagick

### macOS Installation (using Homebrew)

```bash
# Install Homebrew if you haven't already
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required system dependencies
brew install ffmpeg
brew install imagemagick
```

## Project Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd ContentAutomation
```

2. Create and activate a virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your audio files (e.g., .mp3, .wav) in the `AudioAssets` folder
2. Place your background videos (e.g., .mp4, .mov) in the `VideoAssets` folder
3. Run the script:
```bash
python main.py
```
4. When prompted, enter the audio filenames separated by commas:
```
Enter the audio filenames separated by commas (e.g., audio1.mp3, audio2.mp3):
audio1.mp3, audio2.mp3
```

The script will process each audio file and create a corresponding video in the `OutputVideos` folder. Each video will include:
- Vertical format (1080x1920)
- Background video clips
- Your audio
- Auto-generated captions

## Output

Generated videos will be saved in the `OutputVideos` directory with timestamps in their filenames (e.g., `video_1234567890.mp4`).

## Notes

- The tool automatically resizes and crops input videos to fit the vertical format
- Each video segment is approximately 5 seconds long with smooth transitions
- Captions are generated using the Whisper speech recognition model
- Processing time varies depending on the length of your audio files and system capabilities
