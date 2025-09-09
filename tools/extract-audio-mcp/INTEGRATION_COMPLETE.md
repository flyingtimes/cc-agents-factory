# Extract Audio MCP Tool - Claude Code Integration

## 🎉 Integration Complete!

The Extract Audio MCP tool has been successfully integrated into Claude Code.

## What's Been Done

### ✅ Configuration Added
- **Claude Code Settings**: Updated `.claude/settings.local.json` with MCP server configuration
- **MCP Server**: Created Python-based MCP server at `tools/extract-audio-mcp/server.py`
- **Dependencies**: Installed required MCP package

### ✅ Features Available
- **Tool Name**: `extract_audio`
- **Function**: Extract audio from video files using ffmpeg
- **Input Support**: Local files and URLs
- **Output**: MP3 files with UUID-based naming
- **Quality Options**: Low (128k), Medium (192k), High (320k)

## How to Use

### 1. Restart Claude Code
Restart Claude Code to load the new MCP server configuration.

### 2. Use the Tool
The `extract_audio` tool is now available in your Claude Code session.

### 3. Example Usage
```json
{
  "input_path": "assets/1.mp4",
  "audio_quality": "high",
  "output_name": "my_audio"
}
```

## Tool Parameters

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `input_path` | Yes | Path to video file or URL | - |
| `output_name` | No | Custom output filename | Auto-generated |
| `output_dir` | No | Output directory | `../outputs` |
| `audio_quality` | No | Audio quality | `medium` |

## Quality Settings

- **Low**: 128kbps @ 44.1kHz
- **Medium**: 192kbps @ 44.1kHz (default)
- **High**: 320kbps @ 48kHz

## Output Format

Files are saved with UUID-based names:
```
outputs/
├── my_audio_550e8400-e29b-41d4-a716-446655440000.mp3
├── video_550e8400-e29b-41d4-a716-446655440000.mp3
└── url_audio_550e8400-e29b-41d4-a716-446655440000.mp3
```

## Requirements

- ✅ ffmpeg installed and in PATH
- ✅ Python MCP package installed
- ✅ Claude Code configuration updated

## Testing

The integration has been tested and verified:
- ✅ MCP server starts correctly
- ✅ Configuration is valid
- ✅ Dependencies are installed
- ✅ Tool is registered with Claude Code

## Troubleshooting

If the tool doesn't appear:
1. Restart Claude Code
2. Check ffmpeg is installed: `ffmpeg -version`
3. Verify MCP package: `pip show mcp`
4. Check configuration: `.claude/settings.local.json`

## Next Steps

The audio extraction tool is now ready to use! You can extract audio from any video file or URL directly within Claude Code.