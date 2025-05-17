import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VeDownloader")
        self.setGeometry(100, 100, 600, 400)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # URL input
        url_label = QLabel("Enter URL:")
        self.url_input = QLineEdit()
        
        # Output directory selection
        dir_label = QLabel("Output Directory:")
        self.dir_input = QLineEdit()
        self.dir_button = QPushButton("Browse...")
        self.dir_button.clicked.connect(self.browse_directory)
        
        # Download button
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout
        layout.addWidget(url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(dir_label)
        layout.addWidget(self.dir_input)
        layout.addWidget(self.dir_button)
        layout.addWidget(self.download_button)
        layout.addWidget(self.status_label)
        
        # Set default output directory
        self.dir_input.setText("./downloads")
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.dir_input.setText(directory)
    
    def download(self):
        url = self.url_input.text()
        output_dir = self.dir_input.text()
        
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL")
            return
        
        # Here you would implement the actual download functionality
        self.status_label.setText(f"Downloading from {url} to {output_dir}...")
        
        # For demonstration purposes, just show a success message
        QMessageBox.information(self, "Success", "Download functionality would be implemented here")
        self.status_label.setText("Ready")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
