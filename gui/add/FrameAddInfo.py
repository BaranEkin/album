from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDialog,
    QComboBox,
    QGroupBox,
    QTextEdit,
    QRadioButton,
    QButtonGroup,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from data.helpers import turkish_upper
from gui.constants import Constants
from gui.add.DialogAssignLocation import DialogAssignLocation


class FrameAddInfo(QFrame):
    def __init__(self, locations, parent=None):
        super().__init__()
        self.locations = locations

        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)

        # Frame: Topic
        frame_topic = QFrame(self)
        frame_topic_layout = QHBoxLayout(frame_topic)
        label_topic = QLabel(Constants.LABEL_TOPIC)
        label_topic.setFixedWidth(40)
        label_topic.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.input_topic = QLineEdit()
        self.input_topic.setFixedWidth(700)
        frame_topic_layout.addWidget(label_topic)
        frame_topic_layout.addWidget(self.input_topic)
        main_layout.addWidget(frame_topic)

        # Frame: Title
        frame_title = QFrame(self)
        frame_title_layout = QHBoxLayout(frame_title)
        label_title = QLabel(Constants.LABEL_TITLE)
        label_title.setFixedWidth(40)
        label_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.input_title = QLineEdit()
        self.input_title.setFixedWidth(700)
        frame_title_layout.addWidget(label_title)
        frame_title_layout.addWidget(self.input_title)
        main_layout.addWidget(frame_title)

        # Frame: Location
        frame_location = QFrame(self)
        frame_location_layout = QHBoxLayout(frame_location)
        label_location = QLabel(Constants.LABEL_LOCATION)
        label_location.setFixedWidth(40)
        label_location.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.input_location = QLineEdit()
        self.input_location.setFixedWidth(670)
        self.button_location = QPushButton()
        self.button_location.setIcon(
            QIcon("res/icons/List-Search--Streamline-Tabler.png")
        )
        self.button_location.setFixedSize(25, 25)
        self.button_location.clicked.connect(self.show_location_dialog)

        frame_location_layout.addWidget(label_location)
        frame_location_layout.addWidget(self.input_location)
        frame_location_layout.addWidget(self.button_location)
        main_layout.addWidget(frame_location)

        # Frame: date and Tags
        frame_date_and_tags = QFrame(self)
        frame_date_and_tags_layout = QHBoxLayout(frame_date_and_tags)

        # Group box for date
        group_date = QGroupBox(Constants.LABEL_DATE)
        group_date.setFixedWidth(270)
        date_layout = QVBoxLayout()

        # Top section inside the date group: Text input + non-editable combo box
        top_date_layout = QHBoxLayout()
        self.input_date = QLineEdit()
        self.label_date_est = QLabel(Constants.LABEL_DATE_EST)
        self.input_date.setPlaceholderText(Constants.DEFAULT_DATE)
        self.combo_date_est = QComboBox()
        self.combo_date_est.setFixedWidth(100)
        self.combo_date_est.setEditable(False)
        # Mock-up items for the combo box
        self.combo_date_est.addItems(["G.A.Y", "G.A", "G.Y", "G", "A.Y", "A", "Y"])
        top_date_layout.addWidget(self.input_date)
        top_date_layout.addWidget(self.label_date_est)
        top_date_layout.addWidget(self.combo_date_est)
        date_layout.addLayout(top_date_layout)

        # Bottom section inside the date group: Radio buttons
        bottom_date_layout = QHBoxLayout()
        self.radio_label = QLabel(Constants.LABEL_DATE_OPTION)
        self.radio_date_from_filename = QRadioButton(
            Constants.LABEL_RADIO_DATE_FROM_FILENAME
        )
        self.radio_date_from_filedate = QRadioButton(
            Constants.LABEL_RADIO_DATE_FROM_FILEDATE
        )
        self.radio_date_fixed = QRadioButton(Constants.LABEL_RADIO_DATE_FIXED)

        # Create a button group to ensure only one radio button can be selected at a time
        self.radio_group_date = QButtonGroup()
        self.radio_group_date.addButton(self.radio_date_from_filename)
        self.radio_group_date.addButton(self.radio_date_from_filedate)
        self.radio_group_date.addButton(self.radio_date_fixed)

        bottom_date_layout.addWidget(self.radio_label)
        bottom_date_layout.addWidget(self.radio_date_from_filename)
        bottom_date_layout.addWidget(self.radio_date_from_filedate)
        bottom_date_layout.addWidget(self.radio_date_fixed)
        date_layout.addLayout(bottom_date_layout)

        group_date.setLayout(date_layout)
        frame_date_and_tags_layout.addWidget(group_date)

        # Tags input on the right wrapped in a group box
        group_tags = QGroupBox(Constants.LABEL_TAGS)
        tags_layout = QVBoxLayout()
        self.label_tags = QLabel(Constants.LABEL_TAGS_HELP)
        self.input_tags = QLineEdit()
        tags_layout.addWidget(self.label_tags)
        tags_layout.addWidget(self.input_tags)
        group_tags.setLayout(tags_layout)

        frame_date_and_tags_layout.addWidget(group_tags)
        main_layout.addWidget(frame_date_and_tags)

        # Frame 4: Notes People
        frame_people_notes = QFrame(self)
        frame_people_notes_layout = QHBoxLayout(frame_people_notes)

        group_people = QGroupBox(Constants.LABEL_PEOPLE)
        group_people.setFixedWidth(270)
        people_layout = QVBoxLayout()
        self.input_people = QTextEdit()
        self.input_people.setEnabled(False)
        people_layout.addWidget(self.input_people)
        group_people.setLayout(people_layout)
        frame_people_notes_layout.addWidget(group_people)

        group_notes = QGroupBox(Constants.LABEL_NOTES)
        notes_layout = QVBoxLayout()
        self.input_notes = QTextEdit()
        notes_layout.addWidget(self.input_notes)
        group_notes.setLayout(notes_layout)
        frame_people_notes_layout.addWidget(group_notes)

        main_layout.addWidget(frame_people_notes)

        self.setLayout(main_layout)

    def show_location_dialog(self):
        dialog = DialogAssignLocation(
            location=self.get_location(), location_list=self.locations, parent=self
        )
        if dialog.exec_() == QDialog.Accepted:
            self.set_location(dialog.input_field.text())

    def get_topic(self):
        return turkish_upper(self.input_topic.text().strip())

    def set_topic(self, topic):
        self.input_topic.setText(turkish_upper(topic))

    def get_title(self):
        return turkish_upper(self.input_title.text().strip())

    def set_title(self, title):
        self.input_title.setText(turkish_upper(title))

    def get_location(self):
        return turkish_upper(self.input_location.text().strip())

    def set_location(self, location):
        self.input_location.setText(turkish_upper(location))

    def get_date(self):
        return self.input_date.text().strip()

    def get_date_option(self):
        selected_option = self.radio_group_date.checkedButton()
        if selected_option:
            selected_name = selected_option.text()
            if selected_name == Constants.LABEL_RADIO_DATE_FROM_FILENAME:
                return 1
            elif selected_name == Constants.LABEL_RADIO_DATE_FROM_FILEDATE:
                return 2
            elif selected_name == Constants.LABEL_RADIO_DATE_FIXED:
                return 3
        return 0

    def set_date(self, date):
        self.input_date.setText(date)

    def get_date_est(self):
        return 7 - self.combo_date_est.currentIndex()

    def set_date_est(self, date_est):
        self.combo_date_est.setCurrentIndex(7 - date_est)

    def get_tags(self):
        return self.input_tags.text().strip()

    def set_tags(self, tags):
        self.input_tags.setText(tags)

    def get_notes(self):
        return self.input_notes.toPlainText().strip()

    def set_notes(self, notes):
        self.input_notes.setPlainText(notes)

    def get_people(self):
        raw_text = self.input_people.toPlainText()
        processed_lines = [
            line.strip() for line in raw_text.splitlines() if line.strip()
        ]
        return ",".join(processed_lines)

    def set_people(self, people: str):
        self.input_people.setPlainText(people.replace(",", "\n"))

    def set_people_enable(self, enable: bool):
        self.input_people.setEnabled(enable)
