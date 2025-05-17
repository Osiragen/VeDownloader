#!/bin/bash

# VeDownloader Linux Launcher
# This script launches the VeDownloader application on Linux systems

# Set script to exit on error
set -e

# Display banner
echo "========================================"
echo "       VeDownloader Launcher           "
echo "========================================"
echo "Developed by: OsiragenTM"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 using your distribution's package manager."
    echo "For example: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.6"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python version $PYTHON_VERSION is installed, but VeDownloader requires Python $REQUIRED_VERSION or higher."
    exit 1
fi

# Set up virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv .venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install required packages if needed
echo "Checking dependencies..."
if ! pip show PyQt5 &> /dev/null || ! pip show yt-dlp &> /dev/null; then
    echo "Installing required packages..."
    pip install PyQt5 yt-dlp
    echo "Dependencies installed."
else
    echo "Dependencies already installed."
fi

# Check if running on Xubuntu
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$ID" == "ubuntu" && "$DESKTOP_SESSION" == "xubuntu" ]]; then
        echo "Running on Xubuntu..."
        # Additional Xubuntu-specific setup
        if ! dpkg -l | grep -q libxcb-xinerama0; then
            echo "Warning: libxcb-xinerama0 is not installed."
            echo "This package is required for PyQt5 to work properly on Xubuntu."
            echo "To install it, run: sudo apt install libxcb-xinerama0"
            echo ""
        fi
    fi
fi

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: FFmpeg is not installed."
    echo "Some download features may not work properly."
    echo "To install FFmpeg, run: sudo apt install ffmpeg"
    echo ""
    echo "Continuing without FFmpeg..."
fi

# Fix for potential QT platform plugin issues on some Linux distributions
export QT_QPA_PLATFORM=xcb

# Additional environment variables for Xubuntu
if [[ "$ID" == "ubuntu" && "$DESKTOP_SESSION" == "xubuntu" ]]; then
    # Fix for "Could not find the Qt platform plugin" error
    export QT_DEBUG_PLUGINS=1

    # Fix for high DPI displays
    export QT_AUTO_SCREEN_SCALE_FACTOR=1

    # Fix for font rendering issues
    export QT_FONT_DPI=96
fi

# Run the application
echo "Starting VeDownloader..."
python3 advanced_gui.py

# Deactivate virtual environment when done
deactivate

echo "VeDownloader closed."
