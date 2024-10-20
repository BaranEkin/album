from PyQt5.QtWidgets import (
    QApplication, QFrame, QVBoxLayout, QScrollArea, QWidget,
    QCheckBox, QGroupBox, QPushButton, QHBoxLayout
)
from PyQt5.QtGui import QIcon

from gui.Constants import Constants


class FrameAction(QFrame):
    def __init__(self, album_list, parent=None):
        super().__init__()
        
        self.parent = parent
        self.album_list = album_list
        # Main layout for the frame
        self.layout = QVBoxLayout(self)

        # Scrollable area for checkboxes
        self.scroll_area_albums = QScrollArea()
        self.scroll_area_albums.setFixedHeight(500)
        self.scroll_area_albums.setWidgetResizable(False)

        # Container for the checkboxes
        self.container_albums = QWidget()
        self.layout_albums = QVBoxLayout(self.container_albums)
        self.layout_albums.setSpacing(0)

        # Dictionary to store the mapping between checkboxes and tags
        self.checkbox_to_album_tag = {}

        # Create checkboxes for each path and store the tag
        for path, tag in self.album_list:
            checkbox = QCheckBox(f"{path}")
            self.layout_albums.addWidget(checkbox)
            # Store the checkbox-tag mapping
            self.checkbox_to_album_tag[checkbox] = tag

        self.container_albums.setLayout(self.layout_albums)
        self.container_albums.setMinimumHeight(500)
        self.container_albums.setMinimumWidth(211)
        self.container_albums.setStyleSheet("background-color: white;")
        self.scroll_area_albums.setWidget(self.container_albums)

        # Bottom frame containing group box and button
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(360)
        self.bottom_layout = QVBoxLayout(bottom_frame)

        # Empty group box
        group_box = QGroupBox()
        self.bottom_layout.addWidget(group_box)

        # Button aligned at the bottom-center
        self.button_add = QPushButton(Constants.LABEL_BUTTON_ADD)
        self.button_add.setFixedSize(220, 40)
        self.button_add.setIcon(QIcon("res/icons/Image-Add-Fill--Streamline-Remix-Fill.png"))
        self.bottom_layout.addWidget(self.button_add)

        # Button aligned at the bottom-center
        self.button_upload = QPushButton(Constants.LABEL_BUTTON_UPLOAD)
        self.button_upload.setFixedSize(220, 40)
        self.button_upload.setIcon(QIcon("res/icons/Upload-Cloud-2-Fill--Streamline-Remix-Fill.png"))
        self.bottom_layout.addWidget(self.button_upload)

        # Add scrollable area and bottom frame to main layout
        self.layout.addWidget(self.scroll_area_albums)
        self.layout.addWidget(bottom_frame)

    def get_selected_album_tags(self):
        selected_album_tags = []

        for checkbox, tag in self.checkbox_to_album_tag.items():
            if checkbox.isChecked():
                selected_album_tags.append(tag)

        return sorted(selected_album_tags)
    
    def clear_selected_album_tags(self):
        for checkbox, tag in self.checkbox_to_album_tag.items():
            checkbox.setChecked(False)
    

