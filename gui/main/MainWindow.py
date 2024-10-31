from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QScrollArea,
    QWidget,
    QListView,
    QPushButton,
    QGridLayout,
    QDialog,
    QApplication
)
from PyQt5.QtCore import Qt, QModelIndex, QSize, QTimer
from PyQt5.QtGui import QPixmap, QPalette, QKeyEvent, QIcon, QImage
from PIL import Image

from media_loader import MediaLoader
from logger import log
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

import face_detection
from ops import cloud_ops


class MainWindow(QMainWindow):
    def __init__(self, data_manager: DataManager, media_loader: MediaLoader):
        super().__init__()
        self.data_manager = data_manager
        self.media_loader = media_loader

        """
        if cloud_ops.check_s3():
            success = self.data_manager.update_local_db()
            if not success:
                pass
        else:
            pass
        """

        self.media_data = self.data_manager.get_all_media()
        self.previous_media_data = self.media_data.copy()
        self.selected_media = None
        self.previous_index = None

        # Set window title and initial dimensions
        self.setWindowTitle("ALBUM 2.0")
        self.setGeometry(100, 100, 1280, 720)

        #self.file_menu = QMenu("&Dosya", self)
        #self.file_menu.addAction(QAction("&Aç...", self))
        #self.menuBar().addMenu(self.file_menu)
        #self.menuBar().setFixedWidth(50)

        # Main container widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create the layout for the main widget
        main_layout = QVBoxLayout(main_widget)

        # Create a horizontal layout to hold the left frame and image container
        horizontal_layout = QHBoxLayout()
        main_layout.addLayout(horizontal_layout)

        # Create the frame for the menu on the left side 
        self.frame_menu = QFrame()
        self.frame_menu.setFixedWidth(160)
        horizontal_layout.addWidget(self.frame_menu)

        # Set a layout for the frame_menu
        menu_layout = QVBoxLayout(self.frame_menu)
        # Remove margins for full use of space
        menu_layout.setContentsMargins(0, 0, 0, 0)


        # Create right QFrame with fixed width and height, and add buttons in a grid
        self.frame_features_area = QFrame()
        self.frame_features_area.setFixedWidth(160)
        self.frame_features_area.setFixedHeight(160)

        # Create a grid layout for the buttons inside the right frame
        self.layout_features_area = QGridLayout()
        self.layout_features_area.setContentsMargins(0,0,10,10)

        self.button_upload_media = QPushButton()
        self.button_upload_media.setFocusPolicy(Qt.NoFocus)
        self.button_upload_media.setFixedSize(50, 50)
        self.button_upload_media.setIcon(QIcon("res/icons/Image--Add.png"))
        self.button_upload_media.setIconSize(QSize(30, 30))
        self.button_upload_media.setText("")
        self.button_upload_media.clicked.connect(self.show_add_media_dialog)
        #self.button_upload_media.setToolTip(Constants.TOOLTIP_BUTTON_BACK)
        self.layout_features_area.addWidget(self.button_upload_media, 0, 0)

        self.button_filter = QPushButton()
        self.button_filter.setFocusPolicy(Qt.NoFocus)
        self.button_filter.setFixedSize(50, 50)
        self.button_filter.setIcon(QIcon("res/icons/Filter-2--Streamline-Sharp-Gradient--Free.png"))
        self.button_filter.setIconSize(QSize(30, 30))
        self.button_filter.setText("")
        #self.button_filter.setToolTip(Constants.TOOLTIP_BUTTON_FORWARD)
        self.layout_features_area.addWidget(self.button_filter, 0, 1)
        self.dialog_filter = DialogFilter(self.data_manager)
        self.button_filter.clicked.connect(self.show_filter_dialog)

        self.button_same_date_location = QPushButton()
        self.button_same_date_location.setFocusPolicy(Qt.NoFocus)
        self.button_same_date_location.setFixedSize(50, 50)
        self.button_same_date_location.setIcon(QIcon("res/icons/Date--Location.png"))
        self.button_same_date_location.setIconSize(QSize(30, 30))
        self.button_same_date_location.setText("")
        self.button_same_date_location.clicked.connect(self.on_same_date_location)
        self.button_same_date_location.setCheckable(True)
        #self.button_same_date_location.setToolTip(Constants.TOOLTIP_BUTTON_SLIDESHOW)
        self.layout_features_area.addWidget(self.button_same_date_location, 0, 2)

        self.button_export_media = QPushButton()
        self.button_export_media.setFocusPolicy(Qt.NoFocus)
        self.button_export_media.setFixedSize(50, 50)
        #self.button_export_media.setIcon(QIcon("res/icons/Align-Front-1--Streamline-Core-Gradient.png"))
        self.button_export_media.setEnabled(False)
        self.button_export_media.setIconSize(QSize(30, 30))
        self.button_export_media.setText("")
        #self.button_export_media.setToolTip(Constants.TOOLTIP_BUTTON_NOTES)
        self.layout_features_area.addWidget(self.button_export_media, 1, 0)

        self.button_edit_media = QPushButton()
        self.button_edit_media.setFocusPolicy(Qt.NoFocus)
        self.button_edit_media.setFixedSize(50, 50)
        #self.button_edit_media.setIcon(QIcon("res/icons/Task-List-Edit--Streamline-Plump-Gradient.png"))
        self.button_edit_media.setEnabled(False)
        self.button_edit_media.setIconSize(QSize(30, 30))
        self.button_edit_media.setText("")
        #self.button_edit_media.setToolTip(Constants.TOOLTIP_BUTTON_PEOPLE)
        self.layout_features_area.addWidget(self.button_edit_media, 1, 1)

        self.button_placeholder1 = QPushButton()
        self.button_placeholder1.setFixedSize(50, 50)
        self.button_placeholder1.setText("")
        self.button_placeholder1.setEnabled(False)
        self.layout_features_area.addWidget(self.button_placeholder1, 1, 2)

        self.button_placeholder2 = QPushButton()
        self.button_placeholder2.setFixedSize(50, 50)
        self.button_placeholder2.setText("")
        self.button_placeholder2.setEnabled(False)
        self.layout_features_area.addWidget(self.button_placeholder2, 2, 0)

        self.button_placeholder3 = QPushButton()
        self.button_placeholder3.setFixedSize(50, 50)
        self.button_placeholder3.setText("")
        self.button_placeholder3.setEnabled(False)
        self.layout_features_area.addWidget(self.button_placeholder3, 2, 1)

        self.button_placeholder4 = QPushButton()
        self.button_placeholder4.setFixedSize(50, 50)
        self.button_placeholder4.setText("")
        self.button_placeholder4.setEnabled(False)
        self.layout_features_area.addWidget(self.button_placeholder4, 2, 2)

        self.frame_features_area.setLayout(self.layout_features_area)
        menu_layout.addWidget(self.frame_features_area)

        # Replace QListWidget with QListView
        self.thumbnail_list = QListView(self.frame_menu)
        self.thumbnail_list.setSpacing(1)
        self.thumbnail_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.thumbnail_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        menu_layout.addWidget(self.thumbnail_list)

        # Create the scroll area to display the selected image
        self.scroll_area = QScrollArea()
        horizontal_layout.addWidget(self.scroll_area)
        self.scroll_area.setBackgroundRole(QPalette.Dark)
        self.scroll_area.setVisible(False)
        self.scroll_area.setFocusPolicy(Qt.NoFocus)

        # Create a ImageViewerLabel for the image and add it to the scroll area
        self.image_label = LabelImageViewer(self.scroll_area, self.media_loader)
        self.image_label.setBackgroundRole(QPalette.Base)
        self.image_label.setScaledContents(True)
        self.scroll_area.setWidget(self.image_label)

        # Center the image_label within the scroll area
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setVisible(True)

        # Create the frame for information at the bottom
        self.frame_bottom = FrameBottom()
        self.frame_bottom.setFixedHeight(110)
        self.frame_bottom.setFocusPolicy(Qt.NoFocus)

        self.frame_bottom.top_label.setText(str(len(self.media_data)))

        self.frame_bottom.button_people.clicked.connect(self.on_button_people_clicked)
        self.frame_bottom.button_notes.clicked.connect(self.on_button_notes_clicked)
        self.frame_bottom.button_back.clicked.connect(self.go_to_previous_media)
        self.frame_bottom.button_forward.clicked.connect(self.go_to_next_media)
        
        self.frame_bottom.button_slideshow.clicked.connect(self.on_slideshow_clicked)
        self.slideshow_timer = QTimer(self)
        self.slideshow_timer.setInterval(5000)
        self.slideshow_timer.timeout.connect(self.run_slideshow)

        main_layout.addWidget(self.frame_bottom)

        # Create and set the custom model
        thumbnail_keys = [media.thumbnail_key for media in self.media_data]
        self.thumbnail_model = ListModelThumbnail(thumbnail_keys, self.media_loader)
        self.thumbnail_list.setModel(self.thumbnail_model)

        # Set the custom delegate
        self.thumbnail_list.setItemDelegate(ThumbnailDelegate())

        # Connect the clicked signal to handle item selection
        self.thumbnail_list.clicked.connect(self.on_media_selected)
        self.thumbnail_model.signal.loaded.connect(self.try_select_item)

        self.thumbnail_list.setFocus()

        # Warmup detection to load YOLOv8 model
        face_detection.detect_people(Image.new('RGB', (200, 200), color='white'))
    
    def keyPressEvent(self, event):
        """
        Handle key press events for navigating the thumbnails using the arrow keys.
        """
        if event.key() == Qt.Key_Right:
            self.go_to_next_media()

        elif event.key() == Qt.Key_Left:
            self.go_to_previous_media()

    
    def try_select_item(self, i=0):
        # Check if the model has any loaded items
        if self.thumbnail_model.rowCount() > 0:
            index = self.thumbnail_model.index(i, 0)

            self.thumbnail_list.setCurrentIndex(index)
            self.thumbnail_list.scrollTo(index)
            self.thumbnail_list.setFocus()

            self.thumbnail_list.clicked.emit(index)

    def go_to_next_media(self):
       
        selected_indexes = self.thumbnail_list.selectedIndexes()

        if selected_indexes:
            current_index = selected_indexes[0].row()
            print(f"Current_index: {current_index}")
        
        if current_index + 1 < self.thumbnail_model.rowCount():
            print(f"Going to: {current_index + 1}")
            next_index = self.thumbnail_model.index(current_index + 1)
            self.thumbnail_list.setCurrentIndex(next_index)
            self.on_media_selected(next_index)

    def go_to_previous_media(self):

        selected_indexes = self.thumbnail_list.selectedIndexes()

        if selected_indexes:
            current_index = selected_indexes[0].row()
            print(f"Current_index: {current_index}")
        
        if current_index - 1 >= 0:
            print(f"Going to: {current_index - 1}")
            prev_index = self.thumbnail_model.index(current_index - 1)
            self.thumbnail_list.setCurrentIndex(prev_index)
            self.on_media_selected(prev_index)

    def run_slideshow(self):
        current_direction = self.frame_bottom.get_slideway_direction()
        if current_direction == "F":
            self.go_to_next_media()
        else:
            self.go_to_previous_media()

    def on_slideshow_clicked(self, checked):
        if checked:
            self.slideshow_timer.start()
        else:
            self.slideshow_timer.stop()
    
    def on_button_people_clicked(self, checked):
        if checked:
            q_image = self.media_loader.get_image(self.selected_media.media_key)
            if q_image is None:
                pass
            q_image.save("temp/detections.jpg", "JPEG")
            pil_image = Image.open("temp/detections.jpg")
            
            people = self.selected_media.people
            people_detect = self.selected_media.people_detect
            
            if people is not None and people_detect is not None:
                
                dwn = face_detection.build_detections_with_names(people_detect, people)
                pil_image = face_detection.draw_identifications(pil_image, dwn)
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
            dialog_notes = DialogNotes(self.selected_media.notes or "", parent=self)
            dialog_notes.exec_()
            self.frame_bottom.button_notes.setChecked(False)
    
    def on_media_selected(self, index: QModelIndex):
        self.selected_media = self.media_data[index.row()]
        
        self.load_media_metadata()

        # Image
        if self.selected_media.type == 1:
            self.load_image()
        
        # Video or Audio
        else:
            self.load_video_audio_thumbnail()

    def load_media_metadata(self):
        self.frame_bottom.set_media_info(self.selected_media)

    def load_image(self):
        """
        Load the selected image into the main display area.
        """
        self.image_label.is_image = True
        self.image_label.current_media_key = self.selected_media.media_key
        self.image_label.scale_modifier = 0.0
        q_image = self.media_loader.get_image(self.selected_media.media_key)
        
        if q_image is not None:
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap)
            self.fit_to_window()

    def load_video_audio_thumbnail(self):
        self.image_label.is_image = False
        self.image_label.current_media_key = self.selected_media.media_key
        self.image_label.scale_modifier = 0.0
        q_image = self.media_loader.get_thumbnail(self.selected_media.thumbnail_key)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)
        self.fit_to_window()


    def fit_to_window(self):
        if self.image_label.pixmap():
            scroll_size = self.scroll_area.viewport().size()
            img_size = self.image_label.pixmap().size()
            img_aspect_ratio = img_size.width() / img_size.height()
            scroll_aspect_ratio = scroll_size.width() / scroll_size.height()

            if img_aspect_ratio > scroll_aspect_ratio:
                # Image is wider than the viewport
                new_width = scroll_size.width()
                new_height = new_width / img_aspect_ratio
            else:
                # Image is taller than the viewport
                new_height = scroll_size.height()
                new_width = new_height * img_aspect_ratio

            self.image_label.setFixedSize(new_width, new_height)
            self.image_label.initial_scale = new_width / img_size.width()
            self.image_label.original_size = img_size
            self.image_label.scale_modifier = 0.0


    def adjust_scroll_area(self, click_pos, scale_factor):
        # Get the current scroll positions
        h_scroll = self.scroll_area.horizontalScrollBar()
        v_scroll = self.scroll_area.verticalScrollBar()

        # Get the relative click position in the image as a percentage
        relative_x = click_pos.x() / self.image_label.width()
        relative_y = click_pos.y() / self.image_label.height()

        # Calculate the new scroll position based on the clicked point and zoom level
        h_new_value = int(relative_x * h_scroll.maximum())
        v_new_value = int(relative_y * v_scroll.maximum())

        # Set the new scroll positions, adjusting as needed
        h_scroll.setValue(h_new_value)
        v_scroll.setValue(v_new_value)

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        self.fit_to_window()

    def show_add_media_dialog(self):
        if not cloud_ops.check_s3():
            pass
        dialog = DialogAddMedia(self.data_manager)
        dialog.exec_()

        self.update_media_data(self.data_manager.get_all_media())

    def show_filter_dialog(self):
        if self.dialog_filter.exec_() == QDialog.Accepted:

            self.update_media_data(self.dialog_filter.media_list)
        
        else:
            pass

    def on_same_date_location(self, checked):
        
        if checked:
            selected_indexes = self.thumbnail_list.selectedIndexes()

            if selected_indexes:
                self.previous_index = selected_indexes[0].row()

            self.previous_media_data = self.media_data.copy()

            date = self.selected_media.date_text
            location = self.selected_media.location

            media_filter = MediaFilter(date_range=(date, ""), location_exact=location)
            self.update_media_data(self.data_manager.get_filtered_media(media_filter))
        
        elif self.previous_media_data is not None:

            if self.previous_index is not None:
                self.update_media_data(self.previous_media_data.copy(), self.previous_index)
            else:
                self.update_media_data(self.previous_media_data.copy())


    def update_media_data(self, new_media_data, index=0):
            
            if new_media_data is None:
                log("MainWindow.update_media_data", "Media data is None.", level="error")
                show_message("Medyaları güncellerken bir sorun yaşandı.", level="error")
                return
            
            elif len(new_media_data) == 0:
                log("MainWindow.update_media_data", "Media data is empty, no media to display.", level="warning")
                show_message("Gösterilecek medya bulunamadı.", level="warning")
                
            # Update media_data
            self.media_data = new_media_data

            # Refresh the thumbnails and reset the index
            thumbnail_keys = [media.thumbnail_key for media in self.media_data]
            self.thumbnail_model = ListModelThumbnail(thumbnail_keys, self.media_loader)
            self.thumbnail_list.setModel(self.thumbnail_model)
            self.thumbnail_model.signal.loaded.connect(lambda: self.try_select_item(index))

            self.frame_bottom.top_label.setText(str(len(self.media_data)))
    
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
