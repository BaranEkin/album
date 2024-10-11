import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from config.Config import Config
from gui.MainWindow import MainWindow

# Main application execution
if __name__ == "__main__":

    Config.read_config()

    # Define image file extensions you want to look for
    image_extensions = {".jpg", ".jpeg"}

    # Use pathlib to create a Path object for the folder
    thumbnails_folder = Path("res/thumbnails/1992")
    media_folder = Path("res/media/1992")

    # Recursively find all files with image extensions
    t_paths = [
        str(file)
        for file in thumbnails_folder.rglob("*")
        if file.suffix.lower() in image_extensions
    ]

    m_paths = [
        str(file)
        for file in media_folder.rglob("*")
        if file.suffix.lower() in image_extensions
    ]

    m_paths = ['res\\media\\1992\\01\\M19920115_001.jpg', 'res\\media\\1992\\01\\M19920115_002.jpg', 'res\\media\\1992\\01\\M19920115_003.jpg']

    app = QApplication(sys.argv)
    viewer = MainWindow(t_paths, m_paths)
    viewer.show()
    sys.exit(app.exec_())
