from PyQt5.QtWidgets import QFrame, QLabel, QGroupBox, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
from gui.FrameInfo import FrameInfo
from gui.Constants import Constants


class FrameBottom(QFrame):
    def __init__(self):
        super().__init__()

        # Create a horizontal layout for the parent frame
        parent_layout = QHBoxLayout()
        parent_layout.setContentsMargins(0, 0, 0, 0)

        # Create left QFrame with fixed width and height
        left_frame = QFrame()
        left_frame.setFixedWidth(160)
        left_frame.setFixedHeight(100)  # Set height as requested
        # left_frame.setStyleSheet("background-color: lightgray;")  # Optional styling
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to make the label start at the top
        left_layout.setSpacing(0)  # Remove spacing
        
        # Create and center the QLabel, setting alignment to the top of the frame
        top_label = QLabel("99999 / 99999")
        top_label.setAlignment(Qt.AlignCenter)
        
        # Ensure that the label starts at y=0 by setting alignment and margins
        left_layout.addWidget(top_label, alignment=Qt.AlignTop) 
        
        # Create a group box at the bottom with a label saying "cloud"
        group_box = QGroupBox(Constants.GROUP_BOX_CLOUD)
        group_box.setFixedSize(160, 70)
        
        # Create horizontal layout for the buttons inside the group box
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Create buttons
        status_cloud = QLabel()
        status_cloud.setText("")
        status_cloud.setFixedSize(25, 25)
        status_cloud.setToolTip(Constants.TOOLTIP_CLOUD_SUCCESS)
        status_cloud.setPixmap(QPixmap("res/icons/Cloud-Check--Streamline-Core.png"))
        status_cloud.setScaledContents(True)
        button_layout.addWidget(status_cloud)

        status_storage = QLabel()
        status_storage.setText("")
        status_storage.setFixedSize(25, 25)
        status_storage.setToolTip(Constants.TOOLTIP_STORAGE_ON)
        status_storage.setPixmap(QPixmap("res/icons/Download-Computer--Streamline-Core-Green.png"))
        status_storage.setScaledContents(True)
        button_layout.addWidget(status_storage)

        button_settings = QPushButton(Constants.SETTINGS)
        button_settings.setFixedSize(80, 30)
        button_settings.setIcon(QIcon("res/icons/Setting--Streamline-Unicons.png"))
        button_layout.addWidget(button_settings)

        group_box.setLayout(button_layout)
        left_layout.addWidget(group_box)
        left_frame.setLayout(left_layout)

        group_box.setLayout(button_layout)
        left_layout.addWidget(group_box)
        left_frame.setLayout(left_layout)

        # Create right QFrame with fixed width and height, and add buttons in a grid
        right_frame = QFrame()
        right_frame.setFixedWidth(142)
        right_frame.setFixedHeight(100)  # Set height as requested

        # Create a grid layout for the buttons inside the right frame
        right_layout = QGridLayout()

        self.button_back = QPushButton()
        self.button_back.setFixedSize(40, 40)
        self.button_back.setIcon(QIcon("res/icons/Arrow-Fat-Left-Fill--Streamline-Phosphor-Fill.png"))
        self.button_back.setIconSize(QSize(30, 30))
        self.button_back.setText("")
        self.button_back.setToolTip(Constants.TOOLTIP_BUTTON_BACK)
        #self.button_back.setStyleSheet("background-color: white;")
        right_layout.addWidget(self.button_back, 0, 0)

        self.button_forward = QPushButton()
        self.button_forward.setFixedSize(40, 40)
        self.button_forward.setIcon(QIcon("res/icons/Arrow-Fat-Right-Fill--Streamline-Phosphor-Fill.png"))
        self.button_forward.setIconSize(QSize(30, 30))
        self.button_forward.setText("")
        self.button_forward.setToolTip(Constants.TOOLTIP_BUTTON_FORWARD)
        #self.button_forward.setStyleSheet("background-color: lightgray;")
        right_layout.addWidget(self.button_forward, 0, 1)

        self.button_slideshow = QPushButton()
        self.button_slideshow.setFixedSize(40, 40)
        self.button_slideshow.setIcon(QIcon("res/icons/Slide-Show-Play--Streamline-Sharp.png"))
        self.button_slideshow.setIconSize(QSize(30, 30))
        self.button_slideshow.setText("")
        self.button_slideshow.setToolTip(Constants.TOOLTIP_BUTTON_SLIDESHOW)
        #self.button_slideshow.setStyleSheet("background-color: gray;")
        right_layout.addWidget(self.button_slideshow, 0, 2)

        self.button_notes = QPushButton()
        self.button_notes.setFixedSize(40, 40)
        self.button_notes.setIcon(QIcon("res/icons/Hand-Held-Tablet-Writing--Streamline-Core.png"))
        self.button_notes.setIconSize(QSize(30, 30))
        self.button_notes.setText("")
        self.button_notes.setToolTip(Constants.TOOLTIP_BUTTON_NOTES)
        #self.button_notes.setStyleSheet("background-color: darkgray;")
        right_layout.addWidget(self.button_notes, 1, 0)

        self.button_people = QPushButton()
        self.button_people.setFixedSize(40, 40)
        self.button_people.setIcon(QIcon("res/icons/User-Profile-Focus--Streamline-Core.png"))
        self.button_people.setIconSize(QSize(30, 30))
        self.button_people.setText("")
        self.button_people.setToolTip(Constants.TOOLTIP_BUTTON_PEOPLE)
        # self.button_people.setStyleSheet("background-color: lightgray;")
        right_layout.addWidget(self.button_people, 1, 1)

        self.button_slideway = QPushButton()
        self.button_slideway.setFixedSize(40, 40)
        self.button_slideway.setIcon(QIcon("res/icons/Investing-And-Banking--Streamline-Sharp-Forward.png"))
        self.button_slideway.setIconSize(QSize(30, 30))
        self.button_slideway.setText("")
        self.button_slideway.setToolTip(Constants.TOOLTIP_BUTTON_SLIDEWAY)
        #self.button_slideway.setStyleSheet("background-color: trasparent;")
        right_layout.addWidget(self.button_slideway, 1, 2)

        right_frame.setLayout(right_layout)

        # Create the middle QFrame (InfoFrame)
        middle_frame = FrameInfo()

        # Add all three frames to the parent layout
        parent_layout.addWidget(left_frame)
        parent_layout.addWidget(middle_frame)  # This will stretch to fill the space
        parent_layout.addWidget(right_frame)

        # Set the parent layout to this frame
        self.setLayout(parent_layout)
