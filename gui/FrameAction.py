from PyQt5.QtWidgets import (
    QApplication, QFrame, QVBoxLayout, QScrollArea, QWidget,
    QCheckBox, QGroupBox, QPushButton, QHBoxLayout
)


class FrameAction(QFrame):
    def __init__(self, parent=None):
        super().__init__()
        
        # Main layout for the frame
        self.layout = QVBoxLayout(self)

        # Scrollable area for checkboxes
        self.scroll_area_albums = QScrollArea()
        self.scroll_area_albums.setFixedHeight(600)
        self.scroll_area_albums.setWidgetResizable(False)
        
        # Container for the checkboxes
        self.container_albums = QWidget()
        self.layout_albums = QVBoxLayout(self.container_albums)
        self.layout_albums.setSpacing(0)

        for i in range(50):
            checkbox = QCheckBox(f"Option {i + 1}")
            self.layout_albums.addWidget(checkbox)

        self.container_albums.setLayout(self.layout_albums)
        self.container_albums.setMinimumHeight(600)
        self.container_albums.setMinimumWidth(261)
        self.container_albums.setStyleSheet("background-color: white;")
        self.scroll_area_albums.setWidget(self.container_albums)

        # Bottom frame containing group box and button
        bottom_frame = QFrame()
        bottom_frame.setFixedHeight(300)
        self.bottom_layout = QVBoxLayout(bottom_frame)

        # Empty group box
        group_box = QGroupBox("Group Box")
        self.bottom_layout.addWidget(group_box)

        # Button aligned at the bottom-center
        self.button_add = QPushButton("MEDYAYI ALBÜME EKLE")
        self.button_add.setFixedWidth(260) 
        self.bottom_layout.addWidget(self.button_add)

        # Add scrollable area and bottom frame to main layout
        self.layout.addWidget(self.scroll_area_albums)
        self.layout.addWidget(bottom_frame)

