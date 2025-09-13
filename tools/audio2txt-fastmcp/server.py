#!/usr/bin/env python3
"""
FastMCP Server for Audio Transcription using SenseVoice

This server provides audio transcription capabilities using the SenseVoice model
with support for long audio chunking and multiple languages.
Converted from original MCP server to FastMCP framework.
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
import librosa
import numpy as np
import soundfile as sf
import torch
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from fastmcp import FastMCP
from pydantic import BaseModel, field_validator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP("audio2txt-fastmcp")

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
            sys.stdout.write(f'\r{char} 处理中... {status} ({elapsed:.1f}s)')
            sys.stdout.flush()
    
    def finish(self):
        """Finish progress display"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            sys.stdout.write(f'\r处理完成! (耗时: {elapsed:.1f}s)\n')
            sys.stdout.flush()

progress_tracker = ProgressTracker()

# Set custom model and output paths
MODELS_DIR = Path(__file__).parent.parent.parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUTS_DIR = Path(__file__).parent.parent.parent / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Set environment variables for models to use local directory only
os.environ["XDG_CACHE_HOME"] = str(MODELS_DIR.parent)
os.environ["HF_HOME"] = str(MODELS_DIR)
os.environ["HF_HUB_CACHE"] = str(MODELS_DIR)
os.environ["TRANSFORMERS_CACHE"] = str(MODELS_DIR)

class SenseVoiceTranscriber:
    """SenseVoice audio transcription with chunking support"""
    
    def __init__(self):
        """Initialize the transcriber"""
        self.model = None
        self.model_name = "iic/SenseVoiceSmall"
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
        # Audio chunking settings
        self.chunk_duration = 600  # 10 minutes in seconds
        self.overlap_duration = 5  # 5 seconds overlap between chunks
        
        logger.info(f"Initialized SenseVoiceTranscriber")
        logger.info(f"Models directory: {MODELS_DIR}")
        logger.info(f"Output directory: {OUTPUTS_DIR}")
        logger.info(f"Device: {self.device}")
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        try:
            import funasr
            logger.info(f"FunASR version: {funasr.__version__}")
        except ImportError:
            logger.error("FunASR not installed. Please install with: pip install funasr")
            return False
        
        try:
            import librosa
            logger.info(f"Librosa version: {librosa.__version__}")
        except ImportError:
            logger.error("Librosa not installed. Please install with: pip install librosa")
            return False
        
        try:
            import soundfile
            logger.info(f"Soundfile version: {soundfile.__version__}")
        except ImportError:
            logger.error("Soundfile not installed. Please install with: pip install soundfile")
            return False
        
        try:
            import torch
            logger.info(f"PyTorch version: {torch.__version__}")
            logger.info(f"CUDA available: {torch.cuda.is_available()}")
        except ImportError:
            logger.error("PyTorch not installed. Please install with: pip install torch")
            return False
        
        return True
    
    def load_model(self) -> bool:
        """Load the SenseVoice model"""
        try:
            logger.info("Loading SenseVoice model...")
            
            # Load model with VAD for better long audio processing
            self.model = AutoModel(
                model=self.model_name,
                trust_remote_code=True,
                vad_model="fsmn-vad",
                vad_kwargs={"max_single_segment_time": 30000},  # 30 seconds max segment
                device=self.device,
            )
            
            logger.info("SenseVoice model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load SenseVoice model: {e}")
            return False
    
    def get_audio_duration(self, audio_path: Path) -> float:
        """Get the duration of an audio file"""
        try:
            duration = librosa.get_duration(path=str(audio_path))
            return duration
        except Exception as e:
            logger.error(f"Failed to get audio duration: {e}")
            return 0.0
    
    def split_audio(self, audio_path: Path, chunk_duration: int, overlap_duration: int) -> List[tuple]:
        """
        Split audio file into chunks.
        
        Args:
            audio_path: Path to audio file
            chunk_duration: Duration of each chunk in seconds
            overlap_duration: Overlap between chunks in seconds
        
        Returns:
            List of tuples (chunk_path, start_time, end_time)
        """
        logger.info(f"Splitting audio into {chunk_duration}s chunks with {overlap_duration}s overlap")
        
        # Load audio
        audio, sr = librosa.load(str(audio_path), sr=None)
        total_duration = len(audio) / sr
        
        chunks = []
        chunk_samples = chunk_duration * sr
        overlap_samples = overlap_duration * sr
        hop_samples = chunk_samples - overlap_samples
        
        start_sample = 0
        chunk_idx = 0
        
        while start_sample < len(audio):
            end_sample = min(start_sample + chunk_samples, len(audio))
            chunk_audio = audio[start_sample:end_sample]
            
            # Save chunk
            chunk_path = OUTPUTS_DIR / f"temp_chunk_{uuid.uuid4().hex[:8]}_{chunk_idx:03d}.wav"
            sf.write(str(chunk_path), chunk_audio, sr)
            
            start_time = start_sample / sr
            end_time = end_sample / sr
            
            chunks.append((chunk_path, start_time, end_time))
            
            logger.info(f"Created chunk {chunk_idx}: {start_time:.1f}s - {end_time:.1f}s")
            
            chunk_idx += 1
            start_sample += hop_samples
            
            # Stop if we've reached the end
            if end_sample >= len(audio):
                break
        
        logger.info(f"Created {len(chunks)} chunks from {total_duration:.1f}s audio")
        return chunks
    
    def transcribe_chunk(self, chunk_path: Path, language: str = "auto") -> Dict[str, Any]:
        """
        Transcribe a single audio chunk.
        
        Args:
            chunk_path: Path to audio chunk
            language: Language code (auto, zh, en, yue, ja, ko)
        
        Returns:
            Transcription result
        """
        try:
            # Transcribe with SenseVoice
            res = self.model.generate(
                input=str(chunk_path),
                cache={},
                language=language,
                use_itn=True,
                batch_size_s=60,
                merge_vad=True,
                merge_length_s=15,
            )
            
            # Post-process result
            text = rich_transcription_postprocess(res[0]["text"])
            
            return {
                "success": True,
                "text": text,
                "language": res[0].get("language", language),
            }
            
        except Exception as e:
            logger.error(f"Failed to transcribe chunk {chunk_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    async def transcribe_audio(self, audio_path: str, output_name: str = None, 
                              output_dir: str = None, language: str = "auto") -> Dict[str, Any]:
        """
        Transcribe audio file with automatic chunking for long audio.
        
        Args:
            audio_path: Path to audio file
            output_name: Custom output filename (without extension)
            output_dir: Output directory (default: project outputs/)
            language: Language code (auto, zh, en, yue, ja, ko)
        
        Returns:
            Transcription result
        """
        progress_tracker.start()
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Validate input file
            input_path = Path(audio_path)
            if not input_path.exists():
                return {
                    "success": False,
                    "error": f"Input file not found: {audio_path}",
                    "text": ""
                }
            
            # Set output directory
            if output_dir:
                output_path = Path(output_dir)
            else:
                output_path = OUTPUTS_DIR
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Get audio duration
            duration = self.get_audio_duration(input_path)
            if duration == 0:
                return {
                    "success": False,
                    "error": "Failed to get audio duration or file is corrupted",
                    "text": ""
                }
            
            progress_tracker.update(f"音频时长: {duration:.1f}s")
            
            # Check if chunking is needed
            if duration > self.chunk_duration:
                progress_tracker.update("音频较长，需要分块处理")
                chunks = self.split_audio(input_path, self.chunk_duration, self.overlap_duration)
                
                # Transcribe each chunk
                all_text = []
                detected_languages = []
                
                for i, (chunk_path, start_time, end_time) in enumerate(chunks):
                    progress_tracker.update(f"处理第 {i+1}/{len(chunks)} 块 ({start_time:.1f}s - {end_time:.1f}s)")
                    
                    result = self.transcribe_chunk(chunk_path, language)
                    
                    if result["success"]:
                        all_text.append(result["text"])
                        if result.get("language"):
                            detected_languages.append(result["language"])
                    else:
                        logger.warning(f"Failed to transcribe chunk {i}: {result.get('error', 'Unknown error')}")
                        all_text.append(f"[转录失败: {start_time:.1f}s - {end_time:.1f}s]")
                    
                    # Clean up chunk file
                    try:
                        chunk_path.unlink()
                    except:
                        pass
                
                # Merge results
                transcription = "\n\n".join(all_text)
                detected_language = max(set(detected_languages), key=detected_languages.count) if detected_languages else language
                
            else:
                # Single chunk transcription
                progress_tracker.update("音频较短，直接处理")
                result = self.transcribe_chunk(input_path, language)
                
                if result["success"]:
                    transcription = result["text"]
                    detected_language = result.get("language", language)
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "Transcription failed"),
                        "text": ""
                    }
            
            # Generate output filename
            if output_name is None:
                output_name = f"transcript_{input_path.stem}"
            
            unique_id = str(uuid.uuid4())[:8]
            output_file = output_path / f"{output_name}_{unique_id}.txt"
            
            # Save transcription
            async with aiofiles.open(output_file, 'w', encoding='utf-8') as f:
                await f.write(transcription)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            progress_tracker.finish()
            
            return {
                "success": True,
                "text": transcription,
                "output_file": str(output_file),
                "language_detected": detected_language,
                "duration": duration,
                "chunks_used": duration > self.chunk_duration,
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            progress_tracker.finish()
            logger.error(f"Transcription failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "processing_time": processing_time
            }

class TranscribeAudioParams(BaseModel):
    """Parameters for audio transcription"""
    input_path: str
    output_name: Optional[str] = None
    output_dir: Optional[str] = None
    language: str = "auto"
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        valid_languages = ["auto", "zh", "en", "yue", "ja", "ko"]
        if v not in valid_languages:
            raise ValueError(f'language must be one of: {valid_languages}')
        return v

class TranscriptionResult(BaseModel):
    """Result of audio transcription"""
    success: bool
    text: str
    output_file: Optional[str] = None
    language_detected: Optional[str] = None
    duration: Optional[float] = None
    chunks_used: Optional[bool] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None

@mcp.tool()
async def transcribe_audio_sensevoice(
    input_path: str,
    output_name: str = None,
    output_dir: str = None,
    language: str = "auto"
) -> Dict[str, Any]:
    """
    Transcribe audio file to text using SenseVoice model with automatic chunking for long audio.
    
    Args:
        input_path: Path to audio file (MP3, WAV, M4A, etc.)
        output_name: Custom output filename (without extension)
        output_dir: Output directory (default: ../outputs)
        language: Language code for transcription (auto for automatic detection)
    
    Returns:
        Transcription result with text, metadata, and output file path
    """
    try:
        # Parse parameters
        params = TranscribeAudioParams(
            input_path=input_path,
            output_name=output_name,
            output_dir=output_dir,
            language=language
        )
        
        # Initialize transcriber
        transcriber = SenseVoiceTranscriber()
        
        # Check dependencies
        if not transcriber.check_dependencies():
            return TranscriptionResult(
                success=False,
                text="",
                error="Required dependencies not found. Please install: funasr, librosa, soundfile, torch"
            ).dict()
        
        # Load model
        if not transcriber.load_model():
            return TranscriptionResult(
                success=False,
                text="",
                error="Failed to load SenseVoice model"
            ).dict()
        
        # Transcribe audio
        result = await transcriber.transcribe_audio(
            audio_path=params.input_path,
            output_name=params.output_name,
            output_dir=params.output_dir,
            language=params.language
        )
        
        # Create result object
        transcription_result = TranscriptionResult(
            success=result["success"],
            text=result["text"],
            output_file=result.get("output_file"),
            language_detected=result.get("language_detected"),
            duration=result.get("duration"),
            chunks_used=result.get("chunks_used"),
            processing_time=result.get("processing_time"),
            error=result.get("error")
        )
        
        return transcription_result.dict()
        
    except Exception as e:
        logger.error(f"Error in transcribe_audio_sensevoice: {e}")
        return TranscriptionResult(
            success=False,
            text="",
            error=f"Parameter error: {str(e)}"
        ).dict()

if __name__ == "__main__":
    # Run the FastMCP server
    mcp.run()