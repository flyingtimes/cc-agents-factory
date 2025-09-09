#!/usr/bin/env python3
"""
Setup script for integrating the Extract Audio MCP tool with Claude Code
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def install_mcp_dependencies():
    """Install MCP dependencies."""
    print("Installing MCP dependencies...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "mcp"
        ], capture_output=True, text=True, check=True)
        
        print("[OK] MCP package installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error installing MCP: {e}")
        return False

def test_mcp_server():
    """Test if the MCP server starts correctly."""
    print("Testing MCP server...")
    
    server_path = Path("server.py")
    if not server_path.exists():
        print(f"[ERROR] Server file not found: {server_path}")
        return False
    
    try:
        # Test server import
        result = subprocess.run([
            sys.executable, "-c", 
            "import sys; sys.path.append('tools/extract-audio-mcp'); import server; print('Server imports successfully')"
        ], capture_output=True, text=True, check=True)
        
        print("[OK] MCP server test passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] MCP server test failed: {e}")
        return False

def check_configuration():
    """Check Claude Code configuration."""
    print("Checking Claude Code configuration...")
    
    config_path = Path("../../.claude/settings.local.json")
    if not config_path.exists():
        print("[ERROR] Claude Code configuration not found")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'mcpServers' in config and 'extract-audio' in config['mcpServers']:
            print("[OK] MCP server configuration found in Claude Code settings")
            return True
        else:
            print("[ERROR] MCP server configuration not found in Claude Code settings")
            return False
    except Exception as e:
        print(f"[ERROR] Error reading configuration: {e}")
        return False

def print_usage_instructions():
    """Print usage instructions."""
    print("\n" + "="*60)
    print("EXTRACT AUDIO MCP TOOL - USAGE INSTRUCTIONS")
    print("="*60)
    print()
    print("SETUP COMPLETED!")
    print()
    print("TO USE THE AUDIO EXTRACTION TOOL:")
    print("1. Restart Claude Code to load the MCP server")
    print("2. The tool will be available as 'extract_audio'")
    print()
    print("TOOL PARAMETERS:")
    print("- input_path (required): Path to video file or URL")
    print("- output_name (optional): Custom output filename")
    print("- output_dir (optional): Output directory (default: ../outputs)")
    print("- audio_quality (optional): low/medium/high (default: medium)")
    print()
    print("EXAMPLE USAGE:")
    print("Extract audio from local file:")
    print('  {"input_path": "assets/1.mp4", "audio_quality": "high"}')
    print()
    print("Extract audio from URL:")
    print('  {"input_path": "https://example.com/video.mp4", "output_name": "web_audio"}')
    print()
    print("OUTPUT:")
    print("- Files saved to: ../outputs/")
    print("- Format: {name}_{uuid}.mp3")
    print("- Quality: 128k/192k/320kbps MP3")
    print()
    print("REQUIREMENTS:")
    print("- ffmpeg must be installed and in PATH")
    print("- Python MCP package installed")
    print()

def main():
    """Main setup function."""
    print("Extract Audio MCP Tool - Claude Code Integration Setup")
    print("="*60)
    
    success = True
    
    # Step 1: Install dependencies
    if not install_mcp_dependencies():
        success = False
    
    # Step 2: Test server
    if not test_mcp_server():
        success = False
    
    # Step 3: Check configuration
    if not check_configuration():
        success = False
    
    print()
    print("="*60)
    if success:
        print("[SUCCESS] SETUP SUCCESSFUL!")
        print_usage_instructions()
    else:
        print("[ERROR] SETUP INCOMPLETE!")
        print("Please check the errors above and try again.")
        print("You may need to manually install: pip install mcp")
    
    return success

if __name__ == "__main__":
    main()