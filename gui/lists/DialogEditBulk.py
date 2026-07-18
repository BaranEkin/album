from datetime import datetime
import re
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
)
from PyQt5.QtGui import QIcon
from data.helpers import is_valid_people, replace_in_people_field, turkish_upper
from data.orm import Media
from gui.constants import Constants
from gui.message import show_message
from logger import log


class DialogEditBulk(QDialog):
    def __init__(self, media_list=list[Media], parent=None):
        super().__init__()
        self.setWindowTitle("Medyaları Toplu Düzenle")
        self.setFixedSize(600, 500)
        self.setWindowIcon(
            QIcon("res/icons/Cashing-Check--Streamline-Flex-Gradient.png")
        )

        self.media_list = media_list
        self.edited_media_list = []

        # Main layout
        self.main_layout = QVBoxLayout(self)

        # Metadata fields and their allowed modes
        self.fields = {
            "topic": ["overwrite", "replace"],
            "title": ["overwrite", "replace"],
            "location": ["overwrite", "replace"],
            "people": ["replace"],
            "tags": ["overwrite", "replace", "add", "remove"],
            "notes": ["overwrite", "replace"],
            "date": None,  # No edit modes for Date
            "private": None,  # No edit modes for Private
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

        row = 0
        for field, modes in self.fields.items():
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
                "private": Constants.LABEL_PRIVATE,
            }
            groupbox = QGroupBox(groupbox_titles[field])
            groupbox.setDisabled(True)

            if field == "date":
                # Special layout for "Date" field
                groupbox_layout = QHBoxLayout()

                # Custom Combobox
                custom_combobox = QComboBox()
                custom_combobox.addItems(["G.A.Y", "G.A", "G.Y", "G", "A.Y", "A", "Y"])
                groupbox_layout.addWidget(QLabel(Constants.LABEL_DATE_EST))
                groupbox_layout.addWidget(custom_combobox)

                # Input field stretches to fill the remaining width
                input_lineedit = QLineEdit()
                groupbox_layout.addWidget(QLabel("Tarih:"))
                groupbox_layout.addWidget(input_lineedit, stretch=1)

                groupbox.setLayout(groupbox_layout)

                # Store reference for Date category
                self.frames.append(
                    (
                        field,
                        checkbox,
                        groupbox,
                        None,
                        input_lineedit,
                        None,
                        None,
                        custom_combobox,
                        None,
                    )
                )
            elif field == "private":
                # Special layout for "Private" field: single spinbox 0-9.
                # Tight, right-side group; the group title already says GİZLİLİK
                # so no inner label is needed.
                groupbox.setFixedWidth(70)
                groupbox_layout = QHBoxLayout()

                custom_spinbox = QSpinBox()
                custom_spinbox.setRange(0, 9)
                custom_spinbox.setValue(0)
                custom_spinbox.setToolTip(Constants.TOOLTIP_PRIVATE)
                groupbox_layout.addWidget(custom_spinbox)

                groupbox.setLayout(groupbox_layout)

                self.frames.append(
                    (
                        field,
                        checkbox,
                        groupbox,
                        None,
                        None,
                        None,
                        None,
                        None,
                        custom_spinbox,
                    )
                )
            else:
                # General layout for other fields
                groupbox_layout = QHBoxLayout(groupbox)
                combobox = QComboBox()
                # Add modes with Turkish display
                for mode in modes:
                    combobox.addItem(
                        self.translations[mode], mode
                    )  # mode is the English value
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

                if modes and modes[0] == "replace":
                    input_lineedit2.show()
                    input_arrow_label.show()

                # Store frame components for future reference
                self.frames.append(
                    (
                        field,
                        checkbox,
                        groupbox,
                        combobox,
                        input_lineedit1,
                        input_lineedit2,
                        input_arrow_label,
                        None,
                        None,
                    )
                )

            # Add to grid layout
            if field == "private":
                # Place beside the date row (date was the previous row processed),
                # in columns 2-3 so date and private share the same row.
                grid_layout.addWidget(checkbox, row - 1, 2)
                grid_layout.addWidget(groupbox, row - 1, 3)
            elif field == "date":
                grid_layout.addWidget(checkbox, row, 0)
                grid_layout.addWidget(groupbox, row, 1)
                row += 1
            else:
                grid_layout.addWidget(checkbox, row, 0)
                # Span columns 1-3 so other rows fill the full width
                grid_layout.addWidget(groupbox, row, 1, 1, 3)
                row += 1

        self.main_layout.addLayout(grid_layout)

    def toggle_groupbox(self):
        """Enable/Disable groupbox based on checkbox state."""
        for _, checkbox, groupbox, *_ in self.frames:
            groupbox.setEnabled(checkbox.isChecked())

    def update_input_mode(self, groupbox, index):
        """Update input layout based on selected mode."""
        for _, _, grp, combobox, input1, input2, arrow_label, _, _ in self.frames:
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
        ok_button.setIcon(
            QIcon("res/icons/Upload-Cloud-2-Fill--Streamline-Remix-Fill.png")
        )
        ok_button.clicked.connect(self.on_ok_button)

        button_layout.addStretch()  # Spacer
        button_layout.addWidget(clear_button)
        button_layout.addWidget(ok_button)
        self.main_layout.addLayout(button_layout)

    def clear_dialog(self):
        """Reset dialog to its initial state."""
        for (
            _,
            checkbox,
            groupbox,
            combobox,
            input1,
            input2,
            arrow_label,
            custom_combobox,
            custom_spinbox,
        ) in self.frames:
            checkbox.setChecked(False)
            groupbox.setDisabled(True)
            if combobox:
                combobox.setCurrentIndex(0)
            if input1:
                input1.clear()
            if input2:
                input2.clear()
            if custom_combobox:
                custom_combobox.setCurrentIndex(0)
            if custom_spinbox:
                custom_spinbox.setValue(0)
            if combobox and input2 and arrow_label:
                if combobox.currentData() == "replace":
                    input2.show()
                    arrow_label.show()
                else:
                    input2.hide()
                    arrow_label.hide()

    def get_edit_data(self):
        """Retrieve data from enabled elements."""
        data = {}
        for (
            field,
            checkbox,
            _,
            combobox,
            input1,
            input2,
            _,
            custom_combobox,
            custom_spinbox,
        ) in self.frames:
            if checkbox.isChecked():
                if field == "date":
                    data[field] = {
                        "option": custom_combobox.currentIndex(),
                        "input": input1.text(),
                    }
                elif field == "private":
                    data[field] = {
                        "value": custom_spinbox.value(),
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
                                "from": input1.text().strip(),
                                "to": input2.text().strip(),
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
                                "input": re.sub(r"\s*,\s*", ",", input1.text().strip()),
                            }
                        else:
                            data[field] = {
                                "mode": mode,
                                "input": input1.text().strip(),
                            }
        return data

    def is_valid_edit_data(self, edit_data):
        if edit_data.get("people"):
            people_from = edit_data["people"]["from"].strip()
            people_to = edit_data["people"]["to"].strip()

            if not people_from or not people_to:
                show_message(
                    "Kişiler değiştirme işlemi için eski ve yeni isim alanlarını doldurun.",
                    level="warning",
                )
                return False

            if "," in people_from or "," in people_to:
                show_message(
                    "Kişiler alanı, değiştir modunda virgül içeremez.",
                    level="warning",
                )
                return False

            for media in self.media_list:
                if not media.people:
                    continue

                people_result = replace_in_people_field(
                    media.people, people_from, people_to
                )
                if people_result is None:
                    continue

                if not is_valid_people(people_result):
                    people_log = people_result.replace("\n", "\\n")
                    log(
                        "DialogEditBulk.is_valid_edit_data",
                        f"People result '{people_log}' is incorrectly formatted.",
                        level="warning",
                    )
                    show_message(
                        f"Değiştirme sonucu geçersiz kişi formatı:\n{people_result}\n\n"
                        "Şunlara dikkat edin:\n"
                        "Noktalama işaretleri, semboller veya rakamlar kullanmayın.\n"
                        "İsimlerin baş harflerini ve soyisimlerin tüm harflerini büyük yazın.",
                        level="warning",
                    )
                    return False

                original_count = len(media.people.split(","))
                result_count = len(people_result.split(","))
                if original_count != result_count:
                    log(
                        "DialogEditBulk.is_valid_edit_data",
                        f"People count changed for {media.media_uuid}: "
                        f"{original_count} -> {result_count}.",
                        level="warning",
                    )
                    show_message(
                        f"Değiştirme kişi sayısını değiştirdi:\n{media.people}\n->\n{people_result}",
                        level="warning",
                    )
                    return False

                if media.people_detect:
                    detect_count = len(
                        [box for box in media.people_detect.split(",") if box.strip()]
                    )
                    if result_count != detect_count:
                        log(
                            "DialogEditBulk.is_valid_edit_data",
                            f"People/detect count mismatch for {media.media_uuid}: "
                            f"{result_count} names vs {detect_count} boxes.",
                            level="warning",
                        )
                        show_message(
                            "Bazı medyalarda kişi sayısı ile yüz kutusu sayısı uyuşmuyor.\n"
                            "Bu medyaları tek tek düzenleyerek düzeltin.",
                            level="warning",
                        )
                        return False

        if edit_data.get("tags"):
            tags_input = edit_data["tags"]["input"]
            if edit_data["tags"]["mode"] == "replace":
                if tags_input.find(",") != -1:
                    show_message(
                        "Etiketler alanı, değiştir modunda virgül içeremez.",
                        level="warning",
                    )
                    return False

        if edit_data.get("date"):
            date_input = edit_data["date"]["input"]
            try:
                # Try parsing date as "DD.MM.YYYY"
                _ = datetime.strptime(date_input, "%d.%m.%Y").strftime("%d.%m.%Y")
            except ValueError:
                log(
                    "DialogEditBulk.is_valid_edit_data",
                    f"Date '{date_input}' is incorrectly formatted.",
                    level="warning",
                )
                show_message(
                    "Lütfen tarih alanını GG.AA.YYYY formatında girin.", level="warning"
                )
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
                        topic = media.topic.replace(
                            edit_data["topic"]["from"], edit_data["topic"]["to"]
                        )

            title = media.title
            if edit_data.get("title"):
                if edit_data["title"]["mode"] == "overwrite":
                    title = edit_data["title"]["input"]
                elif edit_data["title"]["mode"] == "replace":
                    if media.title:
                        title = media.title.replace(
                            edit_data["title"]["from"], edit_data["title"]["to"]
                        )

            location = media.location
            if edit_data.get("location"):
                if edit_data["location"]["mode"] == "overwrite":
                    location = edit_data["location"]["input"]
                elif edit_data["location"]["mode"] == "replace":
                    if media.location:
                        location = media.location.replace(
                            edit_data["location"]["from"], edit_data["location"]["to"]
                        )

            notes = media.notes
            if edit_data.get("notes"):
                if edit_data["notes"]["mode"] == "overwrite":
                    notes = edit_data["notes"]["input"]
                elif edit_data["notes"]["mode"] == "replace":
                    if media.notes:
                        notes = media.notes.replace(
                            edit_data["notes"]["from"], edit_data["notes"]["to"]
                        )

            people = media.people
            if edit_data.get("people") and people:
                people_replaced = replace_in_people_field(
                    people,
                    edit_data["people"]["from"],
                    edit_data["people"]["to"],
                )
                if people_replaced is not None:
                    people = people_replaced

            tags = media.tags
            if edit_data.get("tags"):
                if edit_data["tags"]["mode"] == "overwrite":
                    tags = edit_data["tags"]["input"]

                elif edit_data["tags"]["mode"] == "replace":
                    if tags:
                        tags_list = media.tags.split(",")
                        tags_list_replaced = [
                            t.replace(
                                edit_data["tags"]["from"], edit_data["tags"]["to"]
                            )
                            for t in tags_list
                        ]
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

            private = media.private
            if edit_data.get("private"):
                private = edit_data["private"]["value"]

            edited_media = Media()
            edited_media.media_uuid = media.media_uuid
            edited_media.topic = topic
            edited_media.title = title
            edited_media.location = location
            edited_media.tags = tags
            edited_media.notes = notes
            edited_media.people = people
            edited_media.people_count = len(people.split(",")) if people else 0
            edited_media.people_detect = media.people_detect
            edited_media.date_text = date_text
            edited_media.date_est = date_est
            edited_media.albums = media.albums
            edited_media.private = private

            self.edited_media_list.append(edited_media)

        return True

    def on_ok_button(self):
        if self.get_edited_media_list():
            self.accept()
