import sys
from PyQt5.QtWidgets import QApplication
from gui.main.MainWindow import MainWindow

from config.config import Config
from media_loader import MediaLoader
from data.data_manager import DataManager

# Main application execution
if __name__ == "__main__":
    # """
    Config.read_config()
    media_loader = MediaLoader()
    data_manager = DataManager()
    app = QApplication(sys.argv)
    app.setStyle("windowsvista")
    viewer = MainWindow(data_manager, media_loader)
    viewer.showMaximized()
    sys.exit(app.exec_())
