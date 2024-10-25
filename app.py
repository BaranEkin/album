import sys
from PyQt5.QtWidgets import QApplication, QStyleFactory
from gui.MainWindow import MainWindow

from config.Config import Config
from MediaLoader import MediaLoader
from data.DataManager import DataManager


# Main application execution
if __name__ == "__main__":
    #"""
    Config.read_config()
    media_loader = MediaLoader()
    data_manager = DataManager()
    app = QApplication(sys.argv)
    app.setStyle("windowsvista")
    viewer = MainWindow(data_manager, media_loader)
    viewer.showMaximized()
    sys.exit(app.exec_())
    
    """
    Config.read_config()
    data_manager = DataManager()
    albums = data_manager.get_all_albums()
    app = QApplication(sys.argv)
    app.setStyle("windowsvista")
    viewer = DialogFilter(albums)
    viewer.show()
    sys.exit(app.exec_())
    
    """
