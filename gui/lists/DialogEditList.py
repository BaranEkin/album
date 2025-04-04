from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QIcon
from gui.DialogReorder import DialogReorder
from gui.message import show_message


class DialogEditList(DialogReorder):
    def __init__(
        self, media_loader, media_list_manager, list_name, list_names, parent=None
    ):
        self.media_loader = media_loader
        self.media_list_manager = media_list_manager
        self.list_name = list_name
        self.list_names = list_names

        self.thumbnail_keys = [
            f"{uuid}.jpg"
            for uuid in self.media_list_manager.get_uuids_from_list(self.list_name)
        ]

        super().__init__(
            thumbnail_keys=self.thumbnail_keys, media_loader=self.media_loader
        )

        self.setWindowTitle("Listeyi Düzenle")
        self.setFixedSize(260, 600)
        self.setWindowIcon(QIcon("res/icons/Edit--Streamline-Mynaui.png"))

        self.input_name = QLineEdit(self.list_name)
        self.main_layout.insertWidget(0, self.input_name)

        self.ok_button.clicked.disconnect(self.accept)
        self.ok_button.clicked.connect(self.on_ok_button_clicked)

    def get_name(self):
        return self.input_name.text().strip()

    def on_ok_button_clicked(self):
        new_name = self.get_name()
        if new_name == self.list_name or new_name not in self.list_names:
            self.accept()
        else:
            show_message(
                "Aynı adda bir liste zaten var. Başka bir ad girin.", level="warning"
            )
