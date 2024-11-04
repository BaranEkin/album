from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from typing import Literal

def show_message(message: str, level: Literal["info", "warning", "error"] = "info"):
    """
    Display a modal message box with the specified message and level.

    Args:
        message (str): The message to display in the message box.
        level (Literal["info", "warning", "error"], optional): The type of message box to display.
            Accepted values are "info" for an information message, 
            "warning" for a warning message, and "error" for an error message.
            Defaults to "info".
    """

    # Create a message box
    msg_box = QMessageBox()
    msg_box.setText(message)
    
    # Make the message box modal
    msg_box.setWindowModality(Qt.ApplicationModal)  

    # Set the icon and title based on the level
    if level == "info":
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Bilgi")
    elif level == "warning":
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Uyarı")
    elif level == "error":
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Hata")

    # Show the message box and wait for it to close
    msg_box.exec_()
