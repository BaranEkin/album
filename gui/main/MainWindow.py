import os
import random
import copy
from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QWidget,
    QPushButton,
    QGridLayout,
    QDialog,
    QGroupBox,
    QApplication,
)
from PyQt5.QtCore import Qt, QModelIndex, QSize, QTimer, QItemSelectionModel
from PyQt5.QtGui import QPixmap, QPalette, QKeyEvent, QIcon, QImage
from PIL import Image
from datetime import datetime

from data.display_history_manager import DisplayHistoryManager
from data.media_list_manager import MediaListManager
from gui.DialogReorder import DialogReorder
from gui.add.DialogEditMedia import DialogEditMedia
from gui.constants import Constants
from gui.export.DialogExportMedia import DialogExportMedia
from gui.lists.DialogEditBulk import DialogEditBulk
from gui.lists.DialogLists import DialogLists
from gui.main.DialogProcess import DialogProcess
from gui.main.DialogSettings import DialogSettings
from gui.main.ListViewThumbnail import ListViewThumbnail
from media_loader import MediaLoader
from logger import log
from data.helpers import get_unix_time_days_ago, generate_export_filename
from data.media_filter import MediaFilter
from data.data_manager import DataManager
from gui.message import show_message
from gui.filter.DialogFilter import DialogFilter
from gui.main.FrameBottom import FrameBottom
from gui.main.ListModelThumbnail import ListModelThumbnail, ThumbnailDelegate
from gui.main.LabelImageViewer import LabelImageViewer
from gui.add.DialogAddMedia import DialogAddMedia
from gui.main.DialogPeople import DialogPeople
from gui.main.DialogNotes import DialogNotes
from config.config import Config

import face_detection
from ops import cloud_ops, file_ops


class MainWindow(QMainWindow):
    def __init__(
        self,
        data_manager: DataManager,
        media_list_manager: MediaListManager,
        media_loader: MediaLoader,
        display_history_manager: DisplayHistoryManager,
    ):
        super().__init__()

        # MAIN DATA HANDLERS_______________________________________________________________
        self.data_manager = data_manager
        self.media_list_manager = media_list_manager
        self.media_loader = media_loader
        self.display_history_manager = display_history_manager

        # VARIABLES_________________________________________________________________________
        # Current data
        self.media_data = []
        self.media_index = 0
        self.media_list_name = None
        self.media_filter = None
        self.displayed_media = None
        self.selected_rows = []
        self.forgotten_uuids = []

        # Previous data
        self.previous_media_index = 0
        self.previous_mode_media_index = 0
        self.previous_media_filter = None
        self.previous_mode_media_data = None
        self.previous_mode_media_filter = None

        # State variables
        self.mode = ""
        self.is_first_selection = True  # Flag to track first selection after startup

        # GUI ELEMENTS______________________________________________________________________
        # Set window title and initial dimensions
        self.setWindowTitle("Albüm (v1.2.0)")
        self.setWindowIcon(QIcon("res/icons/album_icon_small.png"))
        self.setGeometry(100, 100, 1280, 720)

        # Main container widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create the layout for the main widget
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create a horizontal layout to hold the left frame and image container
        horizontal_layout = QHBoxLayout()
        main_layout.addLayout(horizontal_layout)

        # Create the frame for the menu on the left side
        self.frame_menu = QFrame()
        self.frame_menu.setFixedWidth(170)
        self.frame_menu.setFrameShape(QFrame.StyledPanel)
        self.frame_menu.setFrameShadow(QFrame.Raised)
        self.frame_menu.setObjectName("menuFrame")  # Set object name for styling

        # Set a layout for the frame_menu
        menu_layout = QVBoxLayout(self.frame_menu)
        # Remove margins for full use of space
        menu_layout.setContentsMargins(5, 5, 5, 5)
        menu_layout.setSpacing(10)
        menu_layout.setAlignment(Qt.AlignTop)

        # Add the menu frame to the horizontal layout
        horizontal_layout.addWidget(self.frame_menu)

        # Create right QFrame with fixed width and height, and add buttons in a grid
        self.frame_features_area = QFrame()
        self.frame_features_area.setFixedWidth(170)
        self.frame_features_area.setFixedHeight(400)
        self.frame_features_area.setObjectName(
            "featuresFrame"
        )  # Set object name for styling

        # Create a grid layout for the buttons inside the right frame
        self.layout_features_area = QVBoxLayout()
        self.layout_features_area.setContentsMargins(0, 0, 10, 0)

        self.group_feature_main = QGroupBox("Ana İşlemler")
        self.group_feature_explore = QGroupBox("Keşfet")
        self.group_feature_displayed = QGroupBox("Görüntülen Medya")
        self.group_feature_selected = QGroupBox("Seçili Medyalar")

        self.layout_group_feature_main = QHBoxLayout()
        self.layout_group_feature_explore = QHBoxLayout()
        self.layout_group_feature_displayed = QGridLayout()
        self.layout_group_feature_selected = QHBoxLayout()

        self.layout_group_feature_main.setContentsMargins(0, 0, 0, 5)
        self.layout_group_feature_main.setSpacing(0)

        self.layout_group_feature_explore.setContentsMargins(0, 0, 0, 5)
        self.layout_group_feature_explore.setSpacing(0)

        self.layout_group_feature_displayed.setContentsMargins(0, 0, 0, 5)
        self.layout_group_feature_displayed.setSpacing(0)

        self.layout_group_feature_selected.setContentsMargins(0, 0, 0, 5)
        self.layout_group_feature_selected.setSpacing(0)

        # FEATURES AREA BUTTONS_____________________________________________________________
        # Features for main
        self.button_upload_media = self.make_feature_button(
            "res/icons/Image--Add.png",
            Constants.TOOLTIP_BUTTON_ADD_MEDIA,
            self.show_add_media_dialog,
        )

        self.button_filter = self.make_feature_button(
            "res/icons/Filter-2--Streamline-Sharp-Gradient--Free.png",
            Constants.TOOLTIP_BUTTON_FILTER,
            self.show_filter_dialog,
        )

        self.button_lists = self.make_feature_button(
            "res/icons/Layout-Window-25--Streamline-Sharp-Gradient-Free.png",
            Constants.TOOLTIP_BUTTON_LISTS,
            self.on_button_lists,
            checkable=True,
        )

        self.layout_group_feature_main.addWidget(self.button_upload_media)
        self.layout_group_feature_main.addWidget(self.button_filter)
        self.layout_group_feature_main.addWidget(self.button_lists)

        # Features for explore
        self.button_latest_media = self.make_feature_button(
            "res/icons/Trending-Content--Streamline-Core-Gradient.png",
            Constants.TOOLTIP_BUTTON_LATEST,
            self.on_latest_media,
            checkable=True,
        )

        self.button_today_in_history = self.make_feature_button(
            "res/icons/Calendar-Jump-To-Date--Streamline-Core-Gradient.png",
            Constants.TOOLTIP_BUTTON_TODAY_IN_HISTORY,
            self.on_today_in_history,
            checkable=True,
        )

        self.button_explore_forgotten = self.make_feature_button(
            "res/icons/Lens--Streamline-Plump-Gradient.png",
            Constants.TOOLTIP_BUTTON_EXPLORE_FORGOTTEN,
            self.on_explore_forgotten,
            checkable=True,
        )

        self.layout_group_feature_explore.addWidget(self.button_latest_media)
        self.layout_group_feature_explore.addWidget(self.button_today_in_history)
        self.layout_group_feature_explore.addWidget(self.button_explore_forgotten)

        # Features for displayed
        # Features for same
        self.button_same_date_location = self.make_feature_button(
            "res/icons/Date--Location.png",
            Constants.TOOLTIP_BUTTON_SAME_DATE_LOCATION,
            self.on_same_date_location,
            checkable=True,
        )

        self.button_same_date = self.make_feature_button(
            "res/icons/Circle-Clock--Streamline-Core-Gradient.png",
            Constants.TOOLTIP_BUTTON_SAME_DATE,
            self.on_same_date,
            checkable=True,
        )

        self.button_same_location = self.make_feature_button(
            "res/icons/Location-Pin-3--Streamline-Sharp-Gradient-Free.png",
            Constants.TOOLTIP_BUTTON_SAME_LOCATION,
            self.on_same_location,
            checkable=True,
        )

        self.layout_group_feature_displayed.addWidget(
            self.button_same_date_location, 0, 0
        )
        self.layout_group_feature_displayed.addWidget(self.button_same_date, 0, 1)
        self.layout_group_feature_displayed.addWidget(self.button_same_location, 0, 2)

        # Features for data
        self.button_edit_media = self.make_feature_button(
            "res/icons/Pencil-Square--Streamline-Plump-Gradient.png",
            Constants.TOOLTIP_BUTTON_EDIT_MEDIA,
            self.show_edit_media_dialog,
        )

        self.button_delete_media = self.make_feature_button(
            "res/icons/Recycle-Bin-2--Streamline-Plump-Gradient.png",
            Constants.TOOLTIP_BUTTON_DELETE_MEDIA,
            self.on_delete_media,
        )

        self.button_open_media = self.make_feature_button(
            "res/icons/Link-Share-2--Streamline-Sharp-Gradient-Free.png",
            Constants.TOOLTIP_BUTTON_OPEN_MEDIA,
            self.on_open_media,
        )

        self.layout_group_feature_displayed.addWidget(self.button_edit_media, 1, 0)
        self.layout_group_feature_displayed.addWidget(self.button_delete_media, 1, 1)
        self.layout_group_feature_displayed.addWidget(self.button_open_media, 1, 2)

        # Features for selected
        self.button_bulk_edit_selected_media = self.make_feature_button(
            "res/icons/Cashing-Check--Streamline-Flex-Gradient.png",
            Constants.TOOLTIP_BUTTON_BULK_EDIT,
            self.on_bulk_edit_selected,
        )

        self.button_export_selected_media = self.make_feature_button(
            "res/icons/Align-Front-1--Streamline-Core-Gradient.png",
            Constants.TOOLTIP_BUTTON_EXPORT,
            self.on_export_selected,
        )

        self.button_add_to_list = self.make_feature_button(
            "res/icons/Layout-Window-25--Streamline-Sharp-Gradient-Free--Add.png",
            Constants.TOOLTIP_BUTTON_ADD_TO_LIST,
            self.add_selection_to_list,
        )

        self.layout_group_feature_selected.addWidget(
            self.button_bulk_edit_selected_media
        )
        self.layout_group_feature_selected.addWidget(self.button_export_selected_media)
        self.layout_group_feature_selected.addWidget(self.button_add_to_list)

        # Set layouts for the group boxes
        self.group_feature_main.setLayout(self.layout_group_feature_main)
        self.group_feature_explore.setLayout(self.layout_group_feature_explore)
        self.group_feature_displayed.setLayout(self.layout_group_feature_displayed)
        self.group_feature_selected.setLayout(self.layout_group_feature_selected)

        # Add group boxes to the main layout
        self.layout_features_area.addWidget(self.group_feature_main)
        self.layout_features_area.addWidget(self.group_feature_explore)
        self.layout_features_area.addWidget(self.group_feature_displayed)
        self.layout_features_area.addWidget(self.group_feature_selected)
        self.frame_features_area.setLayout(self.layout_features_area)
        menu_layout.addWidget(self.frame_features_area)

        # Add stretch to make spacing dynamic
        self.layout_features_area.addStretch()

        # THUMBNAIL LIST AND IMAGE VIEWER____________________________________________________
        self.thumbnail_list = ListViewThumbnail(parent=self)
        self.thumbnail_list.setSpacing(1)
        self.thumbnail_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.thumbnail_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.thumbnail_list.setObjectName(
            "thumbnailList"
        )  # Set object name for styling
        menu_layout.addWidget(self.thumbnail_list)

        # Create the scroll area to display the selected image
        self.scroll_area = QScrollArea()
        horizontal_layout.addWidget(self.scroll_area)
        self.scroll_area.setBackgroundRole(QPalette.Dark)
        self.scroll_area.setVisible(False)
        self.scroll_area.setFocusPolicy(Qt.NoFocus)
        self.scroll_area.setObjectName("imageViewer")  # Set object name for styling

        # Create a ImageViewerLabel for the image and add it to the scroll area
        self.image_label = LabelImageViewer(self.scroll_area, self.media_loader)
        self.image_label.setBackgroundRole(QPalette.Base)
        self.image_label.setScaledContents(True)
        self.scroll_area.setWidget(self.image_label)

        # Center the image_label within the scroll area
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setVisible(True)

        # FRAME BOTTOM______________________________________________________________________
        # Create the frame for information at the bottom
        self.frame_bottom = FrameBottom()
        self.frame_bottom.setFixedHeight(110)
        self.frame_bottom.setFocusPolicy(Qt.NoFocus)
        self.frame_bottom.setObjectName("bottomFrame")  # Set object name for styling

        self.frame_bottom.button_people.clicked.connect(self.on_button_people_clicked)
        self.frame_bottom.button_notes.clicked.connect(self.on_button_notes_clicked)
        self.frame_bottom.button_back.clicked.connect(self.go_to_previous_media)
        self.frame_bottom.button_forward.clicked.connect(self.go_to_next_media)

        self.frame_bottom.button_slideshow.clicked.connect(self.on_slideshow_clicked)
        self.slideshow_timer = QTimer(self)
        self.slideshow_timer.setInterval(5000)
        self.slideshow_timer.timeout.connect(self.run_slideshow)

        # Connect settings button signal
        self.frame_bottom.settings_clicked.connect(self.show_settings_dialog)

        main_layout.addWidget(self.frame_bottom)

        # Apply theme-specific styling
        self.apply_theme_styling()

        # LOAD DATA AND SETUP_______________________________________________________________
        self.update_db()
        self.media_data = self.data_manager.get_all_media()
        self.update_frame_bottom_top_label()
        self.handle_selection_feature_buttons()
        self.update_local_storage_status()

        self.dialog_filter = DialogFilter(self.data_manager, parent=self)

        # POPULATE AND SETUP THUMBNAIL LIST_________________________________________________
        # Create and set the custom model
        thumbnail_keys = [f"{media.media_uuid}.jpg" for media in self.media_data]
        self.thumbnail_model = ListModelThumbnail(
            thumbnail_keys, self.media_loader, parent=self
        )
        self.thumbnail_list.setModel(self.thumbnail_model)

        # Set the custom delegate
        self.thumbnail_list.setItemDelegate(ThumbnailDelegate())

        # Connect the clicked signal to handle item selection
        self.thumbnail_list.clicked.connect(self.on_media_selected)
        self.thumbnail_model.signal.loaded.connect(self.try_select_item)

        self.thumbnail_list.setFocus()

        # LOAD YOLO MODEL FOR FACE DETECTION________________________________________________
        # Warmup detection to load YOLOv8 model
        face_detection.detect_people(Image.new("RGB", (200, 200), color="white"))

    def make_feature_button(self, icon_path, tooltip, function, checkable=False):
        """Make a feature button with an icon, tooltip, and function."""

        button = QPushButton()
        button.setFocusPolicy(Qt.NoFocus)
        button.setFixedSize(50, 50)
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(30, 30))
        button.setText("")
        button.clicked.connect(function)
        button.setToolTip(tooltip)
        if checkable:
            button.setCheckable(True)
        return button

    def update_db(self):
        try:
            if cloud_ops.check_s3():
                success = self.data_manager.update_local_db()
                self.set_cloud_connected(success)
                if not success:
                    show_message(
                        "Veri tabanı güncellenemedi. Yerel veri tabanı kullanılacak.",
                        level="error",
                    )
            else:
                show_message(
                    "Bulut sistemi bağlantısı sağlanamadı. Uygulama çevrimdışı olarak çalışacak.",
                    level="warning",
                )
                self.set_cloud_connected(False)
        except:
            show_message(
                "Veri tabanı güncellenemedi. Yerel veri tabanı kullanılacak.",
                level="error",
            )
            self.set_cloud_connected(False)

    def keyPressEvent(self, event):
        """
        Handle key press events for navigating the thumbnails using the arrow keys.
        """
        if event.key() == Qt.Key_Right:
            self.go_to_next_media()

        elif event.key() == Qt.Key_Left:
            self.go_to_previous_media()

    def handle_feature_buttons(self, from_button, checked):
        group_1 = [
            self.button_lists,
            self.button_latest_media,
            self.button_explore_forgotten,
            self.button_today_in_history,
        ]

        group_2 = [
            self.button_same_date,
            self.button_same_location,
            self.button_same_date_location,
        ]

        if checked:
            from_button.setChecked(True)
            if from_button in group_1:
                for b in group_1:
                    if b != from_button:
                        b.setEnabled(False)
                        b.setChecked(False)
                self.button_filter.setEnabled(False)
                for b in group_2:
                    b.setEnabled(True)

            elif from_button in group_2:
                for b in group_1:
                    b.setEnabled(False)
                self.button_filter.setEnabled(False)

                for b in group_2:
                    if b != from_button:
                        b.setEnabled(False)
                        b.setChecked(False)

        else:
            from_button.setChecked(False)
            if from_button in group_1:
                for b in group_1:
                    b.setEnabled(True)
                for b in group_2:
                    b.setEnabled(True)
                self.button_filter.setEnabled(True)

            elif from_button in group_2:
                for b in group_1:
                    b.setEnabled(b.isChecked())
                if any(b.isChecked() for b in group_1):
                    self.button_filter.setEnabled(False)
                else:
                    self.button_filter.setEnabled(True)
                    for b in group_1:
                        b.setEnabled(True)

                for b in group_2:
                    b.setEnabled(True)

    def try_select_item(self, i=0, attempt=0):
        try:
            # Check if the model has any loaded items
            if self.thumbnail_model.rowCount() > 0:
                # Use the INITIAL_MEDIA_INDEX setting only on first selection after startup
                if i == 0 and attempt == 0 and self.is_first_selection:
                    initial_index = Config.INITIAL_MEDIA_INDEX
                    if (
                        initial_index == Constants.SETTINGS_INITIAL_END
                        and self.thumbnail_model.rowCount() > 0
                    ):
                        i = self.thumbnail_model.rowCount() - 1

                index = self.thumbnail_model.index(i, 0)

                self.thumbnail_list.setCurrentIndex(index)
                self.thumbnail_list.scrollTo(index)
                self.thumbnail_list.setFocus()

                self.thumbnail_list.clicked.emit(index)
        except Exception as e:
            log(
                "MainWindow.try_select_item",
                f"Can't select item '{i}' on attempt {attempt}: {e}",
                level="warning",
            )
            # Determine fallback behavior based on the current attempt
            if attempt == 0:
                # First attempt: initial index (i)
                self.try_select_item(i - 1, attempt=1)
            elif attempt == 1 and i > 0:
                # Second attempt: try i-1
                self.try_select_item(i + 1, attempt=2)
            elif attempt == 2 and i + 1 < self.thumbnail_model.rowCount():
                # Third attempt: try i+1
                self.try_select_item(0, attempt=3)
            elif attempt == 3:
                # Final attempt: try 0
                log(
                    "MainWindow.try_select_item",
                    "All attempts to select an item have failed.",
                    level="error",
                )

    def go_to_next_media(self):
        if self.media_index < len(self.media_data) - 1:
            self.try_select_item(self.media_index + 1)

    def go_to_previous_media(self):
        if self.media_index > 0:
            self.try_select_item(self.media_index - 1)

    def go_to_random_media(self):
        index = random.randint(0, len(self.media_data) - 1)
        self.try_select_item(index)

    def on_button_lists(self, checked):
        if checked:
            self.button_lists.setChecked(not self.button_lists.isChecked())
            dialog = DialogLists(
                media_loader=self.media_loader,
                media_list_manager=self.media_list_manager,
                mode="get",
            )

            if dialog.exec_() == QDialog.Accepted:
                selected_list_name = dialog.selected_element
                selected_sorting = dialog.selected_sorting - 1  # -1 for default sorting

                if selected_list_name:
                    selected_uuids = self.media_list_manager.get_uuids_from_list(
                        selected_list_name
                    )
                    media_from_list = self.data_manager.get_media_by_uuids(
                        selected_uuids, selected_sorting
                    )
                    self.previous_media_index = self.media_index
                    self.update_media_data(media_from_list)
                    self.media_list_name = selected_list_name
                    self.mode = "list"
                    self.handle_feature_buttons(self.button_lists, checked=True)

        else:
            self.media_list_name = None
            self.mode = ""
            self.handle_feature_buttons(self.button_lists, checked=False)
            self.return_to_previous_media_state()

    def on_export_selected(self):
        dialog_export = DialogExportMedia()
        if dialog_export.exec_() == QDialog.Accepted:
            export_folder = dialog_export.get_selected_folder_path()
            procceed = show_message(
                f"Seçili {len(self.selected_rows)} medyayı\n'{export_folder}' klasörüne kopyalamak istediğinize emin misiniz?",
                is_question=True,
            )
            if procceed:
                self.export_selected_media(export_folder)

    def export_selected_media(self, export_folder):
        def export_procedure():
            selected_uuids = [
                self.media_data[row].media_uuid for row in self.selected_rows
            ]
            selected_extensions = [
                self.media_data[row].extension for row in self.selected_rows
            ]
            selected_export_filenames = [
                generate_export_filename(self.media_data[row])
                for row in self.selected_rows
            ]

            for uuid, extension, filename in zip(
                selected_uuids, selected_extensions, selected_export_filenames
            ):
                media_path = self.media_loader.get_media_path(uuid, extension)
                file_ops.copy_file(media_path, os.path.join(export_folder, filename))

        dialog = DialogProcess(
            operation=export_procedure,
            title="Medyaları Dışa Aktar",
            message="Medyalar dışa aktarılıyor...",
        )

        if dialog.exec_() == QDialog.Accepted:
            show_message("Dışa aktarma işlemi tamamlandı.", level="info")
            return
        else:
            show_message("Dışa aktarma tamamlanamadı.", level="warning")

    def on_bulk_edit_selected(self):
        def bulk_edit_procedure(edited_media_list):
            self.data_manager.update_local_db()
            for media in edited_media_list:
                self.data_manager.edit_media(media)
            cloud_ops.upload_database()

        if self.check_cloud_connected():
            selected_media_list = [self.media_data[row] for row in self.selected_rows]
            dialog_edit_bulk = DialogEditBulk(selected_media_list)
            if dialog_edit_bulk.exec_() == QDialog.Accepted:
                edited_media_list = dialog_edit_bulk.edited_media_list
                dialog = DialogProcess(
                    operation=lambda: bulk_edit_procedure(edited_media_list),
                    title="Medyaları Toplu Düzenle",
                    message="Toplu düzenleme işlemi devam ediyor...",
                )

                if dialog.exec_() == QDialog.Accepted:
                    show_message("Toplu düzenleme işlemi tamamlandı.", level="info")
                    self.refresh_current_media_state()
                else:
                    show_message(
                        "Toplu düzenleme işlemi tamamlanamadı.", level="warning"
                    )

    def run_slideshow(self):
        current_direction = self.frame_bottom.get_slideway_direction()
        if current_direction == "F":
            self.go_to_next_media()
        elif current_direction == "B":
            self.go_to_previous_media()
        elif current_direction == "R":
            self.go_to_random_media()

    def on_slideshow_clicked(self, checked):
        if checked:
            self.slideshow_timer.start()
        else:
            self.slideshow_timer.stop()

    def stop_slideshow(self):
        self.slideshow_timer.stop()
        self.frame_bottom.button_slideshow.setChecked(False)

    def on_button_people_clicked(self, checked):
        if checked:
            media_key = (
                f"{self.displayed_media.media_uuid}{self.displayed_media.extension}"
            )
            q_image = self.media_loader.get_image(media_key)
            if q_image is None:
                pass
            q_image.save("temp/detections.jpg", "JPEG")
            pil_image = Image.open("temp/detections.jpg")

            people = self.displayed_media.people
            people_detect = self.displayed_media.people_detect

            if people is not None and people_detect is not None:
                dwn = face_detection.build_detections_with_names(people_detect, people)
                pil_image = face_detection.draw_identifications(pil_image, dwn)
                pil_image = pil_image.convert("RGB")
                pil_image.save("temp/detections.jpg", "JPEG")
                q_image = QImage("temp/detections.jpg")
                pixmap = QPixmap.fromImage(q_image)
                self.image_label.setPixmap(pixmap)
                self.fit_to_window()

            dialog_people = DialogPeople(people or "", parent=self)
            dialog_people.exec_()
            self.frame_bottom.button_people.setChecked(False)

            selected_indexes = self.thumbnail_list.selectedIndexes()
            if selected_indexes:
                current_index = selected_indexes[0].row()
                item = self.thumbnail_model.index(current_index)
                self.on_media_selected(item)

    def on_button_notes_clicked(self, checked):
        if checked:
            dialog_notes = DialogNotes(self.displayed_media.notes or "", parent=self)
            dialog_notes.exec_()
            self.frame_bottom.button_notes.setChecked(False)

    def update_thumbnail_highlights(self):
        self.thumbnail_model.dataChanged.emit(
            self.thumbnail_model.index(0),
            self.thumbnail_model.index(self.thumbnail_model.rowCount() - 1),
            [Qt.BackgroundRole],
        )

    def on_media_selected(self, index: QModelIndex):
        row = index.row()

        # If Ctrl + click
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            if row in self.selected_rows:
                self.selected_rows.remove(row)
            else:
                self.selected_rows.append(row)

            self.update_thumbnail_highlights()
            self.update_frame_bottom_top_label()
            self.handle_selection_feature_buttons()
            model_index = self.thumbnail_model.index(self.media_index, 0)
            self.thumbnail_list.selectionModel().select(
                model_index, QItemSelectionModel.Select
            )

        else:
            self.media_index = row
            self.displayed_media = self.media_data[row]
            self.display_history_manager.update(self.displayed_media.media_uuid)

            self.load_media_metadata()

            # Image
            if self.displayed_media.type == 1:
                self.load_image()

            # Video or Audio
            else:
                self.load_video_audio_thumbnail()

            if self.is_first_selection:
                self.is_first_selection = False
                # Perform any actions you want to do on the first selection here

    def load_media_metadata(self):
        self.frame_bottom.set_media_info(self.displayed_media)

    def load_image(self):
        """
        Load the selected image into the main display area.
        """
        self.image_label.is_image = True
        media_key = f"{self.displayed_media.media_uuid}{self.displayed_media.extension}"
        self.image_label.current_media_key = media_key
        self.image_label.scale_modifier = 0.0
        q_image = self.media_loader.get_image(media_key)

        if q_image is not None:
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap)
            self.fit_to_window()

    def load_video_audio_thumbnail(self):
        self.image_label.is_image = False
        media_key = f"{self.displayed_media.media_uuid}{self.displayed_media.extension}"
        self.image_label.current_media_key = media_key
        self.image_label.scale_modifier = 0.0
        q_image = self.media_loader.get_thumbnail(
            f"{self.displayed_media.media_uuid}.jpg"
        )
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)
        self.fit_to_window()

    def on_latest_media(self, checked):
        if checked:
            self.handle_feature_buttons(self.button_latest_media, checked=True)
            self.mode = "latest"

            selected_indexes = self.thumbnail_list.selectedIndexes()
            if selected_indexes:
                self.previous_media_index = self.media_index

            self.previous_media_filter = (
                copy.deepcopy(self.media_filter) if self.media_filter else None
            )
            # Use the LATEST_DURATION_DAYS setting from Config instead of hardcoded 7 days
            days = Config.LATEST_DURATION_DAYS
            self.media_filter = MediaFilter(
                created_at_range_enabled=True,
                created_at_range=(get_unix_time_days_ago(days), -1.0),
            )
            self.update_media_data(
                self.data_manager.get_filtered_media(self.media_filter)
            )

        else:
            self.mode = ""
            self.handle_feature_buttons(self.button_latest_media, checked=False)
            self.return_to_previous_media_state()

    def on_open_media(self):
        media_path = self.media_loader.get_media_path(
            self.displayed_media.media_uuid, self.displayed_media.extension
        )

        try:
            file_ops.open_with_default_app(media_path)
        except:
            show_message("Medya dosyası açılamadı.", level="error")

    def on_delete_media(self):
        def delete_procedure():
            self.data_manager.update_local_db()
            self.data_manager.set_media_deleted(self.displayed_media.media_uuid)
            cloud_ops.upload_database()
            file_ops.delete_media(
                self.displayed_media.media_uuid, self.displayed_media.extension
            )
            cloud_ops.delete_media(
                self.displayed_media.media_uuid, self.displayed_media.extension
            )

        procceed = show_message(
            (
                "Silme işlemi medyayı hem bilgisayarınızdan hem de bulut sisteminden siler!\n"
                "Bu işlem geri alınamaz!\n\n"
                "Seçili medyayı silme işlemini onaylıyor musunuz?"
            ),
            is_question=True,
        )
        if procceed:
            dialog_delete = DialogProcess(
                operation=delete_procedure,
                title="Silme İşlemi",
                message="Silme işlemi devam ediyor...",
            )
            dialog_delete.exec_()
            self.refresh_current_media_state()

    def fit_to_window(self):
        if self.image_label.pixmap():
            scroll_size = self.scroll_area.viewport().size()
            img_size = self.image_label.pixmap().size()
            img_aspect_ratio = img_size.width() / (img_size.height() + 0.001)
            scroll_aspect_ratio = scroll_size.width() / scroll_size.height()

            if img_aspect_ratio > scroll_aspect_ratio:
                # Image is wider than the viewport
                new_width = int(scroll_size.width())
                new_height = int(new_width / (img_aspect_ratio + 0.001))
            else:
                # Image is taller than the viewport
                new_height = int(scroll_size.height())
                new_width = int(new_height * img_aspect_ratio)

            self.image_label.setFixedSize(new_width, new_height)
            self.image_label.initial_scale = new_width / (img_size.width() + 0.001)
            self.image_label.original_size = img_size
            self.image_label.scale_modifier = 0.0

    def adjust_scroll_area(self, click_pos, scale_factor, old_width, old_height):
        horizontal_scroll = self.scroll_area.horizontalScrollBar()
        vertical_scroll = self.scroll_area.verticalScrollBar()

        # Calculate the new dimensions
        new_width = old_width * scale_factor
        new_height = old_height * scale_factor

        # Calculate the relative position of the click within the QLabel
        relative_x = click_pos.x() / old_width if old_width > 0 else 0.5
        relative_y = click_pos.y() / old_height if old_height > 0 else 0.5

        # Adjust the scroll area to maintain the relative position of the mouse
        new_horizontal_value = int(
            horizontal_scroll.value() + (relative_x * new_width - click_pos.x())
        )
        new_vertical_value = int(
            vertical_scroll.value() + (relative_y * new_height - click_pos.y())
        )

        # Set the new scroll values
        horizontal_scroll.setValue(new_horizontal_value)
        vertical_scroll.setValue(new_vertical_value)

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        self.fit_to_window()

    def show_add_media_dialog(self):
        if self.check_cloud_connected():
            dialog = DialogAddMedia(self.data_manager)
            dialog.exec_()
            if dialog.an_upload_completed:
                self.refresh_current_media_state()

    def show_edit_media_dialog(self):
        if self.check_cloud_connected():
            dialog = DialogEditMedia(
                self.data_manager, self.media_loader, self.displayed_media
            )
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_current_media_state()

    def return_to_previous_media_state(self):
        if self.mode in ["list", "explore_forgotten"]:
            if self.previous_mode_media_data:
                self.update_media_data(
                    self.previous_mode_media_data, index=self.previous_mode_media_index
                )
                self.previous_mode_media_data = None
                self.previous_mode_media_index = 0

        elif self.mode in ["today_in_history", "latest"]:
            self.media_filter = (
                copy.deepcopy(self.previous_mode_media_filter)
                if self.previous_mode_media_filter
                else None
            )
            if self.media_filter:
                self.update_media_data(
                    self.data_manager.get_filtered_media(self.media_filter),
                    index=self.previous_mode_media_index,
                )
            else:
                self.update_media_data(
                    self.data_manager.get_all_media(),
                    index=self.previous_mode_media_index,
                )

        else:
            self.media_filter = (
                copy.deepcopy(self.previous_media_filter)
                if self.previous_media_filter
                else None
            )
            if self.media_filter:
                self.update_media_data(
                    self.data_manager.get_filtered_media(self.media_filter),
                    index=self.previous_media_index,
                )
            else:
                self.update_media_data(
                    self.data_manager.get_all_media(), index=self.previous_media_index
                )

    def refresh_current_media_state(self):
        if self.mode == "list":
            selected_uuids = self.media_list_manager.get_uuids_from_list(
                self.media_list_name
            )
            media_from_list = self.data_manager.get_media_by_uuids(selected_uuids)
            self.update_media_data(media_from_list, self.media_index)

        elif self.mode == "explore_forgotten":
            media_list = self.data_manager.get_media_by_uuids(self.forgotten_uuids)
            self.update_media_data(media_list, self.media_index)

        else:
            if self.media_filter:
                self.update_media_data(
                    self.data_manager.get_filtered_media(self.media_filter),
                    index=self.media_index,
                )
            else:
                self.update_media_data(
                    self.data_manager.get_all_media(), index=self.media_index
                )

    def show_filter_dialog(self):
        self.dialog_filter.recenter()
        if self.dialog_filter.exec_() == QDialog.Accepted:
            self.media_filter = self.dialog_filter.media_filter
            self.update_media_data(
                self.data_manager.get_filtered_media(self.media_filter)
            )

    def check_cloud_connected(self):
        if cloud_ops.check_s3():
            self.set_cloud_connected(True)
            return True
        self.set_cloud_connected(False)
        show_message("Bulut sistemi bağlantısı sağlanamadı.", level="warning")
        return False

    def set_cloud_connected(self, connected: bool):
        if connected:
            self.frame_bottom.status_cloud.setToolTip(Constants.TOOLTIP_CLOUD_SUCCESS)
            self.frame_bottom.status_cloud.setPixmap(
                QPixmap("res/icons/Cloud-Check--Streamline-Core.png")
            )
        else:
            self.frame_bottom.status_cloud.setToolTip(Constants.TOOLTIP_CLOUD_FAIL)
            self.frame_bottom.status_cloud.setPixmap(
                QPixmap("res/icons/Cloud-Warning--Streamline-Core.png")
            )

    def show_settings_dialog(self):
        """Show the settings dialog and apply changes if accepted"""
        dialog = DialogSettings(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            # Update local storage status indicator
            self.update_local_storage_status()

            # Theme changes will take effect after restart, so we don't call apply_theme_styling

    def update_local_storage_status(self):
        """Update the local storage status indicator based on config"""
        from config.config import Config

        if Config.LOCAL_STORAGE_ENABLED:
            self.frame_bottom.status_storage.setToolTip(Constants.TOOLTIP_STORAGE_ON)
            self.frame_bottom.status_storage.setPixmap(
                QPixmap("res/icons/Download-Computer--Streamline-Core-Green.png")
            )
        else:
            self.frame_bottom.status_storage.setToolTip(Constants.TOOLTIP_STORAGE_OFF)
            self.frame_bottom.status_storage.setPixmap(
                QPixmap("res/icons/Download-Computer--Streamline-Core-Blue.png")
            )

    def on_today_in_history(self, checked):
        if checked:
            self.handle_feature_buttons(self.button_today_in_history, checked=True)
            self.mode = "today_in_history"

            selected_indexes = self.thumbnail_list.selectedIndexes()
            if selected_indexes:
                self.previous_media_index = self.media_index

            self.previous_media_filter = (
                copy.deepcopy(self.media_filter) if self.media_filter else None
            )
            today_day = datetime.now().strftime("%d")
            today_month = datetime.now().strftime("%m")
            self.media_filter = MediaFilter(days=today_day, months=today_month)
            self.update_media_data(
                self.data_manager.get_filtered_media(self.media_filter)
            )

        else:
            self.mode = ""
            self.handle_feature_buttons(self.button_today_in_history, checked=False)
            self.return_to_previous_media_state()

    def on_explore_forgotten(self, checked):
        if checked:
            self.mode = "explore_forgotten"
            self.handle_feature_buttons(self.button_explore_forgotten, checked=True)

            selected_indexes = self.thumbnail_list.selectedIndexes()
            if selected_indexes:
                self.previous_media_index = self.media_index

            self.previous_media_filter = (
                copy.deepcopy(self.media_filter) if self.media_filter else None
            )

            self.display_history_manager.load_display_history_file()
            all_forgotten_uuids = self.display_history_manager.get_ordered_uuids()[
                :5000
            ]
            self.forgotten_uuids = random.sample(all_forgotten_uuids, 100)

            media_list = self.data_manager.get_media_by_uuids(self.forgotten_uuids)
            self.update_media_data(media_list)

        else:
            self.mode = ""
            self.handle_feature_buttons(self.button_explore_forgotten, checked=False)
            self.display_history_manager.save_display_history_file()
            self.return_to_previous_media_state()

    def on_same_date_location(self, checked):
        if checked:
            self.handle_feature_buttons(self.button_same_date_location, checked=True)

            selected_indexes = self.thumbnail_list.selectedIndexes()

            if self.mode in ["list", "explore_forgotten"]:
                self.previous_mode_media_index = (
                    self.media_index if selected_indexes else 0
                )
                self.previous_mode_media_data = copy.deepcopy(self.media_data)

            elif self.mode in ["today_in_history", "latest"]:
                self.previous_mode_media_index = (
                    self.media_index if selected_indexes else 0
                )
                self.previous_mode_media_filter = (
                    copy.deepcopy(self.media_filter) if self.media_filter else None
                )
            else:
                self.previous_media_index = self.media_index if selected_indexes else 0
                self.previous_media_filter = (
                    copy.deepcopy(self.media_filter) if self.media_filter else None
                )

            date = self.displayed_media.date_text
            location = self.displayed_media.location

            self.media_filter = MediaFilter(
                date_range=(date, ""), location_exact=location
            )
            self.update_media_data(
                self.data_manager.get_filtered_media(self.media_filter)
            )

        else:
            self.handle_feature_buttons(self.button_same_date_location, checked=False)
            self.return_to_previous_media_state()

    def on_same_date(self, checked):
        if checked:
            self.handle_feature_buttons(self.button_same_date, checked=True)

            selected_indexes = self.thumbnail_list.selectedIndexes()

            if self.mode in ["list", "explore_forgotten"]:
                self.previous_mode_media_index = (
                    self.media_index if selected_indexes else 0
                )
                self.previous_mode_media_data = copy.deepcopy(self.media_data)

            elif self.mode in ["today_in_history", "latest"]:
                self.previous_mode_media_index = (
                    self.media_index if selected_indexes else 0
                )
                self.previous_mode_media_filter = (
                    copy.deepcopy(self.media_filter) if self.media_filter else None
                )
            else:
                self.previous_media_index = self.media_index if selected_indexes else 0
                self.previous_media_filter = (
                    copy.deepcopy(self.media_filter) if self.media_filter else None
                )

            date = self.displayed_media.date_text
            self.media_filter = MediaFilter(date_range=(date, ""))
            self.update_media_data(
                self.data_manager.get_filtered_media(self.media_filter)
            )

        else:
            self.handle_feature_buttons(self.button_same_date, checked=False)
            self.return_to_previous_media_state()

    def on_same_location(self, checked):
        if checked:
            self.handle_feature_buttons(self.button_same_location, checked=True)

            selected_indexes = self.thumbnail_list.selectedIndexes()

            if self.mode in ["list", "explore_forgotten"]:
                self.previous_mode_media_index = (
                    self.media_index if selected_indexes else 0
                )
                self.previous_mode_media_data = copy.deepcopy(self.media_data)

            elif self.mode in ["today_in_history", "latest"]:
                self.previous_mode_media_index = (
                    self.media_index if selected_indexes else 0
                )
                self.previous_mode_media_filter = (
                    copy.deepcopy(self.media_filter) if self.media_filter else None
                )
            else:
                self.previous_media_index = self.media_index if selected_indexes else 0
                self.previous_media_filter = (
                    copy.deepcopy(self.media_filter) if self.media_filter else None
                )

            location = self.displayed_media.location
            self.media_filter = MediaFilter(location_exact=location)
            self.update_media_data(
                self.data_manager.get_filtered_media(self.media_filter)
            )

        else:
            self.handle_feature_buttons(self.button_same_location, checked=False)
            self.return_to_previous_media_state()

    def update_media_data(self, new_media_data, index=0):
        self.stop_slideshow()
        self.clear_selection()

        if new_media_data is None:
            log("MainWindow.update_media_data", "Media data is None.", level="error")
            show_message("Medyaları güncellerken bir sorun yaşandı.", level="error")
            return

        elif len(new_media_data) == 0:
            log(
                "MainWindow.update_media_data",
                "Media data is empty, no media to display.",
                level="warning",
            )
            show_message("Gösterilecek medya bulunamadı.", level="warning")

        # Update media_data
        self.media_data = new_media_data

        # Refresh the thumbnails and reset the index
        thumbnail_keys = [f"{media.media_uuid}.jpg" for media in self.media_data]
        self.thumbnail_model = ListModelThumbnail(
            thumbnail_keys, self.media_loader, parent=self
        )
        self.thumbnail_list.setModel(self.thumbnail_model)
        self.thumbnail_model.signal.loaded.connect(lambda: self.try_select_item(index))

        self.update_frame_bottom_top_label()
        self.handle_selection_feature_buttons()

    def update_frame_bottom_top_label(self):
        self.frame_bottom.top_label.setText(
            f"{len(self.selected_rows)} / {len(self.media_data)}"
        )

    def get_uuids_of_selected_rows(self):
        return [self.media_data[row].media_uuid for row in self.selected_rows]

    def select_all(self):
        self.selected_rows = [*range(0, len(self.media_data), 1)]
        self.update_frame_bottom_top_label()
        self.handle_selection_feature_buttons()

    def clear_selection(self):
        self.selected_rows.clear()
        self.update_frame_bottom_top_label()
        self.handle_selection_feature_buttons()

    def reverse_selection(self):
        self.selected_rows = [
            row
            for row in range(0, len(self.media_data), 1)
            if row not in self.selected_rows
        ]
        self.update_frame_bottom_top_label()
        self.handle_selection_feature_buttons()

    def add_selection_to_list(self):
        dialog = DialogLists(
            media_loader=self.media_loader,
            media_list_manager=self.media_list_manager,
            mode="add",
        )
        if dialog.exec_() == QDialog.Accepted:
            selected_list_name = dialog.selected_element
            if show_message(
                f"Seçili {len(self.selected_rows)} medyayı '{selected_list_name}' listesine\neklemek istediğinize emin misiniz?",
                is_question=True,
            ):
                if selected_list_name:
                    self.media_list_manager.add_uuids_to_media_list(
                        list_name=selected_list_name,
                        uuids=self.get_uuids_of_selected_rows(),
                    )
                    show_message(f"Medyalar '{selected_list_name}' listesine eklendi.")

    def remove_selection(self):
        if self.media_list_name:
            if show_message(
                f"Seçili {len(self.selected_rows)} medyayı '{self.media_list_name}' listesinden\nkalıcı olarak çıkarmak istediğinize emin misiniz?",
                is_question=True,
            ):
                self.media_list_manager.remove_uuids_from_media_list(
                    list_name=self.media_list_name,
                    uuids=self.get_uuids_of_selected_rows(),
                )
                self.refresh_current_media_state()
                show_message(
                    f"Medyalar '{self.media_list_name}' listesinden çıkarıldı."
                )

    def handle_selection_feature_buttons(self):
        if len(self.selected_rows) > 0:
            self.button_export_selected_media.setEnabled(True)
            self.button_bulk_edit_selected_media.setEnabled(True)
            self.button_add_to_list.setEnabled(True)
        else:
            self.button_export_selected_media.setEnabled(False)
            self.button_bulk_edit_selected_media.setEnabled(False)
            self.button_add_to_list.setEnabled(False)

    def reorder_date(self, index):
        def reorder_date_procedure(date, reordered_keys):
            self.data_manager.update_local_db()
            reordered_uuids = [key.split(".")[0] for key in reordered_keys]
            self.data_manager.reorder_within_date(
                date=date, ordered_uuids=reordered_uuids
            )
            cloud_ops.upload_database()

        right_clicked_media = self.media_data[index.row()]
        date_text = right_clicked_media.date_text
        date_filter = MediaFilter(date_range=(date_text, ""))
        media_from_date = self.data_manager.get_filtered_media(date_filter)
        thumbnail_keys = [f"{media.media_uuid}.jpg" for media in media_from_date]

        dialog = DialogReorder(thumbnail_keys, self.media_loader, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            reordered_keys = dialog.get_reordered_keys()
            dialog_process = DialogProcess(
                operation=lambda: reorder_date_procedure(
                    right_clicked_media.date, reordered_keys
                ),
                title="Güne Ait Medyaları Yeniden Sırala",
                message="Medya sıralaması güncelleniyor...",
            )
            dialog_process.exec_()
            self.refresh_current_media_state()
            show_message("Medya sıralaması başarı ile güncellendi.", level="info")

    def simulate_keypress(self, window, key):
        """Simulates a keypress event."""
        # Create a QKeyEvent for the keypress (KeyPress event)
        event = QKeyEvent(QKeyEvent.KeyPress, key, Qt.NoModifier)

        # Post the event directly to the QLineEdit widget
        QApplication.postEvent(window, event)

        # Create a QKeyEvent for the key release (KeyRelease event)
        release_event = QKeyEvent(QKeyEvent.KeyRelease, key, Qt.NoModifier)

        # Post the key release event
        QApplication.postEvent(window, release_event)

    def closeEvent(self, event):
        self.display_history_manager.save_display_history_file()
        event.accept()

    def apply_theme_styling(self):
        """Apply theme-specific styling to MainWindow components"""
        # We're now using a minimal approach that preserves the native windowsvista style
        # Most styling is handled by the application palette in ThemeManager.apply_theme
        # Only specific background colors are set via stylesheet in ThemeManager.get_stylesheet

        # No additional styling needed here as it's handled by the ThemeManager
        pass
