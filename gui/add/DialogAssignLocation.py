from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QDialogButtonBox,
    QLineEdit,
    QListWidgetItem,
)

from gui.constants import Constants
from data.helpers import turkish_lower


class DialogAssignLocation(QDialog):
    def __init__(self, location, location_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(Constants.WINDOW_DIALOG_ASSIGN_LOCATION)
        self.setFixedSize(550, 250)

        # Layout for the dialog
        layout = QVBoxLayout(self)
        self.location_list = location_list

        # Create the input field
        self.input_field = QLineEdit(self)
        self.input_field.setText(f"{location}")
        layout.addWidget(self.input_field)

        # Create the scrollable list widget for showing suggestions
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        # Populate the list widget with all locations initially
        self.update_list_widget()

        # Connect the input field's text changes to the filtering function
        self.input_field.textEdited.connect(self.update_list_widget)

        # OK and Close buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accepted)
        layout.addWidget(button_box)

        # Handle item click in the list to set it in the input field
        self.list_widget.itemClicked.connect(self.set_selected_location)

    def update_list_widget(self):
        """Update the list widget based on the input text."""
        # Clear the current list
        self.list_widget.clear()

        # Get the current text from the input field
        text = self.input_field.text()

        # Filter names based on a case-insensitive substring match
        filtered_locations = [
            loc
            for loc in self.location_list
            if turkish_lower(text) in turkish_lower(loc)
        ]

        # Add the filtered locations to the list widget
        for loc in filtered_locations:
            self.list_widget.addItem(QListWidgetItem(loc))

    def set_selected_location(self, item):
        """Set the selected name from the list into the input field."""
        self.input_field.setText(item.text())

    def accepted(self):
        self.accept()
