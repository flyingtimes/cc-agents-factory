#!/usr/bin/env python3
"""
MCP Server for Audio Extraction
Extracts audio from video files using ffmpeg
"""

import asyncio
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try to import MCP components
try:
    from mcp.server import Server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        Tool,
        TextContent,
    )
    from mcp.server.stdio import stdio_server
except ImportError:
    print("Error: MCP package not found. Please install it with: pip install mcp")
    sys.exit(1)

# Create server instance
server = Server("extract-audio-mcp")

# Audio extraction tool definition
EXTRACT_AUDIO_TOOL = Tool(
    name="extract_audio",
    description="Extract audio from video files using ffmpeg. Supports local files and URLs.",
    inputSchema={
        "type": "object",
        "properties": {
            "input_path": {
                "type": "string",
                "description": "Path to local video file or URL to video"
            },
            "output_name": {
                "type": "string",
                "description": "Optional custom name for output file (without extension)",
                "required": False
            },
            "output_dir": {
                "type": "string",
                "description": "Output directory (default: ../outputs)",
                "default": "../outputs"
            },
            "audio_quality": {
                "type": "string",
                "description": "Audio quality preset (low, medium, high)",
                "default": "medium",
                "enum": ["low", "medium", "high"]
            }
        },
        "required": ["input_path"]
    }
)

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [EXTRACT_AUDIO_TOOL]

@server.call_tool()
async def call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls."""
    tool_name = request.params.name
    arguments = request.params.arguments or {}
    
    if tool_name != "extract_audio":
        raise ValueError(f"Unknown tool: {tool_name}")
    
    return await extract_audio(arguments)

async def extract_audio(arguments: Dict[str, Any]) -> CallToolResult:
    """Extract audio from video file."""
    input_path = arguments.get("input_path")
    output_name = arguments.get("output_name")
    output_dir = arguments.get("output_dir", "../outputs")
    audio_quality = arguments.get("audio_quality", "medium")
    
    if not input_path:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Error: input_path is required"
            )]
        )
    
    # Generate UUID for unique filename
    file_uuid = str(uuid.uuid4())
    
    # Determine output filename
    if output_name:
        output_filename = f"{output_name}_{file_uuid}.mp3"
    else:
        # Extract filename from path
        if input_path.startswith(("http://", "https://")):
            filename = "url_audio"
        else:
            filename = Path(input_path).stem
        output_filename = f"{filename}_{file_uuid}.mp3"
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / output_filename
    
    # Set audio quality parameters
    quality_settings = {
        "low": {"bitrate": "128k", "sample_rate": "44100"},
        "medium": {"bitrate": "192k", "sample_rate": "44100"},
        "high": {"bitrate": "320k", "sample_rate": "48000"}
    }
    
    quality = quality_settings.get(audio_quality, quality_settings["medium"])
    
    try:
        # Build ffmpeg command
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vn",  # No video
            "-acodec", "libmp3lame",
            "-ab", quality["bitrate"],
            "-ar", quality["sample_rate"],
            "-y",  # Overwrite output file
            str(output_file)
        ]
        
        # Run ffmpeg
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # Get file info
            file_size = output_file.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            result_text = f"""Audio extraction completed successfully!

Input: {input_path}
Output: {output_file}
File Size: {file_size_mb:.2f} MB
Quality: {audio_quality} ({quality['bitrate']} @ {quality['sample_rate']}Hz)
UUID: {file_uuid}

The audio file has been saved with a unique filename to prevent conflicts."""
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=result_text
                )]
            )
        else:
            error_text = stderr.decode('utf-8', errors='ignore')
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Error extracting audio: {error_text}"
                )]
            )
            
    except FileNotFoundError:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Error: ffmpeg not found. Please install ffmpeg and add it to your PATH."
            )]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )]
        )

async def main():
    """Run the MCP server."""
    # Start the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())