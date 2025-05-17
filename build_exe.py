import os
import sys
import subprocess

def main():
    """Build the executable for VeDownloader"""
    print("Building VeDownloader executable...")
    
    # Define the PyInstaller command
    cmd = [
        ".venv\\Scripts\\pyinstaller",
        "--name=VeDownloader",
        "--onefile",
        "--windowed",
        "--clean",
        "--add-data=.venv\\Lib\\site-packages\\yt_dlp;yt_dlp",
        "advanced_gui.py"
    ]
    
    # Run the command
    subprocess.run(cmd, check=True)
    
    print("\nBuild completed!")
    print("The executable can be found in the 'dist' folder.")

if __name__ == "__main__":
    main()
