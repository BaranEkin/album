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
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

from data.data_manager import DataManager
from data.helpers import get_unix_time_days_ago
from data.media_filter import MediaFilter
from gui.constants import Constants
from gui.filter.FrameDetailedFilter import FrameDetailedFilter
from gui.filter.FrameTreeAlbums import FrameTreeAlbums


class ToggleSwitch(QFrame):
    def __init__(self, left_text: str, right_text: str, parent=None):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)

        font = QFont()
        font.setPointSize(8)

        self._left_label = QLabel(left_text)
        self._left_label.setFont(font)
        self._left_label.setAlignment(Qt.AlignCenter)
        self._left_label.setFixedSize(40, 22)
        self._left_label.setCursor(Qt.PointingHandCursor)
        self._left_label.mousePressEvent = lambda _: self.set_left_active(True)

        self._right_label = QLabel(right_text)
        self._right_label.setFont(font)
        self._right_label.setAlignment(Qt.AlignCenter)
        self._right_label.setFixedSize(40, 22)
        self._right_label.setCursor(Qt.PointingHandCursor)
        self._right_label.mousePressEvent = lambda _: self.set_left_active(False)

        self._layout.addWidget(self._left_label)
        self._layout.addWidget(self._right_label)
        self.setFixedSize(86, 26)

        self._left_active = False
        self.set_left_active(False)

    def _update_styles(self):
        active = (
            "background-color: #4a90d9; color: white; border-radius: 3px; padding: 2px;"
        )
        inactive = (
            "background-color: #d0d0d0; color: #555; border-radius: 3px; padding: 2px;"
        )
        self._left_label.setStyleSheet(active if self._left_active else inactive)
        self._right_label.setStyleSheet(inactive if self._left_active else active)

    def set_left_active(self, active: bool):
        self._left_active = active
        self._update_styles()

    def is_left_active(self) -> bool:
        return self._left_active


class DialogFilter(QDialog):
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__()

        self.data_manager = data_manager
        self.parent = parent
        self.albums = self.data_manager.get_all_albums()
        self.media_filter = None

        self.checkbox_include_child = QCheckBox(Constants.FILTER_INCLUDE_CHILDREN)
        self.checkbox_include_child.setChecked(True)

        self.toggle_albums_mode = ToggleSwitch(
            Constants.FILTER_MODE_AND, Constants.FILTER_MODE_OR
        )
        self.toggle_albums_mode.setVisible(False)

        self.frame_tree = FrameTreeAlbums(self.albums)
        self.checkbox_include_child.stateChanged.connect(
            self._on_include_children_changed
        )
        self.frame_tree.selection_changed.connect(self._on_album_selection_changed)

        self.group_box_quick = QGroupBox(Constants.FILTER_QUICK)
        self.layout_quick = QHBoxLayout()
        self.label_quick = QLabel(Constants.FILTER_QUICK_LABEL)
        self.label_quick.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.input_quick = QLineEdit()

        self.layout_quick.addWidget(self.label_quick)
        self.layout_quick.addWidget(self.input_quick)
        self.group_box_quick.setLayout(self.layout_quick)

        self.frame_detailed = FrameDetailedFilter()
        self.group_box_detailed = QGroupBox(Constants.FILTER_DETAILED)
        self.layout_detailed = QVBoxLayout()
        self.layout_detailed.addWidget(self.frame_detailed)
        self.group_box_detailed.setLayout(self.layout_detailed)

        self.layout_button = QHBoxLayout()
        self.frame_button = QFrame()
        self.frame_button.setFixedSize(320, 50)

        self.button_clear = QPushButton(Constants.FILTER_BUTTON_CLEAR)
        self.button_clear.setFixedSize(150, 40)
        self.button_search = QPushButton(Constants.FILTER_BUTTON_SEARCH)
        self.button_search.setFixedSize(150, 40)

        self.button_search.clicked.connect(self.filter_media)
        self.button_clear.clicked.connect(self.reset_filter)

        self.layout_button.addWidget(self.button_clear)
        self.layout_button.addWidget(self.button_search)
        self.frame_button.setLayout(self.layout_button)

        self.frame_radio = QFrame()
        self.layout_radio = QHBoxLayout()
        self.radio_quick = QRadioButton(Constants.FILTER_QUICK)
        self.radio_detailed = QRadioButton(Constants.FILTER_DETAILED)

        self.radio_quick.toggled.connect(self.on_change_mode)
        self.radio_detailed.toggled.connect(self.on_change_mode)
        self.radio_quick.setChecked(True)

        self.layout_radio.addWidget(self.radio_quick)
        self.layout_radio.addWidget(self.radio_detailed)
        self.frame_radio.setLayout(self.layout_radio)

        self.layout_bottom = QHBoxLayout()
        self.layout_bottom.addWidget(self.frame_radio, alignment=Qt.AlignLeft)
        self.layout_bottom.addWidget(self.frame_button, alignment=Qt.AlignRight)

        self.label_latest = QLabel(Constants.FILTER_CREATED_AT)
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
        self.layout_options.addWidget(self.toggle_albums_mode)
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
        self.setWindowTitle(Constants.FILTER_WINDOW_TITLE)
        self.setWindowIcon(
            QIcon("res/icons/Filter-2--Streamline-Sharp-Gradient--Free.png")
        )
        self.on_change_mode()

    def recenter(self):
        if self.parent:
            self.move(self.parent.geometry().center() - self.rect().center())

    def on_change_mode(self):
        if self.radio_quick.isChecked():
            self.group_box_detailed.hide()
            self.group_box_quick.show()
            self.setFixedSize(620, 510)
            self.recenter()
        else:
            self.group_box_quick.hide()
            self.group_box_detailed.show()
            self.setFixedSize(620, 880)
            self.recenter()

    def _on_include_children_changed(self, state):
        self.frame_tree.set_include_children(state == Qt.Checked)

    def _on_album_selection_changed(self):
        self.toggle_albums_mode.setVisible(self.frame_tree.get_checked_count() > 1)

    def update_albums(self):
        self.albums = self.data_manager.get_all_albums()

    def get_quick(self):
        return self.input_quick.text().strip()

    def get_latest(self):
        if self.combo_latest.currentIndex() != 0:
            selection_to_days = {1: 7, 2: 14, 3: 30, 4: 90, 5: 180, 6: 365}
            days = selection_to_days[self.combo_latest.currentIndex()]
            return (get_unix_time_days_ago(days), -1.0)

    def _get_album_filter_args(self) -> dict:
        return {
            "album_groups": self.frame_tree.get_selected_album_groups(),
            "albums_mode": "and" if self.toggle_albums_mode.is_left_active() else "or",
        }

    def build_filter(self) -> MediaFilter:
        album_args = self._get_album_filter_args()

        if self.radio_quick.isChecked():
            media_filter = MediaFilter(
                **album_args,
                created_at_range_enabled=self.combo_latest.currentIndex() != 0,
                created_at_range=self.get_latest() or (-1.0, -1.0),
                quick=self.get_quick(),
            )
        else:
            media_filter = MediaFilter(
                **album_args,
                created_at_range_enabled=self.combo_latest.currentIndex() != 0,
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
        self.checkbox_include_child.setChecked(True)
        self.toggle_albums_mode.set_left_active(False)
        self.toggle_albums_mode.setVisible(False)
