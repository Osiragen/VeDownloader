# VeDownloader

A simple GUI application for downloading videos using PyQt5.

## Features

- Simple and intuitive user interface
- Download videos from various sources
- Select output directory
- Choose video quality and format
- Download history tracking
- Progress monitoring

## Installation

### Windows

1. Make sure you have Python installed (3.6 or higher)
2. Create a virtual environment:
   ```
   python -m venv .venv
   ```
3. Activate the virtual environment:
   ```
   .venv\Scripts\activate
   ```
4. Install the required packages:
   ```
   pip install PyQt5 yt-dlp
   ```

### Linux/Ubuntu

#### Option 1: Using the installer script

1. Make the installer script executable:
   ```
   chmod +x install_linux.sh
   ```
2. Run the installer with sudo:
   ```
   sudo ./install_linux.sh
   ```
3. Launch the application from your applications menu or by running:
   ```
   vedownloader
   ```

#### Option 2: Manual installation

1. Make the launcher script executable:
   ```
   chmod +x vedownloader.sh
   ```
2. Run the launcher script:
   ```
   ./vedownloader.sh
   ```

## Usage

### Basic Version

Run the basic version with:
```
python main.py
```

### Advanced Version

Run the advanced version with:
```
python advanced_gui.py
```

### Linux Version

Run the Linux version with:
```
./vedownloader.sh
```

## Application Structure

- `main.py` - Basic GUI application
- `advanced_gui.py` - Advanced GUI with more features
- `vedownloader.sh` - Linux launcher script
- `install_linux.sh` - Linux installation script
- `VeDownloader.desktop` - Linux desktop entry file

## Requirements

- Python 3.6 or higher
- PyQt5
- yt-dlp
- FFmpeg (recommended for full functionality)

## License

MIT
