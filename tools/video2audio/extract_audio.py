#!/usr/bin/env python3
"""
Video to Audio Extraction Tool
Extracts audio from video files using ffmpeg with various quality options.
"""

import os
import subprocess
import uuid
from pathlib import Path
from typing import Optional


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
    
    def extract_audio(self, input_path: str, output_name: str = None, 
                     quality: str = "medium") -> str:
        """
        Extract audio from video file.
        
        Args:
            input_path: Path to video file
            output_name: Custom output filename (without extension)
            quality: Audio quality (low/medium/high)
        
        Returns:
            Path to the extracted audio file
        
        Raises:
            ValueError: If input file doesn't exist or quality is invalid
            RuntimeError: If ffmpeg is not available or extraction fails
        """
        # Validate input
        if not Path(input_path).exists():
            raise ValueError(f"Input file does not exist: {input_path}")
        
        if quality not in self.quality_presets:
            raise ValueError(f"Invalid quality. Must be one of: {list(self.quality_presets.keys())}")
        
        # Check ffmpeg availability
        if not self.check_ffmpeg():
            raise RuntimeError("ffmpeg is not available or not in PATH")
        
        # Generate output filename
        if output_name is None:
            output_name = f"video_{Path(input_path).stem}_audio"
        
        # Add UUID for uniqueness
        unique_name = f"{output_name}_{uuid.uuid4().hex[:8]}"
        output_path = self.output_dir / f"{unique_name}.mp3"
        
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
            str(output_path)           # Output file
        ]
        
        try:
            # Run ffmpeg
            print(f"Extracting audio from {input_path}...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg failed: {result.stderr}")
            
            print(f"Audio extracted successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            # Clean up partial file if it exists
            if output_path.exists():
                output_path.unlink()
            raise RuntimeError(f"Failed to extract audio: {str(e)}")


def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract audio from video files")
    parser.add_argument("input_path", help="Path to video file")
    parser.add_argument("-o", "--output-name", help="Custom output filename")
    parser.add_argument("-q", "--quality", choices=["low", "medium", "high"], 
                       default="medium", help="Audio quality")
    parser.add_argument("-d", "--output-dir", help="Output directory")
    
    args = parser.parse_args()
    
    extractor = VideoToAudioExtractor(args.output_dir)
    
    try:
        output_file = extractor.extract_audio(
            args.input_path, 
            args.output_name, 
            args.quality
        )
        print(f"Success! Audio saved to: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())