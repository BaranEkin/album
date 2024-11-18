import re
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

from logger import log
from media_loader import MediaLoader
from data.helpers import is_valid_people
from gui.message import show_message
from gui.main.DialogProcess import DialogProcess
from gui.add.DialogAddMedia import DialogAddMedia
from data.data_manager import DataManager
from data.orm import Media

import face_detection
from ops import cloud_ops

class DialogEditMedia(DialogAddMedia):
    def __init__(self, data_manager: DataManager, media_loader: MediaLoader, media: Media):
        super().__init__(data_manager)

        self.media = media
        self.media_loader = media_loader
        self.setFixedSize(1100, 900)

        self.frame_navigation.hide()
        self.frame_add_info.radio_label.hide()
        self.frame_add_info.radio_date_from_filename.hide()
        self.frame_add_info.radio_date_from_filedate.hide()
        self.frame_add_info.radio_date_fixed.hide()

        self.frame_action.button_add.hide()
        self.frame_action.button_upload.setText("DEĞİŞİKLİKLERİ KAYDET")
        self.frame_action.button_upload.setEnabled(True)
        self.frame_action.button_upload.clicked.disconnect(self.on_media_upload)
        self.frame_action.button_upload.clicked.connect(self.on_media_edit)
        

        self.setWindowTitle("Medya Düzenleme")
        self.setWindowIcon(QIcon("res/icons/Pencil-Square--Streamline-Plump-Gradient.png"))

        self.selected_media_path = self.media_loader.get_media_path(self.media.media_uuid, self.media.extension)
        if self.media.people_detect:
            self.detections_with_names = face_detection.build_detections_with_names(self.media.people_detect, self.media.people)
        
        self.set_media_data()

        if self.media.type == 1:
            self.frame_add_info.set_people_enable(False)
            self.draw_identifications()
            self.image_label.detections_with_names = self.detections_with_names
            self.image_label.set_image("temp/detections.jpg")
        
        else:
            self.image_label.clear()
            self.frame_add_info.set_people_enable(True)

    def set_media_data(self):
        self.frame_add_info.set_topic(self.media.topic or "")
        self.frame_add_info.set_title(self.media.title or "")
        self.frame_add_info.set_location(self.media.location)
        self.frame_add_info.set_date(self.media.date_text)
        self.frame_add_info.set_date_est(self.media.date_est)
        self.frame_add_info.set_notes(self.media.notes or "")
        self.frame_add_info.set_tags(self.media.tags or "")
        self.frame_add_info.set_people(self.media.people or "")
        if self.media.albums:
            album_tags = re.findall(r'a\d{2}', self.media.albums)
            self.frame_action.set_selected_album_tags(album_tags)

    def on_media_edit(self):
        
        connected = cloud_ops.check_s3()
        if not connected:
            pass

        self.frame_action.button_upload.setEnabled(False)
        media_data = self.get_media_data()
        media = Media()

        
        # Unmodifiable fields
        media.media_uuid = self.media.media_uuid
        media.created_by = self.media.created_by
        media.created_at = self.media.created_at
        media.extension = self.media.extension
        media.type = self.media.type
        media.rank = self.media.rank
        media.private = self.media.private
        
        # Modifiable fields
        media.topic = media_data["topic"]
        media.title = media_data["title"]
        media.location = media_data["location"]
        media.date_text = media_data["date_text"]
        media.date_est = media_data["date_est"]
        media.albums=media_data["albums"]
        media.tags=media_data["tags"]
        media.notes=media_data["notes"]
        media.people=media_data["people"]
        media.people_detect=media_data["people_detect"]
        media.people_count=media_data["people_count"]

        edit_dialog = DialogProcess(operation=self.edit_procedure,
                                    operation_args=(media,),
                                    title="Medya Düzenleme İşlemi",
                                    message="Medya düzenleme işlemi devam ediyor")
        
        if edit_dialog.exec_() == QDialog.Accepted:
            self.frame_action.button_upload.setEnabled(True)
            self.accept()

    def edit_procedure(self, media: Media):
        self.data_manager.update_local_db()
        self.data_manager.edit_media(media)
        cloud_ops.upload_database()
