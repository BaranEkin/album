from PyQt5.QtWidgets import ( QDialog, QVBoxLayout, 
                             QListWidget, QDialogButtonBox, 
                             QLineEdit, QListWidgetItem)



class DialogAssignPerson(QDialog):
    def __init__(self, person, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kişiyi ekle...")

        # Layout for the dialog
        layout = QVBoxLayout(self)

        # Mock-up list of names for the list widget
        self.name_list = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']

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

        # Filter names based on a case-insensitive substring match
        filtered_names = [
            name for name in self.name_list
            if text.lower() in name.lower()
        ]

        # Add the filtered names to the list widget
        for name in filtered_names:
            self.list_widget.addItem(QListWidgetItem(name))

    def set_selected_name(self, item):
        """Set the selected name from the list into the input field."""
        self.input_field.setText(item.text())

    def accepted(self):
        # Print the input field value when OK is pressed
        print(f"Person entered: {self.input_field.text()}")
        self.accept()