import sys
from typing import Literal
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QInputDialog, QFrame, QLabel, QComboBox
)
from PyQt5.QtGui import QIcon
from gui.message import show_message
from data.media_list_manager import MediaListManager

class DialogLists(QDialog):
    def __init__(self, media_list_manager: MediaListManager, inital_selection=None, mode: Literal["get", "add"] = "get"):
        super().__init__()
        
        if mode == "get":
            title = "Listeler"
            label_ok_button = "Getir"
        
        else: # mode == "add"
            title = "Listeye Ekle"
            label_ok_button = "Listeye Ekle"

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon("res/icons/Layout-Window-25--Streamline-Sharp-Gradient-Free.png"))
        self.setFixedSize(350, 250)

        self.media_list_manager = media_list_manager
        self.selected_sorting = 0

        # Main layout
        self.layout = QVBoxLayout()

        self.elements = self.media_list_manager.get_media_list_names()
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.elements)
        self.layout.addWidget(self.list_widget)
        self.selected_element = inital_selection if self.select_by_text(inital_selection) else None
        
        # Sorting frame
        self.layout_sorting = QHBoxLayout()
        self.label_sorting = QLabel("Medya Sıralaması:")
        self.combo_sorting = QComboBox()
        self.combo_sorting.addItems(["Listeye Eklenme", "Tarih", "Başlık", "Yer", "Tür", "Kişiler", "Uzantı"])
        self.combo_sorting.currentIndexChanged.connect(self.update_sorting)
        self.layout_sorting.addWidget(self.label_sorting)
        self.layout_sorting.addWidget(self.combo_sorting)

        # Add/Delete/Edit buttons
        self.layout_middle = QHBoxLayout()
        self.button_add = QPushButton()
        self.button_add.setFixedWidth(25)
        self.button_add.setIcon(QIcon("res/icons/Add--Streamline-Material-Pro.png"))
        self.button_add.setToolTip("Yeni liste ekle")
        self.button_delete = QPushButton()
        self.button_delete.setFixedWidth(25)
        self.button_delete.setIcon(QIcon("res/icons/Remove--Streamline-Material-Pro.png"))
        self.button_delete.setToolTip("Seçili listeyi sil")
        self.button_delete.setEnabled(False)  # Initially disabled
        self.button_edit = QPushButton()
        self.button_edit.setFixedWidth(25)
        self.button_edit.setIcon(QIcon("res/icons/Edit--Streamline-Mynaui.png"))
        self.button_edit.setToolTip("Seçili listeyi yeniden adlandır")
        self.button_edit.setEnabled(False)  # Initially disabled
        self.layout_middle.addWidget(self.button_add)
        self.layout_middle.addWidget(self.button_delete)
        self.layout_middle.addWidget(self.button_edit)
        self.layout_middle.addStretch()  # Push buttons to the left
        if mode == "get":
            self.layout_middle.addLayout(self.layout_sorting)
        self.layout.addLayout(self.layout_middle)

        # OK and Clear buttons
        self.dialog_button_layout = QHBoxLayout()
        self.clear_button = QPushButton("Seçimi Temizle")
        self.clear_button.setFixedSize(100, 30)
        self.ok_button = QPushButton(label_ok_button)
        self.ok_button.setEnabled(False)
        self.ok_button.setFixedSize(100, 30)
        self.dialog_button_layout.addStretch()  # Push buttons to the right
        self.dialog_button_layout.addWidget(self.clear_button)
        self.dialog_button_layout.addWidget(self.ok_button)
        self.layout.addLayout(self.dialog_button_layout)

        # Set layout
        self.setLayout(self.layout)

        # Connect signals
        self.button_add.clicked.connect(self.add_element)
        self.button_delete.clicked.connect(self.delete_element)
        self.button_edit.clicked.connect(self.edit_element)  # Connect Edit button
        self.list_widget.itemSelectionChanged.connect(self.update_buttons)
        self.clear_button.clicked.connect(self.clear_selection)
        self.ok_button.clicked.connect(self.on_accept)

    def update_sorting(self):
        self.selected_sorting = self.combo_sorting.currentIndex()

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

    def edit_element(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            current_name = selected_items[0].text()
            new_name, ok = QInputDialog.getText(self, "Listeyi Yeniden Adlandır", f"Yeni ad girin:", text=current_name)
            new_name = new_name.strip()
            if ok and new_name:
                if new_name == current_name:
                    return  # No change
                if new_name in self.elements:
                    show_message("Aynı adda bir liste zaten var!", level="error")
                    return
                # Update in backend
                self.media_list_manager.rename_media_list(old_name=current_name, new_name=new_name)
                # Update in UI
                self.elements[self.elements.index(current_name)] = new_name
                selected_items[0].setText(new_name)

    def update_buttons(self):
        has_selection = bool(self.list_widget.selectedItems())
        self.ok_button.setEnabled(has_selection)
        self.button_delete.setEnabled(has_selection)
        self.button_edit.setEnabled(has_selection)  # Enable Edit button if an item is selected

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
