# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is **cc-agents-factory**, a specialized toolkit for Claude Code featuring custom MCP (Model Context Protocol) integrations. The project focuses on audio extraction capabilities with comprehensive development infrastructure and multi-platform support.

## Technology Stack

- **Primary Language**: Python 3.8+
- **MCP Framework**: Model Context Protocol server implementation
- **Audio Processing**: FFmpeg for audio extraction
- **Platform**: Windows (with batch script support)
- **Dependencies**: MCP package, pydantic, aiofiles

## Project Structure

```
cc-agents-factory/
├── .claude/
│   ├── agents/
│   │   └── git.md (Chinese git automation agent)
│   └── settings.local.json (MCP server config)
├── tools/
│   ├── extract-audio-mcp/
│   │   ├── server.py (MCP server)
│   │   ├── setup_claude_integration.py
│   │   ├── test_server.py
│   │   ├── requirements.txt
│   │   └── README.md
│   └── extract_audio.bat (Windows batch script)
├── assets/
│   └── 1.mp4 (sample video file)
├── outputs/ (audio extraction output directory)
├── node_modules/
└── .gitignore (comprehensive ignore file)
```

## Key Features

### Audio Extraction MCP Server
- **Tool Name**: `extract_audio`
- **Input Support**: Local video files and URLs
- **Output Format**: MP3 files with UUID-based naming
- **Quality Options**: 
  - Low: 128kbps @ 44.1kHz
  - Medium: 192kbps @ 44.1kHz (default)
  - High: 320kbps @ 48kHz
- **Features**: Automatic output directory creation, comprehensive error handling

### Development Infrastructure
- **Automated Setup**: `setup_claude_integration.py` for MCP integration
- **Testing Framework**: `test_server.py` for server functionality validation
- **Multi-Platform Support**: Python-based server with Windows batch alternative
- **Professional Documentation**: Comprehensive README files and usage guides

### Chinese Language Support
The git agent (`.claude/agents/git.md`) is configured to respond in Chinese, providing git automation capabilities for Chinese-speaking developers.

## Development Commands

### Installation and Setup
```bash
# Install Python dependencies
pip install -r tools/extract-audio-mcp/requirements.txt

# Run automated Claude Code integration setup
cd tools/extract-audio-mcp
python setup_claude_integration.py

# Test MCP server functionality
python test_server.py
```

### Testing and Validation
```bash
# Run comprehensive server tests
python tools/extract-audio-mcp/test_server.py

# Test MCP server startup
python -c "import sys; sys.path.append('tools/extract-audio-mcp'); import server"

# Verify FFmpeg installation
ffmpeg -version

# Check MCP package installation
pip show mcp
```

### Development Workflow
```bash
# Start MCP server manually for testing
python tools/extract-audio-mcp/server.py

# Run integration setup script
cd tools/extract-audio-mcp && python setup_claude_integration.py

# Verify Claude Code configuration
cat .claude/settings.local.json
```

### Prerequisites
- Python 3.8+
- FFmpeg installed and in PATH
- Claude Code with MCP support

### Usage
The `extract_audio` tool is available within Claude Code sessions:

```json
{
  "name": "extract_audio",
  "arguments": {
    "input_path": "path/to/video.mp4",
    "output_name": "my_audio",
    "audio_quality": "high"
  }
}
```

**Parameters**:
- `input_path` (required): Path to video file or URL
- `output_name` (optional): Custom output filename
- `output_dir` (optional): Output directory (default: ../outputs)
- `audio_quality` (optional): low/medium/high (default: medium)

## Configuration Files

### Claude Code Settings
- `.claude/settings.local.json`: MCP server configuration
- `.mcp.json`: Additional MCP settings
- `.claude/agents/git.md`: Chinese-language git automation agent

### Build and Development
- **No traditional build process**: This is a Python-based MCP server
- **Dependencies**: Listed in `tools/extract-audio-mcp/requirements.txt`
- **Testing**: Use `test_server.py` to validate functionality (tests UUID generation, quality settings, directory creation)
- **Integration**: Use `setup_claude_integration.py` for automated setup (installs MCP dependencies, tests server, checks configuration)
- **Development**: Server can be started manually with `python tools/extract-audio-mcp/server.py`

## Important Files

### Core MCP Server
- `tools/extract-audio-mcp/server.py`: Main MCP server implementation
- `tools/extract-audio-mcp/requirements.txt`: Python dependencies
- `tools/extract-audio-mcp/README.md`: Server documentation

### Setup and Testing
- `tools/extract-audio-mcp/setup_claude_integration.py`: Automated integration script
- `tools/extract-audio-mcp/test_server.py`: Server testing framework
- `tools/extract_audio.bat`: Windows command-line alternative

### Configuration
- `.claude/settings.local.json`: MCP server configuration for Claude Code
- `.gitignore`: Comprehensive ignore file for all platforms
- `.claude/agents/git.md`: Chinese git automation agent

## Output Format
Files are saved with UUID-based names to ensure uniqueness:
- Format: `{name}_{uuid}.mp3`
- Default location: `outputs/`
- Example: `my_audio_550e8400-e29b-41d4-a716-446655440000.mp3`

## Error Handling
The server includes comprehensive error handling for:
- FFmpeg availability checking
- Input validation and file existence verification
- Network error handling for URLs
- Permission and path validation

## Troubleshooting
If the MCP tool doesn't appear:
1. Restart Claude Code
2. Check FFmpeg installation: `ffmpeg -version`
3. Verify MCP package: `pip show mcp`
4. Check configuration: `.claude/settings.local.json`

## Claude Code Permissions
Current permissions allow for comprehensive file operations, bash commands, and MCP server integration. The project is fully configured for Claude Code development workflows.