from PyQt5.QtWidgets import (QFrame, QLabel, QTextBrowser, QPushButton,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt


class FrameInfo(QFrame):
    def __init__(self):
        super().__init__()

        # Set the fixed height for the frame
        self.setFixedHeight(100)

        # Create layout for the frame
        main_layout = QVBoxLayout()

        # Set a fixed width for the labels to ensure both labels have the same width
        label_width = 80

        # Create the first row for title
        title_layout = QHBoxLayout()
        title_label = QLabel("BAŞLIK")
        title_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Align text to the right
        title_label.setFixedWidth(label_width)  # Set a fixed width for the label
        title_label.setStyleSheet("font-family: MS Reference Sans Serif; font-size: 16px;")  # Set label font style

        self.title_browser = QTextBrowser()
        self.title_browser.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align text to the left
        self.title_browser.setFixedHeight(40)  # Set height for consistency
        self.title_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.title_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.title_browser.setStyleSheet("font-family: Arial; font-size: 20px; color: darkblue;")  # Title style

        # Mock-up value for title
        self.title_browser.setHtml('<div style="line-height:27px;">BAŞLIK DENEME YAZISI BAŞLIK DENEME YAZISI</div>')

        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_browser)

        # Create the second row for location and date
        location_date_layout = QHBoxLayout()

        # Location label and browser
        location_label = QLabel("YER")
        location_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Align text to the right
        location_label.setFixedWidth(label_width)  # Set the same fixed width for label
        location_label.setStyleSheet("font-family: MS Reference Sans Serif; font-size: 16px;")  # Set label font style

        self.location_browser = QTextBrowser()
        self.location_browser.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align text to the left
        self.location_browser.setFixedHeight(40)  # Set height for consistency
        self.location_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.location_browser.setStyleSheet("font-family: Arial; font-size: 18px; color: darkred;")  # Location style
        self.location_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.location_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Mock-up value for location
        self.location_browser.setHtml('<div style="line-height:26px;">DENEME ŞEHRİ DENEME SEMTİ DENEME KÖYÜ DENEMELER</div>')

        location_date_layout.addWidget(location_label)
        location_date_layout.addWidget(self.location_browser)

        # Date label and browser
        date_label = QLabel("TARİH")
        date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Align text to the right
        date_label.setFixedWidth(label_width)  # Set the same fixed width for label
        date_label.setStyleSheet("font-family: MS Reference Sans Serif; font-size: 16px;")  # Set label font style

        self.date_browser = QTextBrowser()
        self.date_browser.setAlignment(Qt.AlignHCenter)  # Align text to the left
        self.date_browser.setFixedHeight(40)  # Set height for consistency
        self.date_browser.setFixedWidth(250)  # Set the fixed width for the date
        self.date_browser.setStyleSheet("font-family: Arial; font-size: 18px; color: darkgreen;")  # Date style
        self.date_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.date_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Mock-up value for date
        self.date_browser.setHtml('<div style="line-height:26px;">09 Ağustos 9999 Cumartesi</div>')

        location_date_layout.addWidget(date_label)
        location_date_layout.addWidget(self.date_browser)

        # Add both rows to the main layout
        main_layout.addLayout(title_layout)
        main_layout.addLayout(location_date_layout)

        # Set the main layout to the frame
        self.setLayout(main_layout)
