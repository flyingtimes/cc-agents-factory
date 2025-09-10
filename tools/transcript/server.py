#!/usr/bin/env python3
"""
MCP Server for Audio Transcription using Whisper
"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from mcp import ClientSession, StdioServerParameters
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import pydantic
from pydantic import BaseModel

# Import required libraries
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create server instance
server = Server("transcript-mcp")

class ProgressTracker:
    """Track and display transcription progress"""
    def __init__(self):
        self.start_time = None
        self.last_update = 0
        self.progress_chars = ['/', '-', '\\', '|']
        self.char_index = 0
        
    def start(self):
        """Start progress tracking"""
        self.start_time = time.time()
        self.last_update = 0
        self.char_index = 0
        
    def update(self, status=""):
        """Update progress display"""
        current_time = time.time()
        if current_time - self.last_update < 0.2:  # Update every 200ms
            return
            
        self.last_update = current_time
        
        if self.start_time:
            elapsed = current_time - self.start_time
            char = self.progress_chars[self.char_index % len(self.progress_chars)]
            self.char_index += 1
            
            # Clear line and show progress
            sys.stdout.write(f'\r{char} 转录中... {status} ({elapsed:.1f}s)')
            sys.stdout.flush()
    
    def finish(self):
        """Finish progress display"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            sys.stdout.write(f'\r转录完成! (耗时: {elapsed:.1f}s)\n')
            sys.stdout.flush()

progress_tracker = ProgressTracker()

# Set custom model path
MODELS_DIR = Path(__file__).parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Set environment variable for models
os.environ["XDG_CACHE_HOME"] = str(MODELS_DIR.parent)

class TranscribeAudioParams(BaseModel):
    """Parameters for audio transcription"""
    input_path: str
    output_name: Optional[str] = None
    output_dir: Optional[str] = None
    model_size: str = "base"
    language: Optional[str] = None

class TranscriptionResult(BaseModel):
    """Result of audio transcription"""
    success: bool
    text: str
    output_file: str
    processing_time: float
    model_used: str
    language_detected: Optional[str] = None
    error: Optional[str] = None

@server.list_tools()
async def handle_list_tools() -> List[Dict[str, Any]]:
    """List available tools"""
    return [
        {
            "name": "transcribe_audio",
            "description": "Transcribe audio file to text using GGUF Whisper model",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Path to audio file (MP3, WAV, M4A, etc.)"
                    },
                    "output_name": {
                        "type": "string",
                        "description": "Custom output filename (without extension)"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Output directory (default: ../outputs)"
                    },
                    "model_size": {
                        "type": "string",
                        "enum": ["tiny", "base", "small", "medium", "large"],
                        "description": "Whisper model size (tiny=fastest, large=most accurate)"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code (e.g., 'en', 'zh', 'ja', 'auto')"
                    }
                },
                "required": ["input_path"]
            }
        }
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Handle tool calls"""
    if name != "transcribe_audio":
        raise ValueError(f"Unknown tool: {name}")
    
    try:
        # Parse parameters
        params = TranscribeAudioParams(**arguments)
        
        # Validate input file
        input_path = Path(params.input_path)
        if not input_path.exists():
            return [{
                "type": "text",
                "text": json.dumps(TranscriptionResult(
                    success=False,
                    text="",
                    output_file="",
                    processing_time=0.0,
                    model_used=params.model_size,
                    error=f"Input file not found: {params.input_path}"
                ).dict(), indent=2)
            }]
        
        # Set output directory
        output_dir = Path(params.output_dir) if params.output_dir else Path(__file__).parent.parent.parent / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set output filename
        output_name = params.output_name or input_path.stem
        unique_id = str(uuid.uuid4())[:8]
        output_file = output_dir / f"{output_name}_{unique_id}.txt"
        
        # Transcribe audio
        start_time = asyncio.get_event_loop().time()
        
        # Check dependencies
        if not WHISPER_AVAILABLE:
            return [{
                "type": "text",
                "text": json.dumps(TranscriptionResult(
                    success=False,
                    text="",
                    output_file="",
                    processing_time=0.0,
                    model_used=params.model_size,
                    error="Whisper not installed. Please install with: pip install openai-whisper"
                ).dict(), indent=2)
            }]
        
        if not TORCH_AVAILABLE:
            return [{
                "type": "text",
                "text": json.dumps(TranscriptionResult(
                    success=False,
                    text="",
                    output_file="",
                    processing_time=0.0,
                    model_used=params.model_size,
                    error="PyTorch not installed. Please install with: pip install torch"
                ).dict(), indent=2)
            }]
        
        try:
            # Start progress tracking
            progress_tracker.start()
            print(f"开始转录音频文件: {input_path.name}")
            
            # Load Whisper model
            progress_tracker.update("加载模型中...")
            try:
                model = whisper.load_model(params.model_size)
                logger.info(f"Loaded Whisper model: {params.model_size}")
            except Exception as model_error:
                logger.error(f"Failed to load Whisper model: {model_error}")
                return [{
                    "type": "text",
                    "text": json.dumps(TranscriptionResult(
                        success=False,
                        text="",
                        output_file="",
                        processing_time=0.0,
                        model_used=params.model_size,
                        error=f"Failed to load Whisper model: {str(model_error)}"
                    ).dict(), indent=2)
                }]
            
            # Transcribe audio
            progress_tracker.update("转录中...")
            try:
                # Prepare transcription options
                options = {}
                if params.language and params.language != "auto":
                    options["language"] = params.language
                
                # Transcribe
                result = model.transcribe(str(input_path), **options)
                transcription = result["text"]
                detected_language = result.get("language", params.language)
                
                logger.info(f"Transcription completed. Language: {detected_language}")
                
            except Exception as transcribe_error:
                logger.error(f"Failed to transcribe audio: {transcribe_error}")
                return [{
                    "type": "text",
                    "text": json.dumps(TranscriptionResult(
                        success=False,
                        text="",
                        output_file="",
                        processing_time=0.0,
                        model_used=params.model_size,
                        error=f"Failed to transcribe audio: {str(transcribe_error)}"
                    ).dict(), indent=2)
                }]
            
            processing_time = asyncio.get_event_loop().time() - start_time
            progress_tracker.finish()
            
            # Save transcription
            async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
                await f.write(transcription)
            
            # Create response
            transcription_result = TranscriptionResult(
                success=True,
                text=transcription,
                output_file=str(output_file),
                processing_time=processing_time,
                model_used=params.model_size,
                language_detected=detected_language
            )
            
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Transcription failed: {e}")
            return [{
                "type": "text",
                "text": json.dumps(TranscriptionResult(
                    success=False,
                    text="",
                    output_file="",
                    processing_time=processing_time,
                    model_used=params.model_size,
                    error=f"Transcription failed: {str(e)}"
                ).dict(), indent=2)
            }]
        
        return [{
            "type": "text",
            "text": json.dumps(transcription_result.dict(), indent=2)
        }]
        
    except Exception as e:
        logger.error(f"Error in transcribe_audio: {e}")
        return [{
            "type": "text",
            "text": json.dumps(TranscriptionResult(
                success=False,
                text="",
                output_file="",
                processing_time=0.0,
                model_used="medium",
                error=f"Parameter error: {str(e)}"
            ).dict(), indent=2)
        }]

async def main():
    """Run the MCP server"""
    # Run the server using stdin/stdout
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="transcript-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    try:
        import mcp.server.stdio
        asyncio.run(main())
    except ImportError:
        print("MCP package not installed. Please install with: pip install mcp")
    except Exception as e:
        print(f"Error starting server: {e}")