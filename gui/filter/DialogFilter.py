from PyQt5.QtWidgets import (
    QFrame,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QGroupBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QRadioButton,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from data.data_manager import DataManager
from data.helpers import get_unix_time_days_ago
from data.media_filter import MediaFilter
from gui.filter.FrameDetailedFilter import FrameDetailedFilter
from gui.filter.FrameTreeAlbums import FrameTreeAlbums


class DialogFilter(QDialog):
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__()

        self.data_manager = data_manager
        self.parent = parent
        self.albums = self.data_manager.get_all_albums()
        self.media_filter = None

        self.checkbox_include_child = QCheckBox("Alt albümleri dahil et")
        self.checkbox_include_child.setChecked(True)

        self.frame_tree = FrameTreeAlbums(self.albums, parent=self)
        self.checkbox_include_child.stateChanged.connect(
            self.frame_tree.on_select_albums
        )

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

        self.label_latest = QLabel("Eklenme Tarihi:")
        self.combo_latest = QComboBox()
        self.combo_latest.setFixedWidth(90)
        self.combo_latest.addItems(
            [
                "Tümü",
                "Son 1 hafta",
                "Son 2 hafta",
                "Son 1 ay",
                "Son 3 ay",
                "Son 6 ay",
                "Son 1 yıl",
            ]
        )

        self.layout_options = QHBoxLayout()
        self.layout_options.addWidget(
            self.checkbox_include_child, alignment=Qt.AlignLeft
        )
        self.layout_latest = QHBoxLayout()
        self.layout_latest.addWidget(self.label_latest, alignment=Qt.AlignRight)
        self.layout_latest.addWidget(self.combo_latest)
        self.layout_options.addLayout(self.layout_latest)
        self.layout_options.setContentsMargins(5, 5, 0, 5)

        self.layout_main = QVBoxLayout()
        self.layout_main.addWidget(self.frame_tree)
        self.layout_main.addLayout(self.layout_options)
        self.layout_main.addWidget(self.group_box_quick)
        self.layout_main.addWidget(self.group_box_detailed)
        self.layout_main.addLayout(self.layout_bottom)

        self.setLayout(self.layout_main)
        self.setWindowTitle("Süzgeç")
        self.setWindowIcon(
            QIcon("res/icons/Filter-2--Streamline-Sharp-Gradient--Free.png")
        )
        self.on_change_mode()

    def recenter(self):
        """Recenter the dialog relative to its parent"""

        if self.parent:
            self.move(self.parent.geometry().center() - self.rect().center())

    def on_change_mode(self):
        if self.radio_quick.isChecked():
            self.group_box_detailed.hide()
            self.group_box_quick.show()
            self.setFixedSize(620, 480)
            self.recenter()
        else:
            self.group_box_quick.hide()
            self.group_box_detailed.show()
            self.setFixedSize(620, 850)
            self.recenter()

    def update_albums(self):
        self.albums = self.data_manager.get_all_albums()

    def get_quick(self):
        return self.input_quick.text().strip()

    def get_latest(self):
        if self.combo_latest.currentIndex() != 0:
            selection_to_days = {1: 7, 2: 14, 3: 30, 4: 90, 5: 180, 6: 365}
            days = selection_to_days[self.combo_latest.currentIndex()]
            return (get_unix_time_days_ago(days), -1.0)

    def build_filter(self) -> MediaFilter:
        if self.radio_quick.isChecked():
            media_filter = MediaFilter(
                albums=self.frame_tree.get_selected_albums(),
                created_at_range_enabled=True
                if self.combo_latest.currentIndex() != 0
                else False,
                created_at_range=self.get_latest() or (-1.0, -1.0),
                quick=self.get_quick(),
            )

        else:
            media_filter = MediaFilter(
                albums=self.frame_tree.get_selected_albums(),
                created_at_range_enabled=True
                if self.combo_latest.currentIndex() != 0
                else False,
                created_at_range=self.get_latest() or (-1.0, -1.0),
                topic=self.frame_detailed.get_topic(),
                title=self.frame_detailed.get_title(),
                location=self.frame_detailed.get_location(),
                people=self.frame_detailed.get_people(),
                people_count_range=self.frame_detailed.get_people_count_range(),
                people_count_range_enabled=self.frame_detailed.get_people_count_range_enabled(),
                file_type=self.frame_detailed.get_file_type(),
                file_ext=self.frame_detailed.get_ext(),
                tags=self.frame_detailed.get_tags(),
                date_range=self.frame_detailed.get_date_range(),
                date_range_enabled=self.frame_detailed.get_date_range_enabled(),
                days=self.frame_detailed.get_days(),
                months=self.frame_detailed.get_months(),
                years=self.frame_detailed.get_years(),
                days_of_week=self.frame_detailed.get_days_of_week(),
                sort=self.frame_detailed.get_sort(),
            )

        return media_filter

    def filter_media(self):
        self.media_filter = self.build_filter()
        self.accept()

    def reset_filter(self):
        self.input_quick.setText("")
        self.combo_latest.setCurrentIndex(0)
        self.frame_detailed.clear_all_fields()
        self.frame_tree.clear_selection()
