# FastMCP Audio Transcription Server

This is a FastMCP server implementation for audio transcription using the SenseVoice model. It provides powerful audio-to-text capabilities with automatic chunking for long audio files and multi-language support.

## Features

- **SenseVoice Model Integration**: Uses FunASR's SenseVoiceSmall model for high-quality speech recognition
- **Long Audio Support**: Automatic chunking for audio files longer than 10 minutes
- **Multi-language Support**: Supports Chinese (zh), English (en), Cantonese (yue), Japanese (ja), Korean (ko), and auto-detection
- **Real-time Progress**: Visual progress tracking during transcription
- **Smart Chunking**: Overlapping chunks to ensure no content is lost at boundaries
- **Error Handling**: Comprehensive error handling and recovery
- **Output Management**: UUID-based naming for unique output files

## Quick Start

### 1. Installation

```bash
# Navigate to the server directory
cd tools/audio2txt-fastmcp

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Server

```bash
# Start the FastMCP server
python server.py
```

### 3. Use the Tool

In your Claude Code session, you can now use the `transcribe_audio_sensevoice` tool:

```json
{
  "name": "transcribe_audio_sensevoice",
  "arguments": {
    "input_path": "assets/1.mp3",
    "output_name": "my_transcript",
    "language": "auto"
  }
}
```

## Tool Parameters

### Required Parameters
- `input_path`: Path to audio file (MP3, WAV, M4A, etc.)

### Optional Parameters
- `output_name`: Custom output filename (without extension)
- `output_dir`: Output directory (default: ../outputs)
- `language`: Language code (auto, zh, en, yue, ja, ko) - defaults to "auto"

## Configuration

The server uses the following configuration:

- **Models Directory**: `/models` (project root) - stores SenseVoice model files
- **Output Directory**: `/outputs` (project root) - stores transcription results
- **Chunk Duration**: 10 minutes (600 seconds) - splits long audio into chunks
- **Overlap Duration**: 5 seconds - ensures seamless transcription at chunk boundaries

## Dependencies

Core dependencies:
- `fastmcp>=0.3.0` - FastMCP framework
- `funasr>=1.0.0` - SenseVoice model and speech recognition
- `librosa>=0.10.0` - Audio loading and processing
- `soundfile>=0.12.0` - Audio file I/O
- `torch>=2.0.0` - PyTorch for model inference
- `aiofiles>=23.0.0` - Async file operations
- `pydantic>=2.0.0` - Data modeling and validation

## GPU Support

The server automatically detects and uses CUDA if available. For GPU acceleration:

1. Install PyTorch with CUDA support
2. The server will automatically use `cuda:0` device when available

## Output Format

The tool returns a JSON object with the following structure:

```json
{
  "success": true,
  "text": "Transcribed text content...",
  "output_file": "/path/to/output/transcript_name_uuid.txt",
  "language_detected": "en",
  "duration": 120.5,
  "chunks_used": false,
  "processing_time": 15.3
}
```

## Error Handling

The server includes comprehensive error handling for:
- Missing dependencies
- Model loading failures
- Invalid audio files
- Network issues (for remote files)
- Permission and path errors
- Transcription failures

## Testing

```bash
# Test the server installation
python -c "import fastmcp; print('FastMCP installed successfully')"

# Test dependencies
python -c "import funasr, librosa, soundfile, torch; print('All dependencies available')"

# Run a basic test
python -c "
from server import SenseVoiceTranscriber
transcriber = SenseVoiceTranscriber()
print(f'Dependencies OK: {transcriber.check_dependencies()}')
"
```

## Deployment

### Local Development

```bash
# Start in development mode
python server.py

# Or use FastMCP CLI
fastmcp dev tools/audio2txt-fastmcp
```

### Production Deployment

```bash
# Install in production mode
pip install -r requirements.txt

# Start server
fastmcp run tools/audio2txt-fastmcp
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "server.py"]
```

## Integration with Claude Code

To use this server with Claude Code:

1. Add the server to your Claude Code configuration
2. The `transcribe_audio_sensevoice` tool will be available in your sessions
3. Use it to transcribe audio files with automatic chunking and multi-language support

## Performance Notes

- **Model Loading**: Initial model loading may take 30-60 seconds
- **Long Audio**: Files longer than 10 minutes are automatically chunked
- **GPU Acceleration**: CUDA provides 3-5x speedup for transcription
- **Memory Usage**: ~2GB RAM for model + processing
- **Chunk Processing**: Each chunk is processed sequentially to manage memory

## Troubleshooting

### Common Issues

1. **Model Not Downloading**: Check internet connection and model permissions
2. **CUDA Out of Memory**: Reduce batch size or use CPU mode
3. **Audio File Issues**: Ensure audio files are in supported formats
4. **Permission Errors**: Check write permissions for output directory

### Debug Mode

```bash
# Enable debug logging
export PYTHONPATH=/path/to/project
python server.py --log-level DEBUG
```

## Migration from Original MCP Server

This FastMCP version maintains full compatibility with the original MCP server implementation:

- Same tool interface and parameters
- Identical output format
- Same model and chunking behavior
- Compatible with existing workflows and scripts

The main differences are:
- Uses FastMCP framework instead of raw MCP
- Simplified server startup and configuration
- Better integration with FastMCP ecosystem