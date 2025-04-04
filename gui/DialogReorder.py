from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from gui.main.ListModelThumbnail import ListModelThumbnail, ThumbnailDelegate


class DialogReorder(QDialog):
    def __init__(self, thumbnail_keys, media_loader, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Yeniden Sırala")
        self.setModal(True)
        self.setFixedSize(220, 600)
        self.setWindowIcon(QIcon("res/icons/Menu-Order--Streamline-Tabler.png"))

        # Variables
        self.thumbnail_keys = thumbnail_keys
        self.media_loader = media_loader

        # Layouts
        self.main_layout = QVBoxLayout(self)

        # Thumbnail ListView
        self.thumbnail_list = QListView(self)
        self.thumbnail_list.setSpacing(1)
        self.thumbnail_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.thumbnail_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.thumbnail_list)

        # Thumbnail Model
        self.thumbnail_model = ListModelThumbnail(
            self.thumbnail_keys, self.media_loader, is_reorder=True, parent=self
        )
        self.thumbnail_list.setModel(self.thumbnail_model)
        self.thumbnail_list.setDragDropMode(QListView.InternalMove)
        self.thumbnail_list.setDefaultDropAction(Qt.MoveAction)
        self.thumbnail_list.setSelectionMode(QListView.SingleSelection)
        self.thumbnail_list.setItemDelegate(ThumbnailDelegate(is_reorder=True))

        # Buttons
        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Kaydet", self)
        self.cancel_button = QPushButton("Vazgeç", self)

        # Button Connections
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.ok_button)

        self.main_layout.addLayout(self.button_layout)

    def get_reordered_keys(self):
        """Return the reordered thumbnail keys."""
        return self.thumbnail_model.thumbnail_keys
