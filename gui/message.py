from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from typing import Literal


def show_message(
    message: str,
    level: Literal["info", "warning", "error"] = "info",
    is_question: bool = False,
) -> bool:
    """
    Display a modal message box with the specified message and level.
    If is_question is True, display a confirmation dialog with Yes/No buttons.

    Args:
        message (str): The message to display in the message box.
        level (Literal["info", "warning", "error"], optional): The type of message box to display.
            Accepted values are "info" for an information message,
            "warning" for a warning message, and "error" for an error message.
            Defaults to "info".
        is_question (bool, optional): If True, show a confirmation dialog with Yes/No buttons.
            Defaults to False.

    Returns:
        bool: True if the user confirms (Yes), False otherwise.
    """

    # Create a message box
    msg_box = QMessageBox()
    msg_box.setText(message)

    # Make the message box modal
    msg_box.setWindowModality(Qt.ApplicationModal)

    msg_box.setWindowIcon(
        QIcon("res/icons/Chat-Bubble-Square-Warning--Streamline-Core.png")
    )

    if is_question:
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("İşlem Onaylama")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)

        response = msg_box.exec_()
        return response == QMessageBox.Yes
    else:
        # Set the icon and title based on the level
        if level == "info":
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Bilgi Mesajı")
        elif level == "warning":
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("Uyarı Mesajı")
        elif level == "error":
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Hata Mesajı")

        # Show the message box and wait for it to close
        msg_box.exec_()
        return False  # No confirmation is needed for info/warning/error
