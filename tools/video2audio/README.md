# Video2Audio MCP Server

A Model Context Protocol (MCP) server that extracts audio from video files using ffmpeg.

## Features

- Extract audio from video files (MP4, AVI, MOV, etc.)
- Multiple quality options (low, medium, high)
- Automatic output directory creation
- UUID-based unique naming
- Comprehensive error handling
- Timeout protection (5 minutes)
- File size validation

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure ffmpeg is installed and available in your PATH:
```bash
ffmpeg -version
```

## Configuration

The server is automatically configured in the project's MCP settings:

- `.mcp.json`: Contains the server configuration
- `.claude/settings.local.json`: Contains permissions and enabled servers

## Usage

The server provides one tool:

### extract_audio_from_video

Extract audio from a video file.

**Parameters:**
- `input_path` (required): Path to video file
- `output_name` (optional): Custom output filename (without extension)
- `output_dir` (optional): Output directory (default: ../outputs)
- `audio_quality` (optional): Audio quality - "low" (128kbps), "medium" (192kbps), "high" (320kbps)

**Example usage in Claude Code:**
```json
{
  "name": "extract_audio_from_video",
  "arguments": {
    "input_path": "assets/2.mp4",
    "output_name": "my_video_audio",
    "audio_quality": "high"
  }
}
```

**Response:**
```json
{
  "success": true,
  "output_file": "/path/to/outputs/my_video_audio_12345678.mp3",
  "file_size": 43999336,
  "quality": "high",
  "bitrate": 320,
  "sample_rate": 48000,
  "processing_time": 12.34,
  "message": "Audio extracted successfully in 12.34 seconds"
}
```

## Quality Options

- **Low**: 128kbps @ 44.1kHz (smaller file size)
- **Medium**: 192kbps @ 44.1kHz (balanced quality/size)
- **High**: 320kbps @ 48kHz (best quality)

## Output Format

- Audio files are saved as MP3 format
- Files are saved to the `outputs/` directory by default
- Filenames use the pattern: `{name}_{uuid}.mp3`
- UUID ensures unique filenames to prevent conflicts

## Testing

Run the test suite to verify functionality:

```bash
python test_server.py
```

The test suite includes:
- Audio extraction functionality test
- Parameter validation test
- Error handling test

## Dependencies

- Python 3.8+
- ffmpeg (must be installed system-wide)
- mcp>=1.0.0
- pydantic>=2.0.0
- aiofiles>=23.0.0

## Error Handling

The server handles various error conditions:

- Missing or invalid input files
- ffmpeg not available
- Invalid quality parameters
- File permission issues
- Process timeouts
- Disk space issues

## Integration

The server is automatically integrated with Claude Code through the project's MCP configuration. Once configured, the `extract_audio_from_video` tool will be available in your Claude Code sessions.

## Project Structure

```
tools/video2audio/
├── server.py              # MCP server implementation
├── extract_audio.py       # Standalone extraction script
├── test_server.py         # Test suite
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Troubleshooting

If the tool doesn't appear in Claude Code:

1. Restart Claude Code
2. Check that ffmpeg is installed: `ffmpeg -version`
3. Verify MCP dependencies: `pip show mcp pydantic aiofiles`
4. Check configuration files: `.mcp.json` and `.claude/settings.local.json`
5. Run tests: `python test_server.py`

## License

This project is part of the cc-agents-factory toolkit.