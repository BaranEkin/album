from PyQt5.QtWidgets import (QFrame, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox, QLabel, QLineEdit, QRadioButton)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from data.data_manager import DataManager
from data.media_filter import MediaFilter
from data.helpers import turkish_upper
from gui.filter.FrameDetailedFilter import FrameDetailedFilter
from gui.filter.FrameTreeAlbums import FrameTreeAlbums


class DialogFilter(QDialog):
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__()

        self.data_manager = data_manager
        self.parent = parent
        self.albums = self.data_manager.get_all_albums()
        self.media_list = []

        self.frame_tree = FrameTreeAlbums(self.albums)

        self.group_box_quick = QGroupBox("Hızlı Süzme")
        self.layout_quick = QHBoxLayout()
        self.label_quick = QLabel("Hepsinde:")
        self.label_quick.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.input_quick = QLineEdit()
        
        self.layout_quick.addWidget(self.label_quick)
        self.layout_quick.addWidget(self.input_quick)
        self.group_box_quick.setLayout(self.layout_quick)

        self.frame_detailed = FrameDetailedFilter()
        self.group_box_detailed = QGroupBox("Detaylı Süzme")
        self.layout_detailed = QVBoxLayout()
        self.layout_detailed.addWidget(self.frame_detailed)
        self.group_box_detailed.setLayout(self.layout_detailed)

        self.layout_button = QHBoxLayout()
        self.frame_button = QFrame()
        self.frame_button.setFixedSize(320, 50)

        self.button_clear = QPushButton("Süzmeyi Temizle")
        self.button_clear.setFixedSize(150, 40)
        self.button_search = QPushButton("Süz")
        self.button_search.setFixedSize(150, 40)

        self.button_search.clicked.connect(self.filter_media)
        self.button_clear.clicked.connect(self.reset_filter)

        self.layout_button.addWidget(self.button_clear)
        self.layout_button.addWidget(self.button_search)
        self.frame_button.setLayout(self.layout_button)

        self.frame_radio = QFrame()
        self.layout_radio = QHBoxLayout()
        self.radio_quick = QRadioButton("Hızlı Süzme")
        self.radio_detailed = QRadioButton("Detaylı Süzme")

        self.radio_quick.toggled.connect(self.on_change_mode)
        self.radio_detailed.toggled.connect(self.on_change_mode)
        self.radio_quick.setChecked(True)

        self.layout_radio.addWidget(self.radio_quick)
        self.layout_radio.addWidget(self.radio_detailed)
        self.frame_radio.setLayout(self.layout_radio)

        self.layout_bottom = QHBoxLayout()
        self.layout_bottom.addWidget(self.frame_radio, alignment=Qt.AlignLeft)
        self.layout_bottom.addWidget(self.frame_button, alignment=Qt.AlignRight)

        self.layout_main = QVBoxLayout()
        self.layout_main.addWidget(self.frame_tree)
        self.layout_main.addWidget(self.group_box_quick)
        self.layout_main.addWidget(self.group_box_detailed)
        self.layout_main.addLayout(self.layout_bottom)

        self.setLayout(self.layout_main)
        self.setWindowTitle("Süzgeç")
        self.setWindowIcon(QIcon("res/icons/Filter-2--Streamline-Sharp-Gradient--Free.png"))

    def on_change_mode(self):
        if self.radio_quick.isChecked():
            self.group_box_detailed.hide()
            self.group_box_quick.show()
            self.setFixedSize(620, 450)
        else:
            self.group_box_quick.hide()
            self.group_box_detailed.show()
            self.setFixedSize(620, 810)

    def update_albums(self):
        self.albums = self.data_manager.get_all_albums()

    def get_quick(self):
        return turkish_upper(self.input_quick.text().strip())

    def build_filter(self) -> MediaFilter:

        if self.radio_quick.isChecked():
            media_filter = MediaFilter(
                albums=self.frame_tree.get_selected_albums(),
                quick=self.get_quick()
                )

        else:
            media_filter = MediaFilter(
                albums=self.frame_tree.get_selected_albums(),
                topic=self.frame_detailed.get_topic(),
                title=self.frame_detailed.get_title(),
                location=self.frame_detailed.get_location(),
                people=self.frame_detailed.get_people(),
                people_count_range=self.frame_detailed.get_people_count_range(),
                file_type=self.frame_detailed.get_file_type(),
                file_ext=self.frame_detailed.get_ext(),
                tags=self.frame_detailed.get_tags(),
                date_range=self.frame_detailed.get_date_range(),
                days=self.frame_detailed.get_days(),
                months=self.frame_detailed.get_months(),
                years=self.frame_detailed.get_years(),
                days_of_week=self.frame_detailed.get_days_of_week(),
                sort=self.frame_detailed.get_sort()
            )

        return media_filter

    def filter_media(self):
        media_filter = self.build_filter()
        self.media_list = self.data_manager.get_filtered_media(media_filter)
        self.parent.previous_media_filter = media_filter
        self.accept()

    def reset_filter(self):
        self.input_quick.setText("")
        self.frame_detailed.clear_all_fields()
        self.frame_tree.clear_selection()
