import sys
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
from gui.MainWindow import MainWindow
from gui.DialogAddMedia import DialogAddMedia  # For testing

from config.Config import Config
from MediaLoader import MediaLoader
from data.DataManager import DataManager


def simulate_keypress(window, key):
        """Simulates a keypress event."""
        # Create a QKeyEvent for the keypress (KeyPress event)
        event = QKeyEvent(QKeyEvent.KeyPress, key, Qt.NoModifier)
        
        # Post the event directly to the QLineEdit widget
        QApplication.postEvent(window, event)
        
        # Create a QKeyEvent for the key release (KeyRelease event)
        release_event = QKeyEvent(QKeyEvent.KeyRelease, key, Qt.NoModifier)
        
        # Post the key release event
        QApplication.postEvent(window, release_event)

# Main application execution
if __name__ == "__main__":
    """
    Config.read_config()
    data_manager = DataManager()
    app = QApplication(sys.argv)
    app.setStyle("windowsvista")
    viewer = DialogAddMedia(data_manager)
    viewer.show()
    sys.exit(app.exec_())
    
    """
    Config.read_config()
    media_loader = MediaLoader()
    data_manager = DataManager()
    app = QApplication(sys.argv)
    app.setStyle("windowsvista")
    viewer = MainWindow(data_manager, media_loader)
    viewer.showMaximized()
    simulate_keypress(viewer.thumbnail_list, Qt.Key_Left)
    simulate_keypress(viewer.thumbnail_list, Qt.Key_Right)
    simulate_keypress(viewer.thumbnail_list, Qt.Key_Left)
    sys.exit(app.exec_())
    
    
    
