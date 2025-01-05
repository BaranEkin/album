from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QLineEdit,
)
from PyQt5.QtGui import QIcon


class DialogExportMedia(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Medyaları Dışa Aktar")
        self.setWindowIcon(QIcon("res/icons/Align-Front-1--Streamline-Core-Gradient.png"))
        self.setFixedSize(400, 100)

        # Main Layout
        self.layout = QVBoxLayout(self)

        # Horizontal Layout for Label, Line Edit, and Button
        self.folder_layout = QHBoxLayout()

        self.label = QLabel("Aktarılacak Klasör:")
        self.folder_line_edit = QLineEdit()
        self.folder_line_edit.setReadOnly(True)
        self.browse_button = QPushButton()
        self.browse_button.setIcon(QIcon("res/icons/Folder-Search-2--Streamline-Lucide.png"))
        self.browse_button.clicked.connect(self.browse_folder)

        self.folder_layout.addWidget(self.label)
        self.folder_layout.addWidget(self.folder_line_edit)
        self.folder_layout.addWidget(self.browse_button)

        self.layout.addLayout(self.folder_layout)

        # Ok and Cancel Buttons
        self.button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Dışa Aktar")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)
        self.cancel_button = QPushButton("Vazgeç")
        self.cancel_button.clicked.connect(self.reject)

        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.ok_button)
        
        self.layout.addLayout(self.button_layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if folder:
            # Convert the path to use forward slashes
            folder = folder.replace("\\", "/")
            self.folder_line_edit.setText(folder)
            self.ok_button.setEnabled(True)

    def get_selected_folder_path(self):
        return self.folder_line_edit.text() if self.result() == QDialog.Accepted else None
