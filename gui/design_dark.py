import sys
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QTextBrowser,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSizePolicy,
)
from PyQt5.QtCore import Qt


class InfoFrame(QFrame):
    def __init__(self):
        super().__init__()

        # Set the fixed height for the frame
        self.setFixedHeight(100)

        # Set background color for the info frame (dark mode)
        self.setStyleSheet("background-color: #2b2b2b;")

        # Create layout for the frame
        main_layout = QVBoxLayout()

        # Set a fixed width for the labels to ensure both labels have the same width
        label_width = 80

        # Create the first row for title
        title_layout = QHBoxLayout()
        title_label = QLabel("Title:")
        title_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )  # Align text to the right
        title_label.setFixedWidth(label_width)  # Set a fixed width for the label
        title_label.setStyleSheet(
            "font-family: Arial; font-size: 14px; color: #dcdcdc;"
        )  # Light gray label text

        self.title_browser = QTextBrowser()
        self.title_browser.setAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )  # Align text to the left
        self.title_browser.setFixedHeight(30)  # Set height for consistency
        self.title_browser.setStyleSheet("""
            font-family: Calibri;
            font-size: 16px;
            color: #4a90e2;  /* Soft blue for title text */
            background-color: #3a3a3a;  /* Darker background for text browser */
            border: none;
        """)  # Title style for dark mode

        # Mock-up value for title
        self.title_browser.setText("Project X Overview")

        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_browser)

        # Create the second row for location and date
        location_date_layout = QHBoxLayout()

        # Location label and browser
        location_label = QLabel("Location:")
        location_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )  # Align text to the right
        location_label.setFixedWidth(label_width)  # Set the same fixed width for label
        location_label.setStyleSheet(
            "font-family: Arial; font-size: 14px; color: #dcdcdc;"
        )  # Light gray label text

        self.location_browser = QTextBrowser()
        self.location_browser.setAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )  # Align text to the left
        self.location_browser.setFixedHeight(30)  # Set height for consistency
        self.location_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.location_browser.setStyleSheet("""
            font-family: Georgia;
            font-size: 12px;
            color: #e57373;  /* Muted red for location text */
            background-color: #3a3a3a;  /* Darker background for text browser */
            border: none;
        """)  # Location style for dark mode

        # Mock-up value for location
        self.location_browser.setText("New York, USA")

        location_date_layout.addWidget(location_label)
        location_date_layout.addWidget(self.location_browser)

        # Date label and browser
        date_label = QLabel("Date:")
        date_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )  # Align text to the right
        date_label.setFixedWidth(label_width)  # Set the same fixed width for label
        date_label.setStyleSheet(
            "font-family: Arial; font-size: 14px; color: #dcdcdc;"
        )  # Light gray label text

        self.date_browser = QTextBrowser()
        self.date_browser.setAlignment(
            Qt.AlignLeft | Qt.AlignVCenter
        )  # Align text to the left
        self.date_browser.setFixedHeight(30)  # Set height for consistency
        self.date_browser.setFixedWidth(150)  # You can change the width as needed
        self.date_browser.setStyleSheet("""
            font-family: Verdana;
            font-size: 10px;
            color: #81c784;  /* Muted green for date text */
            background-color: #3a3a3a;  /* Darker background for text browser */
            border: none;
        """)  # Date style for dark mode

        # Mock-up value for date
        self.date_browser.setText("12-Oct-2024")

        location_date_layout.addWidget(date_label)
        location_date_layout.addWidget(self.date_browser)

        # Add both rows to the main layout
        main_layout.addLayout(title_layout)
        main_layout.addLayout(location_date_layout)

        # Set the main layout to the frame
        self.setLayout(main_layout)


class ParentFrame(QFrame):
    def __init__(self):
        super().__init__()

        # Create a horizontal layout for the parent frame
        parent_layout = QHBoxLayout()

        # Create left QFrame with a fixed width (also dark mode)
        left_frame = QFrame()
        left_frame.setFixedWidth(100)
        left_frame.setFixedHeight(
            100
        )  # Set same height as the middle frame for consistency
        left_frame.setStyleSheet(
            "background-color: #3a3a3a;"
        )  # Darker gray for side frame

        # Create right QFrame with a fixed width (also dark mode)
        right_frame = QFrame()
        right_frame.setFixedWidth(100)
        right_frame.setFixedHeight(
            100
        )  # Set same height as the middle frame for consistency
        right_frame.setStyleSheet(
            "background-color: #3a3a3a;"
        )  # Darker gray for side frame

        # Create the middle QFrame (InfoFrame)
        middle_frame = InfoFrame()

        # Add all three frames to the parent layout
        parent_layout.addWidget(left_frame)
        parent_layout.addWidget(middle_frame)  # This will stretch to fill the space
        parent_layout.addWidget(right_frame)

        # Set the parent layout to this frame
        self.setLayout(parent_layout)


# Main app window to hold the Parent QFrame
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        # Create instance of ParentFrame
        parent_frame = ParentFrame()

        # Add ParentFrame to the main window layout
        layout.addWidget(parent_frame)

        # Set the main window layout
        self.setLayout(layout)


# Global dark mode stylesheet for the entire application
def set_dark_mode(app):
    app.setStyleSheet("""
        QWidget {
            background-color: #2b2b2b;
            color: #dcdcdc;
        }
        QTextBrowser {
            border: 1px solid #444444;
        }
        QPushButton {
            background-color: #3a3a3a;
            color: #dcdcdc;
            border: 1px solid #444444;
        }
        QPushButton:hover {
            background-color: #444444;
        }
    """)


if __name__ == "__main__":
    app = QApplication(sys.argv + ["-platform", "windows:darkmode=1"])

    # Apply global dark mode styling
    set_dark_mode(app)

    window = MainWindow()
    window.show()
    app.setStyle("Fusion")
    app.exec_()
