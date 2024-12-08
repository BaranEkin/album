import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QInputDialog
)
from PyQt5.QtGui import QIcon
from gui.message import show_message
from data.media_list_manager import MediaListManager

class DialogLists(QDialog):
    def __init__(self, media_list_manager: MediaListManager, title="Listeler", inital_selection=None):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("res/icons/Layout-Window-25--Streamline-Sharp-Gradient-Free.png"))
        self.setFixedSize(350, 250)

        self.media_list_manager = media_list_manager

        # Main layout
        self.layout = QVBoxLayout()

        self.elements = self.media_list_manager.get_media_list_names()
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.elements)
        self.layout.addWidget(self.list_widget)
        self.selected_element = inital_selection if self.select_by_text(inital_selection) else None

        # Add/Delete buttons
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Ekle")
        self.add_button.setFixedWidth(50)
        self.add_button.setIcon(QIcon("res/icons/Add--Streamline-Material-Pro.png"))
        self.delete_button = QPushButton("Sil")
        self.delete_button.setFixedWidth(50)
        self.delete_button.setIcon(QIcon("res/icons/Remove--Streamline-Material-Pro.png"))
        self.delete_button.setEnabled(False)  # Initially disabled
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addStretch()  # Push buttons to the left
        self.layout.addLayout(self.button_layout)

        # OK and Clear buttons
        self.dialog_button_layout = QHBoxLayout()
        self.clear_button = QPushButton("Seçimi Temizle")
        self.ok_button = QPushButton("Seç")
        self.dialog_button_layout.addStretch()  # Push buttons to the right
        self.dialog_button_layout.addWidget(self.clear_button)
        self.dialog_button_layout.addWidget(self.ok_button)
        self.layout.addLayout(self.dialog_button_layout)

        # Set layout
        self.setLayout(self.layout)

        # Connect signals
        self.add_button.clicked.connect(self.add_element)
        self.delete_button.clicked.connect(self.delete_element)
        self.list_widget.itemSelectionChanged.connect(self.update_buttons)
        self.clear_button.clicked.connect(self.clear_selection)
        self.ok_button.clicked.connect(self.on_accept)

    def add_element(self):
        text, ok = QInputDialog.getText(self, "Liste Ekle", "Liste adı girin:")
        text = text.strip()
        if ok and text:
            if text in self.elements:
                show_message("Aynı adda bir liste zaten var!", level="error")
                return
            self.list_widget.addItem(text)
            self.elements.append(text)
            self.media_list_manager.create_media_list(list_name=text)

    def delete_element(self):
        if show_message("Listeyi kalıcı olarak silmek istediğinizden emin misiniz?", is_question=True):
            selected_items = self.list_widget.selectedItems()
            for item in selected_items:
                self.elements.remove(item.text())
                self.list_widget.takeItem(self.list_widget.row(item))
                self.media_list_manager.delete_media_list(list_name=item.text())
            self.clear_selection()

    def update_buttons(self):
        has_selection = bool(self.list_widget.selectedItems())
        self.delete_button.setEnabled(has_selection)

    def clear_selection(self):
        # Clear the selection in the list
        self.list_widget.clearSelection()
        self.selected_element = None
        self.update_buttons()  # Update button states

    def on_accept(self):
        # Get the selected element and close the dialog
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            self.selected_element = selected_items[0].text()
        self.accept()  # Close the dialog

    def select_by_text(self, text):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.text() == text:
                self.list_widget.setCurrentItem(item)
                return True
        return False 
