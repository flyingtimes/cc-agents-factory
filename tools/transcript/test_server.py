#!/usr/bin/env python3
"""
Test script for Transcript MCP Server
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Add the server directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from server import TranscribeAudioParams, TranscriptionResult

def test_parameter_validation():
    """Test parameter validation"""
    print("Testing parameter validation...")
    
    # Test valid parameters
    try:
        params = TranscribeAudioParams(input_path="test.mp3")
        print("✓ Valid parameters accepted")
    except Exception as e:
        print(f"✗ Valid parameters rejected: {e}")
        return False
    
    # Test missing required parameter
    try:
        params = TranscribeAudioParams()
        print("✗ Missing required parameter not caught")
        return False
    except Exception:
        print("✓ Missing required parameter caught")
    
    # Test invalid model size - this won't be caught by Pydantic since it's a string field
    try:
        params = TranscribeAudioParams(input_path="test.mp3", model_size="invalid")
        print("✓ Invalid model size handled (string field accepts any value)")
    except Exception:
        print("✓ Invalid model size caught")
    
    return True

def test_transcription_result():
    """Test transcription result model"""
    print("\nTesting transcription result model...")
    
    try:
        result = TranscriptionResult(
            success=True,
            text="Test transcription",
            output_file="test.txt",
            processing_time=1.5,
            model_used="medium",
            language_detected="en"
        )
        print("✓ Valid transcription result created")
        
        # Test JSON serialization
        json_str = json.dumps(result.model_dump(), indent=2)
        parsed_back = TranscriptionResult(**json.loads(json_str))
        print("✓ JSON serialization/deserialization works")
        
    except Exception as e:
        print(f"✗ Transcription result model failed: {e}")
        return False
    
    return True

def test_dependencies():
    """Test if required dependencies are available"""
    print("\nTesting dependencies...")
    
    missing_deps = []
    
    try:
        import ctransformers
        print("✓ CTransformers is available")
    except ImportError:
        missing_deps.append("ctransformers")
        print("✗ CTransformers not available")
    
    try:
        import modelscope
        print("✓ ModelScope is available")
    except ImportError:
        missing_deps.append("modelscope")
        print("✗ ModelScope not available")
    
    try:
        import librosa
        print("✓ Librosa is available")
    except ImportError:
        missing_deps.append("librosa")
        print("✗ Librosa not available")
    
    try:
        import mcp
        print("✓ MCP is available")
    except ImportError:
        missing_deps.append("mcp")
        print("✗ MCP not available")
    
    try:
        import pydantic
        print("✓ Pydantic is available")
    except ImportError:
        missing_deps.append("pydantic")
        print("✗ Pydantic not available")
    
    try:
        import aiofiles
        print("✓ aiofiles is available")
    except ImportError:
        missing_deps.append("aiofiles")
        print("✗ aiofiles not available")
    
    if missing_deps:
        print(f"\nMissing dependencies: {', '.join(missing_deps)}")
        print(f"Install with: pip install {' '.join(missing_deps)}")
        return False
    
    return True

def test_output_directory_creation():
    """Test output directory creation"""
    print("\nTesting output directory creation...")
    
    try:
        # Test default output directory
        default_output = Path(__file__).parent.parent / "outputs"
        default_output.mkdir(parents=True, exist_ok=True)
        print("✓ Default output directory created")
        
        # Test custom output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_output = Path(temp_dir) / "custom_output"
            custom_output.mkdir(parents=True, exist_ok=True)
            print("✓ Custom output directory created")
        
        return True
        
    except Exception as e:
        print(f"✗ Output directory creation failed: {e}")
        return False

def test_uuid_generation():
    """Test UUID generation for unique filenames"""
    print("\nTesting UUID generation...")
    
    try:
        import uuid
        
        # Generate multiple UUIDs and check uniqueness
        uuids = [str(uuid.uuid4())[:8] for _ in range(10)]
        unique_uuids = set(uuids)
        
        if len(uuids) == len(unique_uuids):
            print("✓ UUID generation produces unique identifiers")
            return True
        else:
            print("✗ UUID generation produced duplicates")
            return False
            
    except Exception as e:
        print(f"✗ UUID generation failed: {e}")
        return False

def test_server_import():
    """Test if server module can be imported"""
    print("\nTesting server import...")
    
    try:
        from server import server, main, MODELS_DIR
        print("✓ Server module imported successfully")
        
        # Test server initialization
        if hasattr(server, 'list_tools'):
            print("✓ Server has list_tools method")
        else:
            print("✗ Server missing list_tools method")
            return False
            
        if hasattr(server, 'call_tool'):
            print("✓ Server has call_tool method")
        else:
            print("✗ Server missing call_tool method")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Server import failed: {e}")
        return False

def test_models_directory():
    """Test models directory setup"""
    print("\nTesting models directory setup...")
    
    try:
        from server import MODELS_DIR
        
        # Check if models directory exists
        if MODELS_DIR.exists():
            print("✓ Models directory exists")
        else:
            print("✗ Models directory does not exist")
            return False
        
        # Check if it's in the correct location
        expected_path = Path(__file__).parent.parent / "models"
        if MODELS_DIR == expected_path:
            print("✓ Models directory is in correct location")
        else:
            print(f"✗ Models directory path mismatch: {MODELS_DIR} != {expected_path}")
            return False
        
        # Test directory permissions
        test_file = MODELS_DIR / "test_permission.tmp"
        try:
            test_file.touch()
            test_file.unlink()
            print("✓ Models directory has write permissions")
        except Exception as e:
            print(f"✗ Models directory permission error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Models directory test failed: {e}")
        return False

def test_model_path_configuration():
    """Test model path environment variables"""
    print("\nTesting model path configuration...")
    
    try:
        import os
        from server import MODELS_DIR
        
        # Check if GGUF model path exists
        model_dir = MODELS_DIR / "OllmOne" / "whisper-large-v3-GGUF"
        gguf_files = list(model_dir.glob("*.gguf"))
        if gguf_files:
            print("✓ GGUF model file exists")
            print(f"✓ Model file: {gguf_files[0].name}")
            print(f"✓ Model size: {gguf_files[0].stat().st_size / (1024*1024):.1f} MB")
        else:
            print("✓ GGUF model file does not exist (will be downloaded on first use)")
        
        if "XDG_CACHE_HOME" in os.environ:
            expected_cache = str(MODELS_DIR.parent)
            if os.environ["XDG_CACHE_HOME"] == expected_cache:
                print("✓ XDG_CACHE_HOME environment variable is set correctly")
            else:
                print("✗ XDG_CACHE_HOME environment variable is incorrect")
                return False
        else:
            print("✗ XDG_CACHE_HOME environment variable is not set")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Model path configuration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Transcript MCP Server Test Suite ===\n")
    
    tests = [
        ("Parameter Validation", test_parameter_validation),
        ("Transcription Result Model", test_transcription_result),
        ("Dependencies", test_dependencies),
        ("Output Directory Creation", test_output_directory_creation),
        ("UUID Generation", test_uuid_generation),
        ("Server Import", test_server_import),
        ("Models Directory", test_models_directory),
        ("Model Path Configuration", test_model_path_configuration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✓ {test_name} passed\n")
        else:
            failed += 1
            print(f"✗ {test_name} failed\n")
    
    print("=== Test Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! The server is ready for use.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())