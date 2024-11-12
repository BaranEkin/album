from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFrame, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy)

from data.orm import Media
from gui.main.TextBrowserDate import TextBrowserDate


class FrameInfo(QFrame):
    def __init__(self):
        super().__init__()

        # Set the fixed height for the frame
        self.setFixedHeight(100)

        # Create layout for the frame
        self.main_layout = QVBoxLayout()

        # Set a fixed width for the labels to ensure both labels have the same width
        label_width = 120

        # Create the first row for title
        self.topic_title_layout = QHBoxLayout()
        self.topic_title_label = QLabel("KONU/BAŞLIK")
        self.topic_title_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Align text to the right
        self.topic_title_label.setFixedWidth(label_width)  # Set a fixed width for the label
        self.topic_title_label.setStyleSheet("font-family: MS Reference Sans Serif; font-size: 16px;")  # Set label font style

        self.topic_title_browser = TextBrowserDate()
        self.topic_title_browser.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align text to the left
        self.topic_title_browser.setFixedHeight(40)  # Set height for consistency
        self.topic_title_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.topic_title_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.topic_title_browser.setStyleSheet("font-family: Arial; font-size: 20px; color: darkblue;")  # Title style

        # Mock-up value for title
        self.topic_title_browser.setHtml('<div style="line-height:27px;">BAŞLIK DENEME YAZISI BAŞLIK DENEME YAZISI</div>')

        self.topic_title_layout.addWidget(self.topic_title_label)
        self.topic_title_layout.addWidget(self.topic_title_browser)

        # Create the second row for location and date
        self.location_date_layout = QHBoxLayout()

        # Location label and browser
        self.location_label = QLabel("YER")
        self.location_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Align text to the right
        self.location_label.setFixedWidth(label_width)  # Set the same fixed width for label
        self.location_label.setStyleSheet(
            "font-family: MS Reference Sans Serif; font-size: 16px;")  # Set label font style

        self.location_browser = TextBrowserDate()
        self.location_browser.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align text to the left
        self.location_browser.setFixedHeight(40)  # Set height for consistency
        self.location_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.location_browser.setStyleSheet("font-family: Arial; font-size: 18px; color: darkred;")  # Location style
        self.location_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.location_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Mock-up value for location
        self.location_browser.setHtml(
            '<div style="line-height:26px;">DENEME ŞEHRİ DENEME SEMTİ DENEME KÖYÜ DENEMELER</div>')

        self.location_date_layout.addWidget(self.location_label)
        self.location_date_layout.addWidget(self.location_browser)

        # Date label and browser
        self.date_label = QLabel("TARİH")
        self.date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Align text to the right
        self.date_label.setFixedWidth(label_width)  # Set the same fixed width for label
        self.date_label.setStyleSheet("font-family: MS Reference Sans Serif; font-size: 16px;")  # Set label font style

        self.date_browser = TextBrowserDate()
        self.date_browser.setAlignment(Qt.AlignHCenter)  # Align text to the left
        self.date_browser.setFixedHeight(40)  # Set height for consistency
        self.date_browser.setFixedWidth(250)  # Set the fixed width for the date
        self.date_browser.setStyleSheet("font-family: Arial; font-size: 18px; color: darkgreen;")  # Date style
        self.date_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.date_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Mock-up value for date
        self.date_browser.setHtml('<div style="line-height:26px;">09 Ağustos 9999 Cumartesi</div>')

        self.location_date_layout.addWidget(self.date_label)
        self.location_date_layout.addWidget(self.date_browser)

        # Add both rows to the main layout
        self.main_layout.addLayout(self.topic_title_layout)
        self.main_layout.addLayout(self.location_date_layout)

        # Set the main layout to the frame
        self.setLayout(self.main_layout)

    def set_info(self, media: Media):
        if media.topic:
            if media.title:
                topic_title_text = f"{media.topic} / {media.title}"
            else:
                topic_title_text = media.topic
        else:
            topic_title_text = media.title

        self.topic_title_browser.set_text(27, topic_title_text)
        self.location_browser.set_text(26, media.location)
        self.date_browser.set_date(26, media.date_text, media.date_est)
