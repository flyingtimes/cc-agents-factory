#!/usr/bin/env python3
"""
Test script for FastMCP Audio Transcription Server
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from server import SenseVoiceTranscriber, TranscribeAudioParams, TranscriptionResult


def test_dependencies():
    """Test if all dependencies are available"""
    print("Testing dependencies...")
    
    transcriber = SenseVoiceTranscriber()
    deps_ok = transcriber.check_dependencies()
    
    if deps_ok:
        print("✅ All dependencies are available")
        return True
    else:
        print("❌ Some dependencies are missing")
        return False


def test_parameter_validation():
    """Test parameter validation"""
    print("\nTesting parameter validation...")
    
    # Test valid parameters
    try:
        params = TranscribeAudioParams(
            input_path="test.mp3",
            language="auto"
        )
        print("✅ Valid parameters accepted")
    except Exception as e:
        print(f"❌ Valid parameters rejected: {e}")
        return False
    
    # Test invalid language
    try:
        params = TranscribeAudioParams(
            input_path="test.mp3",
            language="invalid"
        )
        print("❌ Invalid language should be rejected")
        return False
    except Exception:
        print("✅ Invalid language correctly rejected")
    
    return True


def test_model_loading():
    """Test model loading (may take time)"""
    print("\nTesting model loading...")
    
    transcriber = SenseVoiceTranscriber()
    
    try:
        success = transcriber.load_model()
        if success:
            print("✅ SenseVoice model loaded successfully")
            return True
        else:
            print("❌ Failed to load SenseVoice model")
            return False
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False


def test_file_structure():
    """Test if required directories exist"""
    print("\nTesting file structure...")
    
    models_dir = Path(__file__).parent.parent.parent / "models"
    outputs_dir = Path(__file__).parent.parent.parent / "outputs"
    
    models_ok = models_dir.exists()
    outputs_ok = outputs_dir.exists()
    
    if models_ok:
        print("✅ Models directory exists")
    else:
        print("❌ Models directory missing")
    
    if outputs_ok:
        print("✅ Outputs directory exists")
    else:
        print("❌ Outputs directory missing")
    
    return models_ok and outputs_ok


async def test_transcription_logic():
    """Test transcription logic (without actual file)"""
    print("\nTesting transcription logic...")
    
    transcriber = SenseVoiceTranscriber()
    
    # Test with non-existent file
    result = await transcriber.transcribe_audio("non_existent.mp3")
    
    if not result["success"] and "Input file not found" in result["error"]:
        print("✅ Non-existent file correctly handled")
        return True
    else:
        print("❌ Non-existent file not handled correctly")
        return False


def main():
    """Run all tests"""
    print("FastMCP Audio Transcription Server - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Parameter Validation", test_parameter_validation),
        ("File Structure", test_file_structure),
        ("Model Loading", test_model_loading),
        ("Transcription Logic", test_transcription_logic),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        
        if asyncio.iscoroutinefunction(test_func):
            result = asyncio.run(test_func())
        else:
            result = test_func()
        
        if result:
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The FastMCP server is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)