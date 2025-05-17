#!/bin/bash

# VeDownloader Linux Installer
# This script installs VeDownloader on Linux systems

# Set script to exit on error
set -e

# Display banner
echo "========================================"
echo "       VeDownloader Installer          "
echo "========================================"
echo "Developed by: OsiragenTM"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this installer with sudo:"
    echo "sudo $0"
    exit 1
fi

# Get the real user who ran sudo
REAL_USER=$(logname || echo $SUDO_USER)
if [ -z "$REAL_USER" ]; then
    echo "Could not determine the real user. Please run with sudo."
    exit 1
fi
REAL_HOME=$(eval echo ~$REAL_USER)

# Install required system dependencies
echo "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    apt-get update
    apt-get install -y python3 python3-pip python3-venv ffmpeg
elif command -v dnf &> /dev/null; then
    # Fedora
    dnf install -y python3 python3-pip python3-virtualenv ffmpeg
elif command -v pacman &> /dev/null; then
    # Arch Linux
    pacman -Sy --noconfirm python python-pip python-virtualenv ffmpeg
else
    echo "Unsupported distribution. Please install Python 3, pip, venv, and ffmpeg manually."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install PyQt5 yt-dlp

# Create installation directory
INSTALL_DIR="/opt/vedownloader"
echo "Creating installation directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

# Copy application files
echo "Copying application files..."
cp -r ./* "$INSTALL_DIR/"

# Set permissions
echo "Setting permissions..."
chown -R "$REAL_USER:$(id -gn $REAL_USER)" "$INSTALL_DIR"
chmod +x "$INSTALL_DIR/vedownloader.sh"

# Create symlink for easy access
echo "Creating symlink to /usr/local/bin/vedownloader..."
ln -sf "$REAL_HOME/VeDownloader/vedownloader.sh" /usr/local/bin/vedownloader

# Create desktop entry
echo "Creating desktop entry..."
DESKTOP_FILE="/usr/share/applications/vedownloader.desktop"
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=VeDownloader
Exec=/usr/local/bin/vedownloader
Icon=$REAL_HOME/VeDownloader/icon.png
Type=Application
Categories=Utility;
EOF

# Update desktop database
echo "Updating desktop database..."
update-desktop-database /usr/share/applications || true

echo ""
echo "========================================"
echo "Installation completed successfully!"
echo "========================================"
echo ""
echo "You can now launch VeDownloader from your applications menu"
echo "or by running 'vedownloader' in a terminal."
echo ""
