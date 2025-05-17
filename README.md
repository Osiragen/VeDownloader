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

### Installing FFmpeg (Recommended)

FFmpeg is required for full functionality, such as merging video and audio streams. To install FFmpeg:

#### Windows
1. Download FFmpeg from [FFmpeg official site](https://ffmpeg.org/download.html).
2. Extract the zip file.
3. Add the `bin` folder to your system PATH.

#### Linux/Ubuntu
1. Install FFmpeg using your package manager:
   ```
   sudo apt update
   sudo apt install ffmpeg
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

### Example Usage

1. Open the application.
2. Paste the video URL into the input field.
3. Select the desired quality and format.
4. Click the "Download" button.

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

## Troubleshooting

### Common Issues

1. **PyQt5 or yt-dlp not found**:
   - Ensure you have installed the required packages using `pip install PyQt5 yt-dlp`.

2. **FFmpeg not installed**:
   - Follow the installation instructions above.

3. **Permission denied on Linux**:
   - Ensure the script is executable using `chmod +x`.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and push to your fork.
4. Submit a pull request.

## License

MIT

## Additional Resources

- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/software/pyqt/intro)
