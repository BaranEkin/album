import os
from datetime import datetime

from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout,
                             QTreeView, QListWidget, QFrame, QFileSystemModel)
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QIcon
from PIL import Image

from logger import log
from data.helpers import is_valid_people
from gui.message import show_message
from gui.add.LabelImageAdd import LabelImageAdd
from gui.add.FrameAddInfo import FrameAddInfo
from gui.add.FrameAction import FrameAction
from gui.add.DialogUpload import DialogUpload
from data.data_manager import DataManager

import face_detection
from ops import file_ops


class DialogAddMedia(QDialog):
    def __init__(self, data_manager: DataManager):
        super().__init__()

        self.data_manager = data_manager
        self.people_list = self.data_manager.get_list_people()
        self.album_list = self.data_manager.get_all_album_paths_with_tags()
        self.locations_list = self.data_manager.get_list_locations()
        self.media_to_be_uploaded = []
        self.media_data_to_be_uploaded = []
        self.media_paths_to_be_uploaded = []
        self.media_paths_uploaded = []

        self.selected_media_path = ""
        self.detections_with_names = []

        self.setFixedSize(1350, 900)

        # Main layout of the dialog (horizontal layout for the 3 frames)
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)

        # Create left frame: frame_navigation
        self.frame_navigation = QFrame(self)
        self.frame_navigation.setFixedWidth(250)  # Set fixed width for frame_navigation
        self.frame_navigation_layout = QVBoxLayout(self.frame_navigation)
        self.frame_navigation.setContentsMargins(0, 0, 0, 0)

        # Create and set up the folder tree view
        self.folder_tree = QTreeView(self.frame_navigation)
        self.file_system_model = QFileSystemModel(self.folder_tree)
        self.file_system_model.setRootPath("")  # Set the root path to show the entire filesystem
        self.file_system_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)  # Show only directories

        self.folder_tree.setModel(self.file_system_model)
        self.folder_tree.setRootIndex(self.file_system_model.index(""))
        self.folder_tree.setColumnWidth(0, 250)

        # Create the scrollable list widget for media files
        self.media_list = QListWidget(self.frame_navigation)

        # Add tree and list widgets to the frame_navigation layout
        self.frame_navigation_layout.addWidget(self.folder_tree)
        self.frame_navigation_layout.addWidget(self.media_list)

        # Add the frame_navigation to the main layout
        main_layout.addWidget(self.frame_navigation)

        # Create middle frame: frame_media
        self.frame_media = QFrame(self)
        self.frame_media.setFixedWidth(800)
        self.frame_media_layout = QVBoxLayout(self.frame_media)
        self.frame_media.setContentsMargins(0, 0, 0, 0)

        # Create the clickable image label (top part of frame_media)
        self.image_label = LabelImageAdd(self.people_list, parent=self.frame_media)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedHeight(500)
        self.frame_media_layout.addWidget(self.image_label)

        # Create the frame_details (bottom part of frame_media)
        self.frame_add_info = FrameAddInfo(locations=self.locations_list, parent=self)
        self.frame_add_info.setFixedHeight(350)
        self.frame_add_info.setFrameStyle(QFrame.StyledPanel)
        self.frame_add_info.radio_date_from_filename.toggled.connect(self.set_auto_date)
        self.frame_add_info.radio_date_from_filedate.toggled.connect(self.set_auto_date)
        self.frame_media_layout.addWidget(self.frame_add_info)

        # Add the frame_media to the main layout
        main_layout.addWidget(self.frame_media)

        # Create right frame: frame_action
        self.frame_action = FrameAction(self.album_list, parent=self)
        self.frame_action.button_add.clicked.connect(self.on_media_add)
        self.frame_action.button_upload.clicked.connect(self.on_media_upload)
        self.frame_action.setFixedWidth(250)
        main_layout.addWidget(self.frame_action)

        # Set the layout for the dialog
        self.setLayout(main_layout)
        self.setWindowTitle("Medya Ekleme")
        self.setWindowIcon(QIcon("res/icons/Image--Add.png"))

        # Connect the tree view selection change to update the media list
        self.folder_tree.selectionModel().selectionChanged.connect(self.on_folder_selected)

        # Connect the media list item click to print the file path
        self.media_list.itemClicked.connect(self.on_media_selected)

        # Variable to store the current folder path
        self.current_folder_path = ""

    def on_folder_selected(self):
        # Get the currently selected folder
        index = self.folder_tree.selectionModel().currentIndex()
        folder_path = self.file_system_model.filePath(index)
        self.current_folder_path = folder_path  # Store the current folder path

        # Clear the media list and image label
        self.media_list.clear()
        self.image_label.clear()

        # Define the media file extensions
        image_extensions = [".png", ".jpg", ".jpeg"]
        video_extensions = [".mp4", ".avi", ".mov", ".mpg", ".wmv", ".3gp", ".asf"]
        sound_extensions = [".mp3", ".wav"]

        # List files from the selected directory and filter for images and videos
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                # Exclude already selected paths
                if file_path not in self.media_paths_to_be_uploaded + self.media_paths_uploaded:

                    if os.path.isfile(file_path):
                        if any(file_name.lower().endswith(ext) for ext in
                               image_extensions + video_extensions + sound_extensions):
                            self.media_list.addItem(file_name)

    def on_media_selected(self, item):

        self.clear_fields_for_new_media()

        media_file_name = item.text()
        self.selected_media_path = os.path.join(self.current_folder_path, media_file_name)

        self.set_auto_date()

        # Selected media is an image
        if file_ops.get_file_type(self.selected_media_path) == 1:

            self.frame_add_info.set_people_enable(False)
            self.detect_people()
            self.draw_identifications()
            self.image_label.set_image("temp/detections.jpg")

        # Selected media is a video
        else:
            self.image_label.clear()
            self.frame_add_info.set_people_enable(True)
            file_ops.open_with_default_app(self.selected_media_path)

    def select_next_media(self):
        next_row = self.media_list.currentRow() + 1
        if next_row < self.media_list.count():
            self.media_list.setCurrentRow(next_row)
            next_item = self.media_list.item(next_row)
            self.on_media_selected(next_item)

    def detect_people(self):
        image = Image.open(self.selected_media_path)
        self.detections_with_names = face_detection.detect_people(image)
        self.image_label.detections_with_names = self.detections_with_names

    def draw_identifications(self):
        image = Image.open(self.selected_media_path)
        image = face_detection.draw_identifications(image, self.detections_with_names)
        image = image.convert("RGB")
        image.save("temp/detections.jpg")

    def update_identifications(self, detections_with_names):
        self.detections_with_names = face_detection.preprocess_detections(detections_with_names)
        self.draw_identifications()
        self.frame_add_info.set_people(self.get_people())
        self.image_label.set_image("temp/detections.jpg")

    def get_people_detect(self):
        people_detect = ",".join(['-'.join(map(str, det[:4])) for det in self.detections_with_names if det[4] != ""])
        return people_detect

    def get_people(self):
        people = ",".join([det[4] for det in self.detections_with_names if det[4] != ""])
        return people

    def get_people_count(self):
        return len([det for det in self.detections_with_names if det[4] != ""])

    def on_media_add(self):

        self.frame_action.set_button_add_enabled(False)
        media_data = self.get_media_data()
        if not media_data:
            self.frame_action.set_button_add_enabled(True)
            return

        self.media_paths_to_be_uploaded.append(self.selected_media_path)
        self.media_data_to_be_uploaded.append(media_data)

        self.on_folder_selected()
        self.select_next_media()

        self.frame_action.update_button_upload(len(self.media_data_to_be_uploaded))
        self.frame_action.set_button_add_enabled(True)

    def get_media_data(self):
        
        media_data = {
            "media_path": self.selected_media_path,
            "topic": self.frame_add_info.get_topic(),
            "title": self.frame_add_info.get_title(),
            "location": self.frame_add_info.get_location(),
            "date_text": self.frame_add_info.get_date(),
            "date_est": self.frame_add_info.get_date_est(),
            "tags": self.frame_add_info.get_tags(),
            "notes": self.frame_add_info.get_notes(),
            "people": self.get_people(),
            "people_detect": self.get_people_detect(),
            "people_count": self.get_people_count(),
            "albums": "".join(self.frame_action.get_selected_album_tags()),
        }

        media_path = media_data["media_path"]
        if not media_path:
            log("DialogAddMedia.get_media_data", f"Media path '{media_path}' is falsy.", level="warning")
            show_message("Medya dosyası seçilmedi. Lütfen bir medya dosyası seçin.", level="warning")
            return None

        topic = media_data["topic"]
        title = media_data["title"]

        if not (title or topic):
            log("DialogAddMedia.get_media_data", f"Both topic '{topic}' and title {title} are falsy.", level="warning")
            show_message("Konu ile başlık alanlarından en az bir tanesini doldurmak zorunludur.", level="warning")
            return None
        
        location = media_data["location"]
        if not location:
            log("DialogAddMedia.get_media_data", f"Location '{location}' is falsy.", level="warning")
            show_message("Yer alanını doldurmak zorunludur. Lütfen bir yer girin.", level="warning")
            return None
        
        date_text = media_data["date_text"]
        try:
            # Try parsing date as "DD.MM.YYYY"
            _ = datetime.strptime(date_text, "%d.%m.%Y").strftime("%d.%m.%Y")
        except ValueError as e:
            log("DialogAddMedia.get_media_data", f"Date '{date_text}' is incorrectly formatted.", level="warning")
            show_message("Lütfen tarih alanını GG.AA.YYYY formatında girin.", level="warning")
            return None

        people = media_data["people"]
        if people:
            if not is_valid_people(people):
                people_log = people.replace("\n", "\\n")
                log("DialogAddMedia.get_media_data", f"People '{people_log}' is incorrectly formatted.", level="warning")
                show_message("Kişiler alanını formatı hatalı. Şunlara dikkat edin:\nNoktalama işaretleri, semboller veya rakamlar kullanmayın.\nHer satıra bir kişi girin.\nİsimlerin baş harflerini ve soyisimlerin tüm harflerini büyük yazın.", level="warning")
                return None
        
        return media_data
            

    def on_media_upload(self):

        self.frame_action.set_button_add_enabled(False)
        self.frame_action.set_button_upload_enabled(False)

        for media_data in self.media_data_to_be_uploaded:
            media = self.data_manager.build_media(
                path=media_data["media_path"],
                topic=media_data["topic"],
                title=media_data["title"],
                location=media_data["location"],
                date_text=media_data["date_text"],
                date_est=media_data["date_est"],
                albums=media_data["albums"],
                tags=media_data["tags"],
                notes=media_data["notes"],
                people=media_data["people"],
                people_detect=media_data["people_detect"],
                people_count=media_data["people_count"],
                private=0
            )

            self.media_to_be_uploaded.append(media)

        assert len(self.media_paths_to_be_uploaded) == len(self.media_to_be_uploaded)

        dialog_upload = DialogUpload(
            self.media_paths_to_be_uploaded,
            self.media_to_be_uploaded,
            self.data_manager
        )

        if dialog_upload.exec_() == QDialog.Accepted:
            self.media_paths_uploaded.extend(self.media_paths_to_be_uploaded)
            self.media_paths_to_be_uploaded = []
            self.media_data_to_be_uploaded = []

        self.media_to_be_uploaded = []
        self.clear_fields_for_new_media()

        self.select_next_media()

        self.frame_action.set_button_add_enabled(True)
        self.frame_action.update_button_upload(0)

    def clear_fields_for_new_media(self):
        self.frame_add_info.set_people("")

        if self.frame_add_info.get_date_option() != 3:
            self.frame_add_info.set_date("")

    def clear_all_fields(self):
        self.frame_add_info.set_title("")
        self.frame_add_info.set_location("")
        self.frame_add_info.set_date("")
        self.frame_add_info.set_date_est(7)
        self.frame_add_info.set_people("")
        self.frame_add_info.set_notes("")
        self.frame_add_info.set_tags("")
        self.frame_action.clear_selected_album_tags()

    def set_auto_date(self):
        date_option = self.frame_add_info.get_date_option()
        if date_option == 1:
            auto_date = file_ops.get_date_from_filename(self.selected_media_path)
            self.frame_add_info.set_date(auto_date)
            self.frame_add_info.set_date_est(7)

        elif date_option == 2:
            auto_date = file_ops.get_date_from_file_metadata(self.selected_media_path)
            self.frame_add_info.set_date(auto_date)
            self.frame_add_info.set_date_est(7)
