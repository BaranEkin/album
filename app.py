import sys
from multiprocessing import freeze_support
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLibraryInfo
from data.media_list_manager import MediaListManager
from gui.main.MainWindow import MainWindow

from config.config import Config
from media_loader import MediaLoader
from data.data_manager import DataManager
from logger import close_log


# Main application execution
if __name__ == "__main__":
    freeze_support()
    Config.read_config()

    media_loader = MediaLoader()
    data_manager = DataManager()
    media_list_manager = MediaListManager()

    app = QApplication(sys.argv)
    app.setStyle("windowsvista")

    # Load Turkish translations
    translator = QTranslator()
    translator.load("qtbase_tr", QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)
    app.aboutToQuit.connect(close_log)

    viewer = MainWindow(data_manager, media_list_manager, media_loader)
    viewer.showMaximized()
    sys.exit(app.exec_())
