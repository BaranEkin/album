from PyQt5.QtWidgets import (
    QFrame,
    QLabel,
    QGroupBox,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from data.orm import Media
from gui.main.FrameInfo import FrameInfo
from gui.constants import Constants


class FrameBottom(QFrame):
    # Add signal for settings button
    settings_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        # Create a horizontal layout for the parent frame
        self.layout_main = QHBoxLayout()
        self.layout_main.setContentsMargins(0, 0, 0, 0)

        # Create left QFrame with fixed width and height
        self.frame_cloud = QFrame()
        self.frame_cloud.setFixedWidth(160)
        self.frame_cloud.setFixedHeight(100)  # Set height as requested
        # left_frame.setStyleSheet("background-color: lightgray;")  # Optional styling
        self.layout_cloud = QVBoxLayout()
        self.layout_cloud.setContentsMargins(
            0, 0, 0, 0
        )  # Remove margins to make the label start at the top
        self.layout_cloud.setSpacing(0)  # Remove spacing

        # Create and center the QLabel, setting alignment to the top of the frame
        self.top_label = QLabel("")
        self.top_label.setAlignment(Qt.AlignCenter)

        # Ensure that the label starts at y=0 by setting alignment and margins
        self.layout_cloud.addWidget(self.top_label, alignment=Qt.AlignTop)

        # Create a group box at the bottom with a label saying "cloud"
        self.group_box_cloud = QGroupBox(Constants.GROUP_BOX_CLOUD)
        self.group_box_cloud.setFixedSize(160, 70)

        # Create horizontal layout for the buttons inside the group box
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Create buttons
        self.status_cloud = QLabel()
        self.status_cloud.setText("")
        self.status_cloud.setFixedSize(25, 25)
        self.status_cloud.setToolTip(Constants.TOOLTIP_CLOUD_SUCCESS)
        self.status_cloud.setPixmap(
            QPixmap("res/icons/Cloud-Check--Streamline-Core.png")
        )
        self.status_cloud.setScaledContents(True)
        self.button_layout.addWidget(self.status_cloud)

        self.status_storage = QLabel()
        self.status_storage.setText("")
        self.status_storage.setFixedSize(25, 25)
        self.status_storage.setToolTip(Constants.TOOLTIP_STORAGE_ON)
        self.status_storage.setPixmap(
            QPixmap("res/icons/Download-Computer--Streamline-Core-Green.png")
        )
        self.status_storage.setScaledContents(True)
        self.button_layout.addWidget(self.status_storage)

        self.button_settings = QPushButton(Constants.SETTINGS)
        self.button_settings.setFocusPolicy(Qt.NoFocus)
        self.button_settings.setFixedSize(80, 30)
        self.button_settings.setIcon(QIcon("res/icons/Setting--Streamline-Unicons.png"))
        self.button_settings.setToolTip(Constants.TOOLTIP_BUTTON_SETTINGS)
        self.button_settings.clicked.connect(self.on_settings_clicked)
        self.button_layout.addWidget(self.button_settings)

        self.group_box_cloud.setLayout(self.button_layout)
        self.layout_cloud.addWidget(self.group_box_cloud)
        self.frame_cloud.setLayout(self.layout_cloud)

        # Create right QFrame with fixed width and height, and add buttons in a grid
        self.frame_button_area = QFrame()
        self.frame_button_area.setFixedWidth(142)
        self.frame_button_area.setFixedHeight(100)  # Set height as requested

        # Create a grid layout for the buttons inside the right frame
        self.layout_button_area = QGridLayout()

        self.button_back = QPushButton()
        self.button_back.setFocusPolicy(Qt.NoFocus)
        self.button_back.setFixedSize(40, 40)
        self.button_back.setIcon(
            QIcon("res/icons/Arrow-Fat-Left-Fill--Streamline-Phosphor-Fill.png")
        )
        self.button_back.setIconSize(QSize(30, 30))
        self.button_back.setText("")
        self.button_back.setToolTip(Constants.TOOLTIP_BUTTON_BACK)
        self.layout_button_area.addWidget(self.button_back, 0, 0)

        self.button_forward = QPushButton()
        self.button_forward.setFocusPolicy(Qt.NoFocus)
        self.button_forward.setFixedSize(40, 40)
        self.button_forward.setIcon(
            QIcon("res/icons/Arrow-Fat-Right-Fill--Streamline-Phosphor-Fill.png")
        )
        self.button_forward.setIconSize(QSize(30, 30))
        self.button_forward.setText("")
        self.button_forward.setToolTip(Constants.TOOLTIP_BUTTON_FORWARD)
        self.layout_button_area.addWidget(self.button_forward, 0, 1)

        self.button_slideshow = QPushButton()
        self.button_slideshow.setFocusPolicy(Qt.NoFocus)
        self.button_slideshow.setFixedSize(40, 40)
        self.button_slideshow.setIcon(
            QIcon("res/icons/Slide-Show-Play--Streamline-Sharp.png")
        )
        self.button_slideshow.setIconSize(QSize(30, 30))
        self.button_slideshow.setText("")
        self.button_slideshow.setToolTip(Constants.TOOLTIP_BUTTON_SLIDESHOW)
        self.button_slideshow.setCheckable(True)
        self.layout_button_area.addWidget(self.button_slideshow, 0, 2)

        self.button_notes = QPushButton()
        self.button_notes.setFocusPolicy(Qt.NoFocus)
        self.button_notes.setFixedSize(40, 40)
        self.button_notes.setIcon(
            QIcon("res/icons/Hand-Held-Tablet-Writing--Streamline-Core.png")
        )
        self.button_notes.setIconSize(QSize(30, 30))
        self.button_notes.setText("")
        self.button_notes.setToolTip(Constants.TOOLTIP_BUTTON_NOTES)
        self.button_notes.setCheckable(True)
        self.layout_button_area.addWidget(self.button_notes, 1, 0)

        self.button_people = QPushButton()
        self.button_people.setFocusPolicy(Qt.NoFocus)
        self.button_people.setFixedSize(40, 40)
        self.button_people.setIcon(
            QIcon("res/icons/User-Profile-Focus--Streamline-Core.png")
        )
        self.button_people.setIconSize(QSize(30, 30))
        self.button_people.setText("")
        self.button_people.setToolTip(Constants.TOOLTIP_BUTTON_PEOPLE)
        self.button_people.setCheckable(True)
        self.layout_button_area.addWidget(self.button_people, 1, 1)

        self.button_slideway = QPushButton()
        self.button_slideway.setFocusPolicy(Qt.NoFocus)
        self.button_slideway.setFixedSize(40, 40)
        self.button_slideway.setIcon(
            QIcon("res/icons/Investing-And-Banking--Streamline-Sharp-Forward.png")
        )
        self.button_slideway.setIconSize(QSize(30, 30))
        self.button_slideway.setText("")
        self.button_slideway.setToolTip(Constants.TOOLTIP_BUTTON_SLIDEWAY)
        self.button_slideway.clicked.connect(self.change_slideway_direction)
        self.slideway_direction = "F"
        self.layout_button_area.addWidget(self.button_slideway, 1, 2)
        self.frame_button_area.setLayout(self.layout_button_area)

        # Create the middle QFrame (InfoFrame)
        self.frame_info = FrameInfo()

        # Add all three frames to the parent layout
        self.layout_main.addWidget(self.frame_cloud)
        self.layout_main.addWidget(
            self.frame_info
        )  # This will stretch to fill the space
        self.layout_main.addWidget(self.frame_button_area)

        # Set the parent layout to this frame
        self.setLayout(self.layout_main)

    def set_media_info(self, media: Media):
        self.frame_info.set_info(media)
        if media.notes:
            self.button_notes.setEnabled(True)
        else:
            self.button_notes.setEnabled(False)

        if media.people:
            self.button_people.setEnabled(True)
        else:
            self.button_people.setEnabled(False)

    def get_slideway_direction(self):
        return self.slideway_direction

    def change_slideway_direction(self):
        if self.slideway_direction == "F":
            self.button_slideway.setIcon(
                QIcon("res/icons/Investing-And-Banking--Streamline-Sharp-Back.png")
            )
            self.slideway_direction = "B"

        elif self.slideway_direction == "B":
            self.button_slideway.setIcon(
                QIcon("res/icons/Investing-And-Banking--Streamline-Sharp-Random.png")
            )
            self.slideway_direction = "R"

        elif self.slideway_direction == "R":
            self.button_slideway.setIcon(
                QIcon("res/icons/Investing-And-Banking--Streamline-Sharp-Forward.png")
            )
            self.slideway_direction = "F"

    def on_settings_clicked(self):
        self.settings_clicked.emit()
