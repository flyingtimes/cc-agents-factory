#!/usr/bin/env python3
"""
FastMCP Server for Video to Audio Extraction using ffmpeg
"""

import asyncio
import json
import logging
import os
import subprocess
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiofiles
from fastmcp import FastMCP
import pydantic
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP("Video to Audio Extraction 🎵")

class VideoToAudioExtractor:
    """Extract audio from video files using ffmpeg."""
    
    def __init__(self, output_dir: str = None):
        """Initialize the extractor with output directory."""
        if output_dir is None:
            # Default to project outputs directory
            current_dir = Path(__file__).parent.parent.parent
            output_dir = current_dir / "outputs"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Quality presets (bitrate in kbps, sample rate in Hz)
        self.quality_presets = {
            "low": (128, 44100),
            "medium": (192, 44100),
            "high": (320, 48000)
        }
    
    def check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available."""
        try:
            result = subprocess.run(["ffmpeg", "-version"], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    async def extract_audio(self, input_path: str, output_name: str = None, 
                           quality: str = "medium", output_dir: str = None) -> Dict[str, Any]:
        """
        Extract audio from video file.
        
        Args:
            input_path: Path to video file
            output_name: Custom output filename (without extension)
            quality: Audio quality (low/medium/high)
            output_dir: Output directory
        
        Returns:
            Dictionary with extraction result
        """
        # Validate input
        if not Path(input_path).exists():
            return {
                "success": False,
                "error": f"Input file does not exist: {input_path}"
            }
        
        if quality not in self.quality_presets:
            return {
                "success": False,
                "error": f"Invalid quality. Must be one of: {list(self.quality_presets.keys())}"
            }
        
        # Check ffmpeg availability
        if not self.check_ffmpeg():
            return {
                "success": False,
                "error": "ffmpeg is not available or not in PATH"
            }
        
        # Set output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.output_dir
        output_path.mkdir(exist_ok=True)
        
        # Generate output filename
        if output_name is None:
            output_name = f"video_{Path(input_path).stem}_audio"
        
        # Add UUID for uniqueness
        unique_name = f"{output_name}_{uuid.uuid4().hex[:8]}"
        output_file = output_path / f"{unique_name}.mp3"
        
        # Get quality settings
        bitrate, sample_rate = self.quality_presets[quality]
        
        # Build ffmpeg command
        cmd = [
            "ffmpeg",
            "-i", input_path,          # Input file
            "-vn",                     # No video
            "-acodec", "libmp3lame",   # MP3 codec
            "-ab", f"{bitrate}k",      # Audio bitrate
            "-ar", str(sample_rate),   # Audio sample rate
            "-y",                      # Overwrite output file
            str(output_file)           # Output file
        ]
        
        try:
            # Run ffmpeg
            logger.info(f"Extracting audio from {input_path}...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"ffmpeg failed: {result.stderr}"
                }
            
            # Verify output file exists and has content
            if not output_file.exists() or output_file.stat().st_size == 0:
                return {
                    "success": False,
                    "error": "Output file was not created or is empty"
                }
            
            logger.info(f"Audio extracted successfully: {output_file}")
            
            return {
                "success": True,
                "output_file": str(output_file),
                "file_size": output_file.stat().st_size,
                "quality": quality,
                "bitrate": bitrate,
                "sample_rate": sample_rate
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Audio extraction timed out (5 minutes limit exceeded)"
            }
        except Exception as e:
            # Clean up partial file if it exists
            if output_file.exists():
                output_file.unlink()
            return {
                "success": False,
                "error": f"Failed to extract audio: {str(e)}"
            }

class ExtractAudioParams(BaseModel):
    """Parameters for audio extraction"""
    input_path: str
    output_name: Optional[str] = None
    output_dir: Optional[str] = None
    audio_quality: str = "medium"
    
    @pydantic.field_validator('audio_quality')
    @classmethod
    def validate_audio_quality(cls, v):
        if v not in ["low", "medium", "high"]:
            raise ValueError('audio_quality must be one of: low, medium, high')
        return v

class ExtractionResult(BaseModel):
    """Result of audio extraction"""
    success: bool
    output_file: Optional[str] = None
    file_size: Optional[int] = None
    quality: Optional[str] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    error: Optional[str] = None

@mcp.tool()
async def extract_audio_from_video(
    input_path: str,
    output_name: Optional[str] = None,
    output_dir: Optional[str] = None,
    audio_quality: str = "medium"
) -> str:
    """
    Extract audio from video files using ffmpeg
    
    Args:
        input_path: Path to video file (MP4, AVI, MOV, etc.)
        output_name: Custom output filename (without extension)
        output_dir: Output directory (default: ../outputs)
        audio_quality: Audio quality: low (128kbps), medium (192kbps), high (320kbps)
    
    Returns:
        JSON string with extraction result
    """
    try:
        # Parse parameters
        params = ExtractAudioParams(
            input_path=input_path,
            output_name=output_name,
            output_dir=output_dir,
            audio_quality=audio_quality
        )
        
        # Initialize extractor
        extractor = VideoToAudioExtractor()
        
        # Extract audio
        start_time = asyncio.get_event_loop().time()
        result = await extractor.extract_audio(
            input_path=params.input_path,
            output_name=params.output_name,
            quality=params.audio_quality,
            output_dir=params.output_dir
        )
        processing_time = asyncio.get_event_loop().time() - start_time
        
        # Create result object
        extraction_result = ExtractionResult(
            success=result["success"],
            output_file=result.get("output_file"),
            file_size=result.get("file_size"),
            quality=result.get("quality"),
            bitrate=result.get("bitrate"),
            sample_rate=result.get("sample_rate"),
            error=result.get("error")
        )
        
        if result["success"]:
            # Add processing time to successful results
            result_dict = extraction_result.dict()
            result_dict["processing_time"] = processing_time
            result_dict["message"] = f"Audio extracted successfully in {processing_time:.2f} seconds"
        else:
            result_dict = extraction_result.dict()
            result_dict["processing_time"] = processing_time
        
        return json.dumps(result_dict, indent=2, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Error in extract_audio_from_video: {e}")
        error_result = ExtractionResult(
            success=False,
            error=f"Parameter error: {str(e)}"
        )
        return json.dumps(error_result.dict(), indent=2, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()