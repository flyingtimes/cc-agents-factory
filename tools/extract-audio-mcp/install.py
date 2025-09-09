#!/usr/bin/env python3
"""
Installation script for the Extract Audio MCP Server
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required Python packages."""
    print("Installing required packages...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        
        print("Successfully installed required packages!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        print("Please install manually with: pip install -r requirements.txt")
        return False

def check_ffmpeg():
    """Check if ffmpeg is installed."""
    print("Checking ffmpeg installation...")
    
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True, check=True)
        print("ffmpeg is installed and available!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: ffmpeg not found. Please install ffmpeg and add it to your PATH.")
        print("Download from: https://ffmpeg.org/download.html")
        return False

def main():
    """Run installation."""
    print("=== Extract Audio MCP Server Installation ===\n")
    
    # Install Python packages
    if not install_requirements():
        print("Installation failed!")
        return False
    
    print()
    
    # Check ffmpeg
    ffmpeg_ok = check_ffmpeg()
    
    print("\n=== Installation Summary ===")
    print("Python packages: Installed")
    print(f"ffmpeg: {'Available' if ffmpeg_ok else 'Not found'}")
    
    if ffmpeg_ok:
        print("\n[SUCCESS] Installation completed! You can now run the server with:")
        print("python server.py")
    else:
        print("\n[PARTIAL] Python packages installed, but ffmpeg is required for full functionality.")
    
    return True

if __name__ == "__main__":
    main()