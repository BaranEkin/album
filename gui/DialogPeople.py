from PyQt5.QtWidgets import QApplication, QDialog, QTextBrowser, QVBoxLayout
from PyQt5.QtGui import QFont

class DialogPeople(QDialog):
    def __init__(self, people_str: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kişiler")

        self.setFixedSize(250, 250)

        self.people_text = people_str.replace(",", "\n")
        layout = QVBoxLayout()
        
        # Create a QTextBrowser for displaying text
        text_browser = QTextBrowser()
        
        # Set custom font and color
        text_browser.setStyleSheet("font-family: Arial; font-size: 18px; color: darkgreen;")
        
        text_browser.setText(self.people_text)
        
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
        