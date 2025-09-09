# Extract Audio MCP Server

A Python-based MCP (Model Context Protocol) server for extracting audio from video files using ffmpeg.

## Features

- Extract audio from local video files and URLs
- Support for multiple video formats
- Configurable audio quality (low, medium, high)
- UUID-based unique filenames
- Automatic output directory creation
- Error handling and validation

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure ffmpeg is installed and available in your PATH

## Usage

### Running the Server

```bash
python server.py
```

### MCP Tool Parameters

The `extract_audio` tool accepts the following parameters:

- `input_path` (required): Path to local video file or URL
- `output_name` (optional): Custom name for output file
- `output_dir` (optional): Output directory (default: ../outputs)
- `audio_quality` (optional): Quality preset (low, medium, high)

### Example Usage

```json
{
  "name": "extract_audio",
  "arguments": {
    "input_path": "/path/to/video.mp4",
    "output_name": "my_audio",
    "audio_quality": "high"
  }
}
```

## Audio Quality Settings

- **Low**: 128kbps @ 44.1kHz
- **Medium**: 192kbps @ 44.1kHz (default)
- **High**: 320kbps @ 48kHz

## Output

Files are saved with UUID-based names to ensure uniqueness:
- Format: `{name}_{uuid}.mp3`
- Default location: `../outputs/`

## Requirements

- Python 3.8+
- ffmpeg
- mcp Python package
- pydantic
- asyncio-subprocess
- aiofiles
- uuid