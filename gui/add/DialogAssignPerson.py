from PyQt5.QtWidgets import (QDialog, QVBoxLayout,
                             QListWidget, QDialogButtonBox,
                             QLineEdit, QListWidgetItem)

from gui.constants import Constants


class DialogAssignPerson(QDialog):
    def __init__(self, person, people_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(Constants.WINDOW_DIALOG_ASSIGN_PERSON)

        # Layout for the dialog
        layout = QVBoxLayout(self)

        # Mock-up list of names for the list widget
        self.people_list = people_list

        # Create the input field
        self.input_field = QLineEdit(self)
        self.input_field.setText(f"{person}")
        layout.addWidget(self.input_field)

        # Create the scrollable list widget for showing suggestions
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        # Populate the list widget with all names initially
        self.update_list_widget()

        # Connect the input field's text changes to the filtering function
        self.input_field.textEdited.connect(self.update_list_widget)

        # OK and Close buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accepted)
        layout.addWidget(button_box)

        # Handle item click in the list to set it in the input field
        self.list_widget.itemClicked.connect(self.set_selected_name)

    def update_list_widget(self):
        """Update the list widget based on the input text."""
        # Clear the current list
        self.list_widget.clear()

        # Get the current text from the input field
        text = self.input_field.text()

        # Filter names based on a case-sensitive substring match
        filtered_names = [name for name in self.people_list if text in name]

        # Add the filtered names to the list widget
        for name in filtered_names:
            self.list_widget.addItem(QListWidgetItem(name))

    def set_selected_name(self, item):
        """Set the selected name from the list into the input field."""
        self.input_field.setText(item.text())

    def accepted(self):
        self.accept()
