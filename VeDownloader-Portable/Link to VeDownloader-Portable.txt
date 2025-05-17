#!/bin/bash

# VeDownloader Portable Launcher
# This script launches the portable version of VeDownloader

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Set up environment variables
export PATH="$SCRIPT_DIR/bin:$PATH"
export PYTHONPATH="$SCRIPT_DIR/app:$PYTHONPATH"

# Activate virtual environment
source "$SCRIPT_DIR/python/bin/activate"

# Set Qt environment variables
export QT_QPA_PLATFORM=xcb
export QT_AUTO_SCREEN_SCALE_FACTOR=1

# Check if FFmpeg is in the bin directory
if [ -f "$SCRIPT_DIR/bin/ffmpeg" ]; then
    echo "Using bundled FFmpeg"
else
    echo "Warning: FFmpeg not found in portable package."
    echo "Some download features may not work properly."
    echo "If you have FFmpeg installed on your system, it will be used instead."
fi

# Run the application
echo "Starting VeDownloader Portable..."
python "$SCRIPT_DIR/app/advanced_gui.py"

# Deactivate virtual environment when done
deactivate

echo "VeDownloader closed."
