import sys
from multiprocessing import freeze_support
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLibraryInfo
from data.display_history_manager import DisplayHistoryManager
from data.media_list_manager import MediaListManager
from gui.main.MainWindow import MainWindow

from config.config import Config
from media_loader import MediaLoader
from data.data_manager import DataManager
from logger import close_log, log
from gui.ThemeManager import ThemeManager
from gui.constants import Constants


# Main application execution
if __name__ == "__main__":
    freeze_support()
    Config.read_config()

    media_loader = MediaLoader()
    data_manager = DataManager()
    media_list_manager = MediaListManager()
    display_history_manager = DisplayHistoryManager(data_manager)

    # Apply theme based on settings
    current_theme = Config.THEME
    log("app", f"Applying theme: {current_theme}", level="info")

    # Use the windows:darkmode=1 platform option for proper dark mode window decorations
    if Config.THEME == Constants.SETTINGS_THEME_DARK:
        app = QApplication(sys.argv + ['-platform', 'windows:darkmode=1'])
        app.setStyle("Fusion")

    elif Config.THEME == Constants.SETTINGS_THEME_CLASSIC:
        app = QApplication(sys.argv)
        app.setStyle("Windows")
    else:
        app = QApplication(sys.argv)
        app.setStyle("windowsvista")

    ThemeManager.apply_theme(app, current_theme)
    
    # Apply the stylesheet
    app.setStyleSheet(ThemeManager.get_stylesheet(current_theme))

    # Load Turkish translations
    translator = QTranslator()
    translator.load("qtbase_tr", QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)
    app.aboutToQuit.connect(close_log)

    viewer = MainWindow(data_manager, media_list_manager, media_loader, display_history_manager)
    viewer.showMaximized()
    sys.exit(app.exec_())
