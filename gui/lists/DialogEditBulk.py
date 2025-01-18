from datetime import datetime
import re
import sys
import copy
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QCheckBox, QComboBox, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from data.helpers import is_valid_people
from data.orm import Media
from gui.constants import Constants
from gui.message import show_message
from data.helpers import turkish_upper
from logger import log


class DialogEditBulk(QDialog):
    def __init__(self, media_list=list[Media], parent=None):
        super().__init__()
        self.setWindowTitle("Medyaları Toplu Düzenle")
        self.setFixedSize(600, 500)
        self.setWindowIcon(QIcon("res/icons/Cashing-Check--Streamline-Flex-Gradient.png"))

        self.media_list = media_list
        self.edited_media_list = []

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

        ok_button = QPushButton(f"{len(self.media_list)} MEDYAYI DÜZENLE")
        ok_button.setFixedSize(220, 40)
        ok_button.setIcon(QIcon("res/icons/Upload-Cloud-2-Fill--Streamline-Remix-Fill.png"))
        ok_button.clicked.connect(self.on_ok_button)

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
                    mode = combobox.currentData()
                    if mode == "replace":
                        if field in ["topic", "title", "location"]:
                            data[field] = {
                                "mode": mode,
                                "from": turkish_upper(input1.text()),
                                "to": turkish_upper(input2.text()),
                            }
                        else:
                            data[field] = {
                                "mode": mode,
                                "from": input1.text(),
                                "to": input2.text(),
                            }
                    else:
                        if field in ["topic", "title", "location"]:
                            data[field] = {
                                "mode": mode,
                                "input": turkish_upper(input1.text().strip()),
                            }
                        elif field in ["people", "tags"]:
                            # Remove whitespace around commas
                            data[field] = {
                                "mode": mode,
                                "input": re.sub(r'\s*,\s*', ',', input1.text().strip()),
                            }
                        else:
                            data[field] = {
                                "mode": mode,
                                "input": input1.text().strip(),
                            }
        return data

    def is_valid_edit_data(self, edit_data):
        if edit_data.get("people"):
            people_input = edit_data["people"]["input"]
            if edit_data["people"]["mode"] == "replace":
                if people_input.find(",") != -1:
                    show_message("Kişiler alanı, değiştir modunda virgül içeremez.", level="warning")
                    return False
            else:
                if not is_valid_people(people_input):
                    log("DialogEditBulk.is_valid_edit_data", f"People '{people_input}' is incorrectly formatted.", level="warning")
                    show_message("Kişiler alanını formatı hatalı. Şunlara dikkat edin:\nİsimlerin baş harflerini ve soyisimlerin tüm harflerini büyük yazın.\nBirden fazla kişiyi virgül ile ayırın.", level="warning")
                    return False
        
        if edit_data.get("tags"):
            tags_input = edit_data["tags"]["input"]
            if edit_data["tags"]["mode"] == "replace":
                if tags_input.find(",") != -1:
                    show_message("Etiketler alanı, değiştir modunda virgül içeremez.", level="warning")
                    return False
        
        if edit_data.get("date"):
            date_input = edit_data["date"]["input"]
            try:
                # Try parsing date as "DD.MM.YYYY"
                _ = datetime.strptime(date_input, "%d.%m.%Y").strftime("%d.%m.%Y")
            except ValueError as e:
                log("DialogEditBulk.is_valid_edit_data", f"Date '{date_input}' is incorrectly formatted.", level="warning")
                show_message("Lütfen tarih alanını GG.AA.YYYY formatında girin.", level="warning")
                return False

        return True

    
    def get_edited_media_list(self):

        edit_data = self.get_edit_data()
        if not self.is_valid_edit_data(edit_data):
            return False
        
        self.edited_media_list = []

        for media in self.media_list:
            topic = media.topic
            if edit_data.get("topic"):
                if edit_data["topic"]["mode"] == "overwrite":
                    topic = edit_data["topic"]["input"]
                elif edit_data["topic"]["mode"] == "replace":
                    if media.topic:
                        topic = media.topic.replace(edit_data["topic"]["from"], edit_data["topic"]["to"])

            title = media.title
            if edit_data.get("title"):
                if edit_data["title"]["mode"] == "overwrite":
                    title = edit_data["title"]["input"]
                elif edit_data["title"]["mode"] == "replace":
                    if media.title:
                        title = media.title.replace(edit_data["title"]["from"], edit_data["title"]["to"])

            location = media.location
            if edit_data.get("location"):
                if edit_data["location"]["mode"] == "overwrite":
                    location = edit_data["location"]["input"]
                elif edit_data["location"]["mode"] == "replace":
                    if media.location:
                        location = media.location.replace(edit_data["location"]["from"], edit_data["location"]["to"])
            
            notes = media.notes
            if edit_data.get("notes"):
                if edit_data["notes"]["mode"] == "overwrite":
                    notes = edit_data["notes"]["input"]
                elif edit_data["notes"]["mode"] == "replace":
                    if media.notes:
                        notes = media.notes.replace(edit_data["notes"]["from"], edit_data["notes"]["to"])
            
            people = media.people
            if edit_data.get("people"):
                if edit_data["people"]["mode"] == "overwrite":
                    people = edit_data["people"]["input"]

                elif edit_data["people"]["mode"] == "replace":
                    if people:
                        people_list = media.people.split(",")
                        people_list_replaced = [p.replace(edit_data["people"]["from"], edit_data["people"]["to"]) for p in people_list]
                        people_new = ", ".join(people_list_replaced)
                        people = people_new

                elif edit_data["people"]["mode"] == "add":
                    people_to_add = edit_data["people"]["input"]
                    if people:
                        people_to_add_list = people_to_add.split(",")
                        people_list = media.people.split(", ")
                        people_list.extend(people_to_add_list)
                        people = ",".join(people_list)
                    else:
                        people = people_to_add

                elif edit_data["people"]["mode"] == "remove":
                    if people:
                        people_to_remove = edit_data["people"]["input"]
                        people_to_remove_list = people_to_remove.split(",")
                        people_list = media.people.split(",")
                        for p in people_to_remove_list:
                            if p in people_list:
                                people_list.remove(p)

                        people = ",".join(people_list)


            tags = media.tags
            if edit_data.get("tags"):
                if edit_data["tags"]["mode"] == "overwrite":
                    tags = edit_data["tags"]["input"]

                elif edit_data["tags"]["mode"] == "replace":
                    if tags:
                        tags_list = media.tags.split(",")
                        tags_list_replaced = [t.replace(edit_data["tags"]["from"], edit_data["tags"]["to"]) for t in tags_list]
                        tags = ", ".join(tags_list_replaced)

                elif edit_data["tags"]["mode"] == "add":
                    tags_to_add = edit_data["tags"]["input"]
                    if tags:
                        tags_to_add_list = tags_to_add.split(",")
                        tags_list = media.tags.split(",")
                        tags_list.extend(tags_to_add_list)
                        tags = ",".join(tags_list)
                    else:
                        tags = tags_to_add

                elif edit_data["tags"]["mode"] == "remove":
                    if tags:
                        tags_to_remove = edit_data["tags"]["input"]

                        tags_to_remove_list = tags_to_remove.split(",")
                        tags_list = media.tags.split(",")
                        for t in tags_to_remove_list:
                            if t in tags_list:
                                tags_list.remove(t)

                        tags = ",".join(tags_list)

            date_text = media.date_text
            date_est = media.date_est
            if edit_data.get("date"):
                date_text = edit_data["date"]["input"]
                date_est = 7 - edit_data["date"]["option"]

            edited_media = Media()
            edited_media.media_uuid = media.media_uuid
            edited_media.topic = topic
            edited_media.title = title
            edited_media.location = location
            edited_media.tags = tags
            edited_media.notes = notes
            edited_media.people = people
            edited_media.people_count = len(people.split(",")) if people else 0
            edited_media.date_text = date_text
            edited_media.date_est = date_est

            self.edited_media_list.append(edited_media)
        
        return True

    def on_ok_button(self):
        if self.get_edited_media_list():
            self.accept()

