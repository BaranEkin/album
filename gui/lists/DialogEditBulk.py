import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QCheckBox, QComboBox, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from gui.constants import Constants


class DialogEditBulk(QDialog):
    def __init__(self, number_of_media:int, parent=None):
        super().__init__()
        self.setWindowTitle("Medyaları Toplu Düzenle")
        self.setFixedSize(600, 400)
        self.setWindowIcon(QIcon("res/icons/Cashing-Check--Streamline-Flex-Gradient.png"))

        self.number_of_media = number_of_media
        self.data = None

        # Main layout
        self.main_layout = QVBoxLayout(self)

        # Metadata fields and their allowed modes
        self.fields = {
            "topic": ["overwrite", "replace"],
            "title": ["overwrite", "replace"],
            "location": ["overwrite", "replace"],
            "people": ["overwrite", "replace", "add", "remove"],
            "tags": ["overwrite", "replace", "add", "remove"],
            "notes": ["overwrite", "replace"],
            "date": None,  # No edit modes for Date
        }
        # Turkish translations for display
        self.translations = {
            "overwrite": "Üzerine Yaz",
            "replace": "Değiştir",
            "add": "Ekle",
            "remove": "Çıkar",
        }

        self.frames = []  # To store references for future updates
        self.create_metadata_frames()

        # Bottom buttons
        self.create_buttons()

    def create_metadata_frames(self):
        """Create the metadata frames."""
        grid_layout = QGridLayout()  # Use a grid layout for alignment

        for row, (field, modes) in enumerate(self.fields.items()):
            # Checkbox
            checkbox = QCheckBox()
            checkbox.stateChanged.connect(self.toggle_groupbox)

            # GroupBox with Turkish titles
            groupbox_titles = {
                "topic": Constants.LABEL_TOPIC,
                "title": Constants.LABEL_TITLE,
                "location": Constants.LABEL_LOCATION,
                "people": Constants.LABEL_PEOPLE,
                "tags": Constants.LABEL_TAGS,
                "notes": Constants.LABEL_NOTES,
                "date": Constants.LABEL_DATE,
            }
            groupbox = QGroupBox(groupbox_titles[field])
            groupbox.setDisabled(True)

            if field == "date":
                # Special layout for "Date" field
                groupbox_layout = QHBoxLayout()
                groupbox_layout.setAlignment(Qt.AlignLeft)  # Align contents to the left

                # Custom Combobox
                custom_combobox = QComboBox()
                custom_combobox.addItems(["G.A.Y", "G.A", "G.Y", "G", "A.Y", "A", "Y"])
                groupbox_layout.addWidget(QLabel(Constants.LABEL_DATE_EST))
                groupbox_layout.addWidget(custom_combobox)

                # Input field
                input_lineedit = QLineEdit()
                input_lineedit.setMaximumWidth(100)  # Restrict width for date format
                groupbox_layout.addWidget(QLabel("Tarih:"))
                groupbox_layout.addWidget(input_lineedit)

                # Spacer to push contents to the left
                spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
                groupbox_layout.addSpacerItem(spacer)

                groupbox.setLayout(groupbox_layout)

                # Store reference for Date category
                self.frames.append((field, checkbox, groupbox, None, input_lineedit, None, None, custom_combobox))
            else:
                # General layout for other fields
                groupbox_layout = QHBoxLayout(groupbox)
                combobox = QComboBox()
                # Add modes with Turkish display
                for mode in modes:
                    combobox.addItem(self.translations[mode], mode)  # mode is the English value
                combobox.currentIndexChanged.connect(
                    lambda index, grp=groupbox: self.update_input_mode(grp, index)
                )
                groupbox_layout.addWidget(QLabel("İşlem:"))
                groupbox_layout.addWidget(combobox)

                # Input Frame
                input_layout = QHBoxLayout()
                input_lineedit1 = QLineEdit()
                input_lineedit2 = QLineEdit()
                input_arrow_label = QLabel(">>")
                input_arrow_label.hide()  # Initially hidden (only for "replace")
                input_lineedit2.hide()  # Initially hidden

                input_layout.addWidget(input_lineedit1)
                input_layout.addWidget(input_arrow_label)
                input_layout.addWidget(input_lineedit2)
                groupbox_layout.addLayout(input_layout)

                # Store frame components for future reference
                self.frames.append((field, checkbox, groupbox, combobox, input_lineedit1, input_lineedit2, input_arrow_label, None))

            # Add to grid layout
            grid_layout.addWidget(checkbox, row, 0)  # Checkbox in the first column
            grid_layout.addWidget(groupbox, row, 1)  # GroupBox in the second column

        self.main_layout.addLayout(grid_layout)

    def toggle_groupbox(self):
        """Enable/Disable groupbox based on checkbox state."""
        for _, checkbox, groupbox, *_ in self.frames:
            groupbox.setEnabled(checkbox.isChecked())

    def update_input_mode(self, groupbox, index):
        """Update input layout based on selected mode."""
        for _, _, grp, combobox, input1, input2, arrow_label, _ in self.frames:
            if grp == groupbox:
                mode = combobox.currentData()  # Get the internal (English) mode
                if mode == "replace":
                    input2.show()
                    arrow_label.show()
                else:
                    input2.hide()
                    arrow_label.hide()

    def create_buttons(self):
        """Create Clear and OK buttons."""
        button_layout = QHBoxLayout()
        clear_button = QPushButton("Temizle")
        clear_button.setFixedSize(120, 40)
        clear_button.clicked.connect(self.clear_dialog)

        ok_button = QPushButton(f"{self.number_of_media} MEDYAYI DÜZENLE")
        ok_button.setFixedSize(220, 40)
        ok_button.setIcon(QIcon("res/icons/Upload-Cloud-2-Fill--Streamline-Remix-Fill.png"))
        ok_button.clicked.connect(self.accept)

        button_layout.addStretch()  # Spacer
        button_layout.addWidget(clear_button)
        button_layout.addWidget(ok_button)
        self.main_layout.addLayout(button_layout)

    def clear_dialog(self):
        """Reset dialog to its initial state."""
        for _, checkbox, groupbox, combobox, input1, input2, arrow_label, custom_combobox in self.frames:
            checkbox.setChecked(False)
            groupbox.setDisabled(True)
            if combobox:
                combobox.setCurrentIndex(0)
            if input1:
                input1.clear()
            if input2:
                input2.clear()
                input2.hide()
            if arrow_label:
                arrow_label.hide()
            if custom_combobox:
                custom_combobox.setCurrentIndex(0)

    def get_edit_data(self):
        """Retrieve data from enabled elements."""
        data = {}
        for field, checkbox, _, combobox, input1, input2, _, custom_combobox in self.frames:
            if checkbox.isChecked():
                if field == "date":
                    data[field] = {
                        "option": custom_combobox.currentIndex(),
                        "input": input1.text(),
                    }
                else:
                    mode = combobox.currentData()  # Get English mode
                    if mode == "replace":
                        data[field] = {
                            "mode": mode,
                            "from": input1.text(),
                            "to": input2.text(),
                        }
                    else:
                        data[field] = {
                            "mode": mode,
                            "input": input1.text(),
                        }
        return data
