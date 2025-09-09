@echo off
setlocal enabledelayedexpansion

:: Audio Extraction Script using FFmpeg
:: Supports both local files and URLs

echo Audio Extraction Tool
echo =====================

:: Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: FFmpeg is not installed or not in PATH
    echo Please install FFmpeg and add it to your PATH
    pause
    exit /b 1
)

:: Check if input parameter is provided
if "%~1"=="" (
    echo Usage: %~nx0 "input_file_or_url" [output_name]
    echo.
    echo Examples:
    echo   %~nx0 "C:\path\to\video.mp4"
    echo   %~nx0 "C:\path\to\video.mp4" "my_audio"
    echo   %~nx0 "https://example.com/video.mp4"
    echo   %~nx0 "https://example.com/video.mp4" "online_audio"
    pause
    exit /b 1
)

set "input=%~1"
set "output_name=%~2"

:: Generate UUID for unique filename
for /f "tokens=2 delims==" %%G in ('wmic os get localdatetime /value') do set "datetime=%%G"
set "uuid=%datetime:~0,8%-%datetime:~8,4%-%datetime:~12,4%-%datetime:~16,4%-%datetime:~20,12%"

:: Generate output filename if not provided
if "%output_name%"=="" (
    :: Extract filename from path or URL
    for %%F in ("%input%") do set "filename=%%~nF"
    set "output_name=!filename!_!uuid!"
) else (
    set "output_name=!output_name!_!uuid!"
)

:: Clean output name (remove invalid characters)
set "output_name=!output_name:/=_!"
set "output_name=!output_name:\=_!"
set "output_name=!output_name::=_!"
set "output_name=!output_name:*=_!"
set "output_name=!output_name:?=_!"
set "output_name=!output_name:"=_!"
set "output_name=!output_name:<=_!"
set "output_name=!output_name:>=_!"
set "output_name=!output_name:|=_!"

set "output_file=..\outputs\!output_name!.mp3"

:: Create outputs directory if it doesn't exist
if not exist "..\outputs" (
    mkdir "..\outputs"
)

echo.
echo Input: %input%
echo Output: !output_file!
echo.

:: Check if input is a URL
echo %input% | findstr /r "https*://" >nul
if %errorlevel% equ 0 (
    echo Downloading and processing URL...
    echo This may take some time depending on file size and internet speed.
    
    :: Download and extract audio in one step
    ffmpeg -i "%input%" -vn -acodec libmp3lame -ab 192k -ar 44100 -y "!output_file!"
    
    if %errorlevel% equ 0 (
        echo.
        echo Success! Audio extracted and saved to: !output_file!
    ) else (
        echo.
        echo Error: Failed to download or extract audio from URL
        echo Possible causes:
        echo   - URL is not accessible
        echo   - Network connection issues
        echo   - Video format not supported
        pause
        exit /b 1
    )
) else (
    :: Check if local file exists
    if not exist "%input%" (
        echo Error: File not found: %input%
        pause
        exit /b 1
    )
    
    echo Processing local file...
    
    :: Extract audio from local file
    ffmpeg -i "%input%" -vn -acodec libmp3lame -ab 192k -ar 44100 -y "!output_file!"
    
    if %errorlevel% equ 0 (
        echo.
        echo Success! Audio extracted and saved to: !output_file!
    ) else (
        echo.
        echo Error: Failed to extract audio from file
        echo Possible causes:
        echo   - File is corrupted
        echo   - Video format not supported
        echo   - No audio stream in the file
        pause
        exit /b 1
    )
)

:: Display file information
if exist "!output_file!" (
    echo.
    echo File Information:
    for %%F in ("!output_file!") do (
        echo   Size: %%~zF bytes
        echo   Location: %%F
    )
)

echo.
echo Extraction complete!
pause