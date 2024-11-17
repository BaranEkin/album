import re
from datetime import datetime

from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout,
                             QTreeView, QListWidget, QFrame, QFileSystemModel)
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QIcon
from PIL import Image

from logger import log
from media_loader import MediaLoader
from data.helpers import is_valid_people
from gui.message import show_message
from gui.add.LabelImageAdd import LabelImageAdd
from gui.add.FrameAddInfo import FrameAddInfo
from gui.add.FrameAction import FrameAction
from gui.add.DialogUpload import DialogUpload
from gui.add.DialogAddMedia import DialogAddMedia
from data.data_manager import DataManager
from data.orm import Media

import face_detection
from ops import file_ops

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
        # self.frame_action.button_upload.clicked.connect(self.on_media_edit)

        self.setWindowTitle("Medya Düzenleme")
        self.setWindowIcon(QIcon("res/icons/Pencil-Square--Streamline-Plump-Gradient.png"))

        self.selected_media_path = self.media_loader.get_media_path(self.media.media_uuid, self.media.extension)
        if self.media.people_detect:
            self.detections_with_names = face_detection.build_detections_with_names(self.media.people_detect, self.media.people)
        
        self.set_media_info()

        if self.media.type == 1:
            self.frame_add_info.set_people_enable(False)
            self.draw_identifications()
            self.image_label.detections_with_names = self.detections_with_names
            self.image_label.set_image("temp/detections.jpg")
        
        else:
            self.image_label.clear()
            self.frame_add_info.set_people_enable(True)

    def set_media_info(self):
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
