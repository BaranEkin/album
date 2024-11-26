from PyQt5.QtWidgets import QDialog, QTextBrowser, QVBoxLayout


class DialogNotes(QDialog):
    def __init__(self, notes: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Notlar")

        self.setFixedSize(500, 250)

        self.notes = notes
        layout = QVBoxLayout()

        # Create a QTextBrowser for displaying text
        text_browser = QTextBrowser()

        # Set custom font and color
        text_browser.setStyleSheet("font-family: Arial; font-size: 18px; color: black;")

        text_browser.setText(self.notes.replace("\\n", "\n"))

        # Add the text browser to the layout
        layout.addWidget(text_browser)
        self.setLayout(layout)
        self.show_at_bottom_right()

    def show_at_bottom_right(self):
        if self.parent():
            parent_geometry = self.parent().geometry()
            parent_x = parent_geometry.x()
            parent_y = parent_geometry.y()
            parent_width = parent_geometry.width()
            parent_height = parent_geometry.height()

            # Calculate bottom-right position with the desired clearance
            x = parent_x + parent_width - self.width() - 100  # 100-pixel clearance in the x-direction
            y = parent_y + parent_height - self.height() - 200  # 200-pixel clearance in the y-direction

            # Move the dialog to the calculated position
            self.move(x, y)
