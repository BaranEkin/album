from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QGroupBox, QTextEdit, QRadioButton, QButtonGroup, QCompleter
)
from PyQt5.QtCore import Qt


class FrameAddInfo(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 300)

        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)

        # Frame 1: Title
        frame_title = QFrame(self)
        frame_title_layout = QHBoxLayout(frame_title)
        label_title = QLabel("BAŞLIK")
        label_title.setFixedWidth(40)
        label_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.input_title = QLineEdit()
        self.input_title.setFixedWidth(700)
        frame_title_layout.addWidget(label_title)
        frame_title_layout.addWidget(self.input_title)
        main_layout.addWidget(frame_title)

        # Frame 2: Location
        frame_location = QFrame(self)
        frame_location_layout = QHBoxLayout(frame_location)
        label_location = QLabel("YER")
        label_location.setFixedWidth(40)
        label_location.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.combo_location = QComboBox()
        self.combo_location.setFixedWidth(700)
        self.combo_location.setEditable(True)
        self.combo_location.setInsertPolicy(QComboBox.NoInsert)

        locations = ["New York", "Los Angeles", "San Francisco", "Chicago", "Houston"]
        self.combo_location.addItems(locations)
        self.combo_location.setCurrentText("")
        
        completer = QCompleter(locations)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.combo_location.setCompleter(completer)
        
        frame_location_layout.addWidget(label_location)
        frame_location_layout.addWidget(self.combo_location)
        main_layout.addWidget(frame_location)

        # Frame 3: Time and Tags
        frame_time_and_tags = QFrame(self)
        frame_time_and_tags_layout = QHBoxLayout(frame_time_and_tags)

        # Group box for Time
        group_time = QGroupBox("ZAMAN")
        group_time.setFixedWidth(270)
        time_layout = QVBoxLayout()

        # Top section inside the Time group: Text input + non-editable combo box
        top_time_layout = QHBoxLayout()
        self.input_time = QLineEdit()
        self.label_time_est = QLabel("Hassasiyet:")
        self.input_time.setPlaceholderText("GG.AA.YYYY")
        self.combo_time_est = QComboBox()
        self.combo_time_est.setFixedWidth(100)
        self.combo_time_est.setEditable(False)
        # Mock-up items for the combo box
        self.combo_time_est.addItems(["G.A.Y", "G.A", "G.Y", "G", "A.Y", "A", "Y"])
        top_time_layout.addWidget(self.input_time)
        top_time_layout.addWidget(self.label_time_est)
        top_time_layout.addWidget(self.combo_time_est)
        time_layout.addLayout(top_time_layout)

        # Bottom section inside the Time group: Radio buttons
        bottom_time_layout = QHBoxLayout()
        self.radio_label = QLabel("Oto. Doldur:")
        self.radio_option1 = QRadioButton("Addan")
        self.radio_option2 = QRadioButton("Tarihten")
        self.radio_option3 = QRadioButton("Sabit")

        # Create a button group to ensure only one radio button can be selected at a time
        self.radio_group = QButtonGroup()
        self.radio_group.addButton(self.radio_option1)
        self.radio_group.addButton(self.radio_option2)
        self.radio_group.addButton(self.radio_option3)

        bottom_time_layout.addWidget(self.radio_label)
        bottom_time_layout.addWidget(self.radio_option1)
        bottom_time_layout.addWidget(self.radio_option2)
        bottom_time_layout.addWidget(self.radio_option3)
        time_layout.addLayout(bottom_time_layout)

        group_time.setLayout(time_layout)
        frame_time_and_tags_layout.addWidget(group_time)
        
        # Tags input on the right wrapped in a group box
        group_tags = QGroupBox("ETİKETLER")
        tags_layout = QVBoxLayout()
        self.label_tags = QLabel("Etiketleri virgül ile ayırın:")
        self.input_tags = QLineEdit()
        tags_layout.addWidget(self.label_tags)
        tags_layout.addWidget(self.input_tags)
        group_tags.setLayout(tags_layout)
        
        frame_time_and_tags_layout.addWidget(group_tags)
        main_layout.addWidget(frame_time_and_tags)

        # Frame 4: Notes
        frame_notes = QFrame(self)
        frame_notes_layout = QVBoxLayout(frame_notes)
        group_notes = QGroupBox("NOTLAR")
        notes_layout = QVBoxLayout()
        self.input_notes = QTextEdit()
        notes_layout.addWidget(self.input_notes)
        group_notes.setLayout(notes_layout)
        frame_notes_layout.addWidget(group_notes)
        main_layout.addWidget(frame_notes)

        self.setLayout(main_layout)