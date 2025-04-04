from PyQt5.QtWidgets import QDialog, QTextBrowser, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, QPoint
import platform


class DialogNotes(QDialog):
    def __init__(self, notes: str, parent=None):
        # For Wayland compatibility, set the right window flags from the beginning
        if platform.system() == "Linux":
            # Use Popup type which has better positioning behavior on Wayland
            super().__init__(parent, Qt.Popup)
        else:
            super().__init__(parent)

        self.setWindowTitle("Notlar")
        self.setFixedSize(500, 250)

        self.notes = notes
        layout = QVBoxLayout()

        # Create a QTextBrowser for displaying text
        text_browser = QTextBrowser()
        text_browser.setObjectName("notesBrowser")  # Set object name for styling

        # Set custom font - color will be handled by theme
        text_browser.setStyleSheet("font-family: Arial; font-size: 18px;")

        text_browser.setText(self.notes.replace("\\n", "\n"))

        # Add the text browser to the layout
        layout.addWidget(text_browser)
        self.setLayout(layout)

        # Position first, then show
        self.calculate_position()
        self.show()

    def calculate_position(self):
        """Calculate and set the position of the dialog at the bottom right of the parent or screen."""
        # Get screen geometry
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # If we have a parent, position relative to it
        if self.parent() and self.parent().isVisible():
            # For Wayland, we need to use global position
            parent_global_pos = self.parent().mapToGlobal(QPoint(0, 0))
            parent_width = self.parent().width()
            parent_height = self.parent().height()

            # Calculate position - bottom right with clearance
            pos_x = parent_global_pos.x() + parent_width - self.width() - 100
            pos_y = parent_global_pos.y() + parent_height - self.height() - 200
        else:
            # No parent, position at bottom right of screen
            pos_x = screen_geometry.right() - self.width() - 100
            pos_y = screen_geometry.bottom() - self.height() - 100

        # Make sure we're on screen
        pos_x = max(
            screen_geometry.left(), min(pos_x, screen_geometry.right() - self.width())
        )
        pos_y = max(
            screen_geometry.top(), min(pos_y, screen_geometry.bottom() - self.height())
        )

        # Move the dialog to the calculated position
        self.move(pos_x, pos_y)
