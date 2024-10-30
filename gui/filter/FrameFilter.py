from PyQt5.QtWidgets import (
    QFrame, QLabel, QLineEdit, QCheckBox, QComboBox, QGroupBox,
    QHBoxLayout, QVBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt

from data.helpers import turkish_upper


class FrameFilter(QFrame):
    def __init__(self):
        super().__init__()

        self.setFixedSize(550, 350)

        # Title filter
        self.title_input = QLineEdit()
        self.title_input.setFixedWidth(485)
        self.label_title = QLabel("Başlık:")
        self.label_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        title_layout = QHBoxLayout()
        title_layout.addWidget(self.label_title)
        title_layout.addWidget(self.title_input)

        # Location filter
        self.location_input = QLineEdit()
        self.location_input.setFixedWidth(485)
        self.label_location = QLabel("Yer:")
        self.label_location.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        location_layout = QHBoxLayout()
        location_layout.addWidget(self.label_location)
        location_layout.addWidget(self.location_input)

        # Date filter inside a QGroupBox
        date_group_box = QGroupBox("Tarih")
        self.date_start = QLineEdit()
        self.date_start.setPlaceholderText("Başlangıç")
        self.date_start.setFixedWidth(120)

        self.date_end = QLineEdit()
        self.date_end.setPlaceholderText("Bitiş")
        self.date_end.setFixedWidth(120)

        self.date_range_checkbox = QCheckBox("Aralık")
        self.date_end.setEnabled(False)  # Initially disable the end date input

        # Connect checkbox state change to enable/disable the end date input
        self.date_range_checkbox.stateChanged.connect(self.toggle_date_range)

        # Checkbox for enabling additional date filters
        self.additional_date_filters_checkbox = QCheckBox("Filtrele")
        self.additional_date_filters_checkbox.stateChanged.connect(self.toggle_additional_date_filters)

        # Additional date filters
        self.days_input = QLineEdit()
        self.days_input.setFixedWidth(300)
        self.days_input.setEnabled(False)

        self.months_input = QLineEdit()
        self.months_input.setFixedWidth(300)
        self.months_input.setEnabled(False)

        self.years_input = QLineEdit()
        self.years_input.setFixedWidth(300)
        self.years_input.setEnabled(False)

        self.days_of_week_input = QLineEdit()
        self.days_of_week_input.setFixedWidth(300)
        self.days_of_week_input.setEnabled(False)

        # Layout for date filters
        date_layout = QVBoxLayout()
        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("Tarihler:"))
        date_range_layout.addWidget(self.date_start)
        date_range_layout.addWidget(self.date_end)
        date_range_layout.addWidget(self.date_range_checkbox)

        # Layout for additional date filters with labels
        additional_filters_layout = QVBoxLayout()
        additional_filters_layout.addWidget(self.additional_date_filters_checkbox)

        # Add each labeled input directly to the additional_filters_layout
        days_layout = QHBoxLayout()
        label_days = QLabel("Günler:")
        label_days.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        days_layout.addWidget(label_days)
        days_layout.addWidget(self.days_input)
        additional_filters_layout.addLayout(days_layout)

        months_layout = QHBoxLayout()
        label_months = QLabel("Aylar:")
        label_months.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        months_layout.addWidget(label_months)
        months_layout.addWidget(self.months_input)
        additional_filters_layout.addLayout(months_layout)

        years_layout = QHBoxLayout()
        label_years = QLabel("Yıllar:")
        label_years.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        years_layout.addWidget(label_years)
        years_layout.addWidget(self.years_input)
        additional_filters_layout.addLayout(years_layout)

        days_of_week_layout = QHBoxLayout()
        label_days_of_week = QLabel("Haftanın\nGünleri:")
        label_days_of_week.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        days_of_week_layout.addWidget(label_days_of_week)
        days_of_week_layout.addWidget(self.days_of_week_input)
        additional_filters_layout.addLayout(days_of_week_layout)

        date_layout.addLayout(date_range_layout)
        date_layout.addLayout(additional_filters_layout)
        date_group_box.setLayout(date_layout)

        # Extras
        layout_extras = QHBoxLayout()
        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["Fotoğraf", "Video", "Ses"])
        self.type_dropdown.setFixedWidth(80)

        self.extension_input = QLineEdit()
        self.extension_input.setFixedWidth(40)

        group_box_file = QGroupBox("Dosya")
        group_box_file.setFixedWidth(220)
        type_extension_layout = QHBoxLayout()
        label_type = QLabel("Tip:")
        label_type.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        type_extension_layout.addWidget(label_type)
        type_extension_layout.addWidget(self.type_dropdown)
        label_extension = QLabel("Uzantı:")
        label_extension.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        type_extension_layout.addWidget(label_extension)
        type_extension_layout.addWidget(self.extension_input)
        group_box_file.setLayout(type_extension_layout)

        self.tags_input = QLineEdit()
        self.tags_input.setFixedWidth(220)

        tags_layout = QHBoxLayout()
        label_tags = QLabel("Etiketler:")
        label_tags.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        tags_layout.addWidget(label_tags)
        tags_layout.addWidget(self.tags_input)

        layout_extras.addWidget(group_box_file)
        layout_extras.addLayout(tags_layout)

        # People and People Count filter (same row)
        self.people_input = QLineEdit()
        self.people_input.setFixedWidth(283)

        self.people_count_min = QLineEdit()
        self.people_count_min.setFixedWidth(40)
        self.people_count_max = QLineEdit()
        self.people_count_max.setFixedWidth(40)
        self.people_count_range_checkbox = QCheckBox("Aralık")
        self.people_count_max.setEnabled(False)  # Initially disable the max input

        # Connect checkbox state change to enable/disable the max input
        self.people_count_range_checkbox.stateChanged.connect(self.toggle_people_count_range)

        people_layout = QHBoxLayout()
        label_people = QLabel("Kişiler:")
        label_people.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        people_layout.addWidget(label_people)
        people_layout.addWidget(self.people_input)
        people_layout.addWidget(QLabel("Kişi Adeti:"))
        people_layout.addWidget(self.people_count_min)
        people_layout.addWidget(self.people_count_max)
        people_layout.addWidget(self.people_count_range_checkbox)

        # Layout for the entire frame
        main_layout = QVBoxLayout()
        main_layout.addLayout(title_layout)
        main_layout.addLayout(location_layout)
        main_layout.addLayout(people_layout)
        main_layout.addLayout(layout_extras)

        bottom_row_layout = QHBoxLayout()
        bottom_row_layout.addWidget(date_group_box)

        group_box_sort = QGroupBox("Sırala")
        group_box_sort.setFixedHeight(100)
        layout_sort_primary = QHBoxLayout()
        label_sort_primary = QLabel("Birincil:")
        label_sort_primary.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.dropdown_sort_primary = QComboBox()
        self.dropdown_sort_primary.addItems(["Tarih", "Başlık", "Yer", "Tür", "Kişiler", "Uzantı"])
        self.dropdown_sort_primary.setFixedWidth(80)
        layout_sort_primary.addWidget(label_sort_primary)
        layout_sort_primary.addWidget(self.dropdown_sort_primary)

        layout_sort_secondary = QHBoxLayout()
        label_sort_secondary = QLabel("İkincil:")
        label_sort_secondary.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.dropdown_sort_secondary = QComboBox()
        self.dropdown_sort_secondary.addItems(["Tarih", "Başlık", "Yer", "Tür", "Kişiler", "Uzantı"])
        self.dropdown_sort_secondary.setFixedWidth(80)
        layout_sort_secondary.addWidget(label_sort_secondary)
        layout_sort_secondary.addWidget(self.dropdown_sort_secondary)

        layout_sort = QVBoxLayout()
        layout_sort.addLayout(layout_sort_primary)
        layout_sort.addLayout(layout_sort_secondary)
        group_box_sort.setLayout(layout_sort)

        self.clear_button = QPushButton("Süzmeyi Temizle")
        self.clear_button.setFixedSize(150, 40)
        self.search_button = QPushButton("Süz")
        self.search_button.setFixedSize(150, 40)

        layout_bottom_right = QVBoxLayout()
        layout_bottom_right.addWidget(group_box_sort)
        layout_bottom_right.addWidget(self.clear_button, alignment=Qt.AlignBottom)
        layout_bottom_right.addWidget(self.search_button, alignment=Qt.AlignBottom)

        bottom_row_layout.addLayout(layout_bottom_right)
        main_layout.addLayout(bottom_row_layout)

        self.setLayout(main_layout)

    def toggle_date_range(self, state):
        """Enable or disable the end date based on the checkbox state."""
        self.date_end.setEnabled(state == Qt.Checked)

    def toggle_additional_date_filters(self, state):
        """Enable or disable the additional date filters based on the checkbox state."""
        enabled = state == Qt.Checked
        self.days_input.setEnabled(enabled)
        self.months_input.setEnabled(enabled)
        self.years_input.setEnabled(enabled)
        self.days_of_week_input.setEnabled(enabled)

    def toggle_people_count_range(self, state):
        """Enable or disable the max people count based on the checkbox state."""
        self.people_count_max.setEnabled(state == Qt.Checked)

    def get_title(self):
        return turkish_upper(self.title_input.text().strip())

    def get_location(self):
        return turkish_upper(self.location_input.text().strip())

    def get_people(self):
        return self.people_input.text().strip()

    def get_days(self):
        if self.additional_date_filters_checkbox.isChecked():
            return self.days_input.text().strip()
        return ""

    def get_months(self):
        if self.additional_date_filters_checkbox.isChecked():
            return self.months_input.text().strip()
        return ""

    def get_years(self):
        if self.additional_date_filters_checkbox.isChecked():
            return self.years_input.text().strip()
        return ""

    def get_days_of_week(self):
        if self.additional_date_filters_checkbox.isChecked():
            return self.days_of_week_input.text().strip()
        return ""

    def get_date_range(self):
        if self.date_range_checkbox.isChecked():
            return self.date_start.text().strip(), self.date_end.text().strip()
        return self.date_start.text().strip(), ""

    def get_people_count_range(self):
        if self.people_count_range_checkbox.isChecked():
            if self.people_count_min.text().isdigit():
                count_min = int(self.people_count_min.text())
                if self.people_count_max.text().isdigit():
                    count_max = int(self.people_count_max.text())
                    return count_min, count_max
                return count_min, -1
            return -1, -1
        else:
            if self.people_count_min.text().isdigit():
                count_min = int(self.people_count_min.text())
                return count_min, -1
            return -1, -1

    def get_file_type(self):
        return int(self.type_dropdown.currentIndex())

    def get_ext(self):
        return self.extension_input.text().strip()

    def get_tags(self):
        return self.tags_input.text().strip()

    def get_sort(self):
        return int(self.dropdown_sort_primary.currentIndex()), int(self.dropdown_sort_secondary.currentIndex())
