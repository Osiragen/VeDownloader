import sys
import os
import yt_dlp
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox,
    QProgressBar, QComboBox, QTabWidget, QListWidget, QGroupBox,
    QFormLayout, QSpinBox, QCheckBox, QStatusBar, QAction, QMenu,
    QTextBrowser, QDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap

class ProgressHook:
    """Progress hook for yt-dlp to report download progress"""
    def __init__(self, progress_signal, status_signal):
        self.progress_signal = progress_signal
        self.status_signal = status_signal

    def __call__(self, d):
        if d['status'] == 'downloading':
            # Calculate download progress
            downloaded_bytes = d.get('downloaded_bytes', 0)

            # Try to get total bytes or estimated total bytes
            if 'total_bytes' in d and d['total_bytes'] is not None and d['total_bytes'] > 0:
                percent = int((downloaded_bytes / d['total_bytes']) * 100)
                self.progress_signal.emit(percent)
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate'] is not None and d['total_bytes_estimate'] > 0:
                percent = int((downloaded_bytes / d['total_bytes_estimate']) * 100)
                self.progress_signal.emit(percent)
            else:
                # If we can't calculate percentage, just show indeterminate progress
                self.status_signal.emit(f"Downloading... ({downloaded_bytes / 1024 / 1024:.2f} MB downloaded)")
                # Send a progress update that's not 100% to show activity
                self.progress_signal.emit(min(downloaded_bytes % 100, 95))

            # Update status with download speed
            if 'speed' in d and d['speed'] is not None:
                speed = d['speed'] / 1024 / 1024  # Convert to MB/s
                self.status_signal.emit(f"Downloading: {speed:.2f} MB/s")
            else:
                self.status_signal.emit("Downloading...")

        elif d['status'] == 'finished':
            self.status_signal.emit("Download finished, now processing...")
        elif d['status'] == 'error':
            self.status_signal.emit(f"Error: {d.get('error', 'Unknown error')}")


class DownloadThread(QThread):
    """Thread for handling downloads without freezing the UI"""
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, url, output_dir, quality="best", format_option="mp4", subtitles=False):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.quality = quality
        self.format_option = format_option
        self.subtitles = subtitles
        self.is_cancelled = False

    def run(self):
        try:
            if self.is_cancelled:
                self.status_signal.emit("Download cancelled")
                self.finished_signal.emit(False, "Download cancelled by user")
                return

            self.status_signal.emit("Starting download...")

            # Map quality selection to yt-dlp format strings
            format_string = self._get_format_string()

            # Configure yt-dlp options
            ydl_opts = {
                'format': format_string,
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'progress_hooks': [ProgressHook(self.progress_signal, self.status_signal)],
                'quiet': True,
                'no_warnings': True,
                'noplaylist': True,  # Only download the video, not the playlist
            }

            # If audio only is selected, we can avoid needing FFmpeg
            if self.quality == "audio only":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessor_args': ['-ar', '44100'],
                    'prefer_ffmpeg': False,  # Try to avoid using FFmpeg if possible
                    'extractaudio': True,    # Extract audio
                    'nopostoverwrites': False,
                    'keepvideo': False,
                    # Avoid post-processing that requires FFmpeg
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                        'nopostoverwrites': False,
                        'already_have_video': True  # Skip FFmpeg if possible
                    }] if self.format_option.lower() in ['mp3', 'aac'] else []
                })

            # Add subtitle options if requested
            if self.subtitles:
                ydl_opts.update({
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['en'],
                })

            # Add format-specific options
            if self.format_option.lower() != "auto":
                if self.format_option.lower() == "mp4":
                    ydl_opts.update({
                        'merge_output_format': 'mp4',
                        'postprocessor_args': ['-movflags', 'faststart'],
                    })
                elif self.format_option.lower() in ["mkv", "webm", "mp3", "aac"]:
                    ydl_opts.update({
                        'merge_output_format': self.format_option.lower(),
                    })

            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    self.status_signal.emit("Extracting video information...")
                    info = ydl.extract_info(self.url, download=False)

                    if self.is_cancelled:
                        self.status_signal.emit("Download cancelled")
                        self.finished_signal.emit(False, "Download cancelled by user")
                        return

                    if info:
                        video_title = info.get('title', 'Video')
                        self.status_signal.emit(f"Downloading: {video_title}")

                        try:
                            # Perform the actual download
                            ydl.download([self.url])

                            if self.is_cancelled:
                                self.status_signal.emit("Download cancelled")
                                self.finished_signal.emit(False, "Download cancelled by user")
                                return

                            # Final success message
                            self.status_signal.emit("Download complete!")
                            self.finished_signal.emit(True, f"Successfully downloaded: {video_title}")
                        except yt_dlp.utils.DownloadError as e:
                            error_msg = str(e)

                            # Check for FFmpeg error and try alternative download method
                            if "ffmpeg is not installed" in error_msg:
                                self.status_signal.emit("FFmpeg not found. Trying alternative download method...")
                                success = self._try_direct_download(info, video_title)
                                if success:
                                    return

                                # If alternative method failed, show FFmpeg installation instructions
                                ffmpeg_msg = (
                                    "FFmpeg is required but not installed. Please install FFmpeg:\n\n"
                                    "1. Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/\n"
                                    "2. Extract the zip file\n"
                                    "3. Copy the ffmpeg.exe file from the bin folder\n"
                                    "4. Paste it into your Python installation folder or add it to your system PATH"
                                )
                                self.finished_signal.emit(False, ffmpeg_msg)
                            else:
                                self.status_signal.emit(f"Download error: {error_msg}")
                                self.finished_signal.emit(False, f"Download error: {error_msg}")
                    else:
                        self.status_signal.emit("Failed to get video information")
                        self.finished_signal.emit(False, "Failed to get video information")
                except yt_dlp.utils.DownloadError as e:
                    error_msg = str(e)
                    self.status_signal.emit(f"Download error: {error_msg}")

                    # Check for FFmpeg error
                    if "ffmpeg is not installed" in error_msg:
                        ffmpeg_msg = (
                            "FFmpeg is required but not installed. Please install FFmpeg:\n\n"
                            "1. Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/\n"
                            "2. Extract the zip file\n"
                            "3. Copy the ffmpeg.exe file from the bin folder\n"
                            "4. Paste it into your Python installation folder or add it to your system PATH"
                        )
                        self.finished_signal.emit(False, ffmpeg_msg)
                    else:
                        self.finished_signal.emit(False, f"Download error: {error_msg}")

        except Exception as e:
            self.status_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False, str(e))

    def _try_direct_download(self, info, video_title):
        """Try to download a single format that doesn't require merging with FFmpeg"""
        try:
            self.status_signal.emit("Trying direct download without FFmpeg...")

            # Get available formats
            formats = info.get('formats', [])
            if not formats:
                self.status_signal.emit("No suitable formats found for direct download")
                return False

            # Find a suitable format based on quality preference
            target_format = None

            # For audio only, find the best audio format
            if self.quality == "audio only":
                audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                if audio_formats:
                    target_format = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
            else:
                # For video, try to find a format with both audio and video
                complete_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') != 'none']

                if complete_formats:
                    # Filter by height if a specific quality was requested
                    if self.quality == "1080p":
                        filtered = [f for f in complete_formats if f.get('height', 0) <= 1080]
                    elif self.quality == "720p":
                        filtered = [f for f in complete_formats if f.get('height', 0) <= 720]
                    elif self.quality == "480p":
                        filtered = [f for f in complete_formats if f.get('height', 0) <= 480]
                    elif self.quality == "360p":
                        filtered = [f for f in complete_formats if f.get('height', 0) <= 360]
                    else:
                        filtered = complete_formats

                    if filtered:
                        # Get the best quality within our filter
                        target_format = max(filtered, key=lambda x: x.get('height', 0) or 0)

            if target_format:
                format_id = target_format.get('format_id')
                self.status_signal.emit(f"Found compatible format: {format_id}")

                # Configure yt-dlp for direct download
                ydl_opts = {
                    'format': format_id,
                    'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                    'progress_hooks': [ProgressHook(self.progress_signal, self.status_signal)],
                    'quiet': True,
                    'no_warnings': True,
                    'noplaylist': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.url])

                self.status_signal.emit("Download complete!")
                self.finished_signal.emit(True, f"Successfully downloaded: {video_title}")
                return True
            else:
                self.status_signal.emit("No compatible format found for direct download")
                return False

        except Exception as e:
            self.status_signal.emit(f"Direct download failed: {str(e)}")
            return False

    def _get_format_string(self):
        """Convert UI quality selection to yt-dlp format string"""
        if self.quality == "best":
            return "bestvideo+bestaudio/best"
        elif self.quality == "1080p":
            return "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        elif self.quality == "720p":
            return "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif self.quality == "480p":
            return "bestvideo[height<=480]+bestaudio/best[height<=480]"
        elif self.quality == "360p":
            return "bestvideo[height<=360]+bestaudio/best[height<=360]"
        elif self.quality == "audio only":
            return "bestaudio/best"
        else:
            return "bestvideo+bestaudio/best"


class HelpDialog(QDialog):
    """Dialog for displaying help information"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help - VeDownloader")
        self.setGeometry(150, 150, 600, 400)

        layout = QVBoxLayout(self)

        # Create text browser for help content
        self.help_browser = QTextBrowser()
        self.help_browser.setOpenExternalLinks(True)

        # Help content
        help_text = """
        <h2>VeDownloader Help/VeDownloader ความช่วยเหลือ</h2>

        <h3>Basic Usage</h3>
        
        <ol>
            <li>Enter a video URL in the URL field</li>
            <li>Select your preferred quality and format</li>
            <li>Choose an output directory or use the default</li>
            <li>Click the Download button</li>
        </ol>
        
        <h3>การใช้งานพื้นฐาน</h3>
        
        <ol>
            <li>ป้อน URL ของวิดีโอในช่อง URL</li>
            <li>เลือกคุณภาพและรูปแบบที่ต้องการ</li>
            <li>เลือกโฟลเดอร์ปลายทางหรือใช้ค่าดั้งเดิม</li>
            <li>กดปุ่ม ดาวน์โหลด</li>
        </ol>
        
        <h3>Quality Options</h3>
        
        <ul>
            <li><b>Best</b> - Highest quality available</li>
            <li><b>1080p</b> - Full HD quality</li>
            <li><b>720p</b> - HD quality</li>
            <li><b>480p</b> - Standard definition</li>
            <li><b>360p</b> - Low definition</li>
            <li><b>Audio Only</b> - Extract audio only</li>
        </ul>
        
        <h3>ตัวเลือกคุณภาพ</h3>
        
        <ul>
            <li><b>Best</b> - คุณภาพสูงสุดที่มี</li>
            <li><b>1080p</b> - ความละเอียด Full HD</li>
            <li><b>720p</b> - ความละเอียด HD</li>
            <li><b>480p</b> - ความละเอียดมาตรฐาน</li>
            <li><b>360p</b> - ความละเอียดต่ำ</li>
            <li><b>Audio Only</b> - เฉพาะไฟล์เสียง</li>
        </ul>

        <h3>Format Options</h3>
        
        <ul>
            <li><b>Auto</b> - Automatically select the best format</li>
            <li><b>MP4</b> - Standard video format compatible with most devices</li>
            <li><b>MKV</b> - High quality container format</li>
            <li><b>WebM</b> - Open web video format</li>
            <li><b>MP3</b> - Audio format (for audio only)</li>
            <li><b>AAC</b> - High quality audio format (for audio only)</li>
        </ul>
        
        <h3>ตัวเลือกรูปแบบ</h3>
        
        <ul>
            <li><b>Auto</b> - เลือกรูปแบบที่ดีที่สุดโดยอัตโนมัติ</li>
            <li><b>MP4</b> - รูปแบบวิดีโอมาตรฐานที่รองรับอุปกรณ์ส่วนใหญ่</li>
            <li><b>MKV</b> -รูปแบบคอนเทนเนอร์คุณภาพสูง</li>
            <li><b>WebM</b> - รูปแบบวิดีโอแบบเปิดสำหรับเว็บ</li>
            <li><b>MP3</b> - รูปแบบไฟล์เสียง (เฉพาะโหมดเสียง)</li>
            <li><b>AAC</b> - รูปแบบไฟล์เสียงคุณภาพสูง (เฉพาะโหมดเสียง)</li>
        </ul>

        <h3>FFmpeg Requirement</h3>
        
        <p>Some download options require FFmpeg to be installed. If you see an error about FFmpeg, follow the instructions to install it.</p>
        
        <h3>ข้อกำหนดของ FFmpeg</h3>
        
        <p>บางตัวเลือกในการดาวน์โหลดจำเป็นต้องติดตั้ง FFmpeg หากพบข้อความแจ้งเตือนเกี่ยวกับ FFmpeg โปรดทำตามคำแนะนำเพื่อติดตั้ง.</p>

        <h3>History Tab</h3>
        
        <p>The History tab shows your previous downloads. You can clear the history using the Clear History button.</p>
        
        <h3>แท็บประวัติ</h3>
        <p>แท็บ ประวัติ จะแสดงรายการดาวน์โหลดก่อนหน้า คุณสามารถลบประวัติได้โดยกดปุ่ม ล้างประวัติ.</p>

        <h3>Settings Tab</h3>
        <p>Configure default download directory and other options in the Settings tab.</p>
        
        <h3>แท็บการตั้งค่า</h3>
        <p>สามารถกำหนดค่าโฟลเดอร์ปลายทางเริ่มต้นและตัวเลือกอื่นๆ ได้ในแท็บ การตั้งค่า.</p>
        """

        self.help_browser.setHtml(help_text)
        layout.addWidget(self.help_browser)

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button)


class AboutDialog(QDialog):
    """Dialog for displaying information about the application and developers"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About VeDownloader")
        self.setGeometry(150, 150, 500, 350)

        layout = QVBoxLayout(self)

        # App title
        title_label = QLabel("VeDownloader")
        title_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)

        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        # Description
        desc_label = QLabel("A simple and powerful video downloader application")
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)

        # Separator
        line = QLabel()
        line.setFrameShape(QLabel.HLine)
        line.setFrameShadow(QLabel.Sunken)
        layout.addWidget(line)

        # Developer info
        dev_group = QGroupBox("Developer Information")
        dev_layout = QVBoxLayout()

        dev_name = QLabel("Developed by: OsiragenTM")
        dev_name.setAlignment(Qt.AlignCenter)
        dev_layout.addWidget(dev_name)

        dev_email = QLabel("Email: ___@gmail.com")
        dev_email.setAlignment(Qt.AlignCenter)
        dev_layout.addWidget(dev_email)

        dev_purpose = QLabel("Purpose: Educational Project")
        dev_purpose.setAlignment(Qt.AlignCenter)
        dev_layout.addWidget(dev_purpose)

        dev_group.setLayout(dev_layout)
        layout.addWidget(dev_group)

        # Technologies used
        tech_group = QGroupBox("Technologies Used")
        tech_layout = QVBoxLayout()

        tech_list = QLabel("""
        <ul>
            <li>Python 3</li>
            <li>PyQt5 - GUI Framework</li>
            <li>yt-dlp - Download Engine</li>
            <li>FFmpeg - Media Processing</li>
            <li>PyInstaller - Executable Creation</li>
        </ul>
        """)
        tech_layout.addWidget(tech_list)

        tech_group.setLayout(tech_layout)
        layout.addWidget(tech_group)

        # Close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VeDownloader")
        self.setGeometry(100, 100, 800, 600)

        # Create menu bar
        self.setup_menu()

        # Create central widget with tabs
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Create tab widget
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Create tabs
        self.download_tab = QWidget()
        self.history_tab = QWidget()
        self.settings_tab = QWidget()

        self.tabs.addTab(self.download_tab, "Download")
        self.tabs.addTab(self.history_tab, "History")
        self.tabs.addTab(self.settings_tab, "Settings")

        # Set up each tab
        self.setup_download_tab()
        self.setup_history_tab()
        self.setup_settings_tab()

        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

        # Initialize download history
        self.download_history = []

        # Set default output directory
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.dir_input.setText(downloads_dir)

    def setup_menu(self):
        """Set up the application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        help_action = QAction("Help Contents", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_help(self):
        """Show the help dialog"""
        help_dialog = HelpDialog(self)
        help_dialog.exec_()

    def show_about(self):
        """Show the about dialog"""
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

    def setup_download_tab(self):
        layout = QVBoxLayout(self.download_tab)

        # URL input group
        url_group = QGroupBox("Media URL")
        url_layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL to download")
        url_layout.addWidget(self.url_input)

        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        # Options group
        options_group = QGroupBox("Download Options")
        options_layout = QFormLayout()

        # Output directory
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_button = QPushButton("Browse...")
        self.dir_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_button)
        options_layout.addRow("Output Directory:", dir_layout)

        # Quality selection
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Best", "1080p", "720p", "480p", "360p", "Audio Only"])
        options_layout.addRow("Quality:", self.quality_combo)

        # Format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Auto", "MP4", "MKV", "WebM", "MP3", "AAC"])
        options_layout.addRow("Format:", self.format_combo)

        # Additional options
        self.subtitle_check = QCheckBox("Download subtitles if available")
        self.subtitle_check.setChecked(True)
        options_layout.addRow("", self.subtitle_check)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Progress group
        progress_group = QGroupBox("Download Progress")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Action buttons
        button_layout = QHBoxLayout()

        self.download_button = QPushButton("Download")
        self.download_button.setIcon(QIcon.fromTheme("download"))
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setMinimumHeight(40)
        button_layout.addWidget(self.download_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setIcon(QIcon.fromTheme("cancel"))
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False)
        self.cancel_button.setMinimumHeight(40)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def setup_history_tab(self):
        layout = QVBoxLayout(self.history_tab)

        self.history_list = QListWidget()
        layout.addWidget(self.history_list)

        button_layout = QHBoxLayout()
        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.clicked.connect(self.clear_history)
        button_layout.addWidget(self.clear_history_button)

        layout.addLayout(button_layout)

    def setup_settings_tab(self):
        layout = QVBoxLayout(self.settings_tab)

        # General settings group
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout()

        self.default_dir_input = QLineEdit()
        self.default_dir_button = QPushButton("Browse...")
        self.default_dir_button.clicked.connect(self.browse_default_directory)

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.default_dir_input)
        dir_layout.addWidget(self.default_dir_button)
        general_layout.addRow("Default Download Directory:", dir_layout)

        self.max_downloads = QSpinBox()
        self.max_downloads.setRange(1, 10)
        self.max_downloads.setValue(3)
        general_layout.addRow("Maximum Concurrent Downloads:", self.max_downloads)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # Advanced settings group
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout()

        self.auto_update_check = QCheckBox()
        self.auto_update_check.setChecked(True)
        advanced_layout.addRow("Check for Updates Automatically:", self.auto_update_check)

        self.dark_mode_check = QCheckBox()
        advanced_layout.addRow("Dark Mode:", self.dark_mode_check)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        # Save button
        self.save_settings_button = QPushButton("Save Settings")
        self.save_settings_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_settings_button)

        # Fill with default values
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.default_dir_input.setText(downloads_dir)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.dir_input.setText(directory)

    def browse_default_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Default Output Directory")
        if directory:
            self.default_dir_input.setText(directory)

    def start_download(self):
        url = self.url_input.text()
        output_dir = self.dir_input.text()
        quality = self.quality_combo.currentText().lower()
        format_option = self.format_combo.currentText().lower()
        subtitles = self.subtitle_check.isChecked()

        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL")
            return

        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create output directory: {str(e)}")
                return

        # Disable download button and enable cancel button
        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)

        # Reset progress bar
        self.progress_bar.setValue(0)

        # Create and start download thread
        self.download_thread = DownloadThread(url, output_dir, quality, format_option, subtitles)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.status_signal.connect(self.update_status)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.start()

    def cancel_download(self):
        if hasattr(self, 'download_thread') and self.download_thread.isRunning():
            # Set the cancellation flag
            self.download_thread.is_cancelled = True
            # Terminate the thread (this is not ideal but works for our demo)
            self.download_thread.terminate()
            self.update_status("Download cancelled")
            self.download_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            self.progress_bar.setValue(0)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, message):
        self.status_label.setText(message)
        self.statusBar.showMessage(message)

    def download_finished(self, success, message):
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

        if success:
            QMessageBox.information(self, "Success", message)

            # Add to history
            url = self.url_input.text()
            self.download_history.append(url)
            self.history_list.addItem(url)
        else:
            QMessageBox.critical(self, "Error", f"Download failed: {message}")

    def clear_history(self):
        self.download_history.clear()
        self.history_list.clear()

    def save_settings(self):
        # In a real application, you would save these settings to a config file
        QMessageBox.information(self, "Settings", "Settings saved successfully")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
