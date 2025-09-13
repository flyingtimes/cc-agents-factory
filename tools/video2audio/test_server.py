#!/usr/bin/env python3
"""
Test script for video2audio MCP server
"""

import asyncio
import json
import sys
import pydantic
from pathlib import Path

# Add the tools directory to the path
sys.path.append(str(Path(__file__).parent))

from server import VideoToAudioExtractor, ExtractAudioParams
import aiofiles

async def test_extractor():
    """Test the audio extractor with sample video"""
    print("Testing VideoToAudioExtractor...")
    
    # Initialize extractor
    extractor = VideoToAudioExtractor()
    
    # Test with assets/2.mp4
    input_path = Path(__file__).parent.parent.parent / "assets" / "2.mp4"
    
    if not input_path.exists():
        print(f"❌ Test video file not found: {input_path}")
        return False
    
    print(f"✅ Found test video: {input_path}")
    
    # Test ffmpeg availability
    if not extractor.check_ffmpeg():
        print("❌ ffmpeg is not available")
        return False
    print("✅ ffmpeg is available")
    
    # Test audio extraction
    print("🔄 Testing audio extraction...")
    result = await extractor.extract_audio(str(input_path), output_name="test_mcp", quality="medium")
    
    if result["success"]:
        print(f"✅ Audio extraction successful!")
        print(f"   Output file: {result['output_file']}")
        print(f"   File size: {result['file_size']} bytes")
        print(f"   Quality: {result['quality']}")
        print(f"   Bitrate: {result['bitrate']}kbps")
        print(f"   Sample rate: {result['sample_rate']}Hz")
        
        # Verify output file exists
        if Path(result["output_file"]).exists():
            print("✅ Output file was created successfully")
            return True
        else:
            print("❌ Output file was not created")
            return False
    else:
        print(f"❌ Audio extraction failed: {result['error']}")
        return False

async def test_parameter_validation():
    """Test parameter validation"""
    print("\nTesting parameter validation...")
    
    # Test valid parameters
    try:
        params = ExtractAudioParams(
            input_path="test.mp4",
            output_name="test",
            audio_quality="medium"
        )
        print("✅ Valid parameters accepted")
    except Exception as e:
        print(f"❌ Valid parameters rejected: {e}")
        return False
    
    # Test invalid quality
    try:
        params = ExtractAudioParams(
            input_path="test.mp4",
            audio_quality="invalid"
        )
        print("❌ Invalid quality should have been rejected")
        return False
    except pydantic.ValidationError:
        print("✅ Invalid quality properly rejected")
    
    # Test missing required parameter
    try:
        params = ExtractAudioParams()  # Missing input_path
        print("❌ Missing required parameter should have been rejected")
        return False
    except pydantic.ValidationError:
        print("✅ Missing required parameter properly rejected")
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting video2audio MCP server tests...\n")
    
    tests = [
        ("Extractor functionality", test_extractor),
        ("Parameter validation", test_parameter_validation),
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The video2audio MCP server is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)