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
    QMenu,
    QAction
)
from PyQt5.QtCore import Qt, QModelIndex, QEvent, QSize
from PyQt5.QtGui import QPixmap, QPalette, QKeyEvent, QIcon

from data.Media import Media
from gui.FrameBottom import FrameBottom
from gui.ThumbListModel import ThumbListModel, ThumbnailDelegate
from gui.ImageViewerLabel import ImageViewerLabel
from gui.DialogAddMedia import DialogAddMedia

import aws


class MainWindow(QMainWindow):
    def __init__(self, data_manager, media_loader):
        super().__init__()
        self.data_manager = data_manager
        self.media_loader = media_loader

        if aws.check_s3():
            success = self.data_manager.update_local_db()
            if not success:
                pass
        else:
            pass

        self.media_data = self.data_manager.get_all_media()

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
        self.button_upload_media.setFixedSize(50, 50)
        self.button_upload_media.setIcon(QIcon("res/icons/Image--Add.png"))
        self.button_upload_media.setIconSize(QSize(30, 30))
        self.button_upload_media.setText("")
        self.button_upload_media.clicked.connect(self.show_add_media_dialog)
        #self.button_upload_media.setToolTip(Constants.TOOLTIP_BUTTON_BACK)
        self.layout_features_area.addWidget(self.button_upload_media, 0, 0)

        self.button_filter = QPushButton()
        self.button_filter.setFixedSize(50, 50)
        self.button_filter.setIcon(QIcon("res/icons/Filter-2--Streamline-Sharp-Gradient--Free.png"))
        self.button_filter.setIconSize(QSize(30, 30))
        self.button_filter.setText("")
        #self.button_filter.setToolTip(Constants.TOOLTIP_BUTTON_FORWARD)
        self.layout_features_area.addWidget(self.button_filter, 0, 1)

        self.button_same_date_location = QPushButton()
        self.button_same_date_location.setFixedSize(50, 50)
        self.button_same_date_location.setIcon(QIcon("res/icons/Date--Location.png"))
        self.button_same_date_location.setIconSize(QSize(30, 30))
        self.button_same_date_location.setText("")
        #self.button_same_date_location.setToolTip(Constants.TOOLTIP_BUTTON_SLIDESHOW)
        self.layout_features_area.addWidget(self.button_same_date_location, 0, 2)

        self.button_export_media = QPushButton()
        self.button_export_media.setFixedSize(50, 50)
        self.button_export_media.setIcon(QIcon("res/icons/Align-Front-1--Streamline-Core-Gradient.png"))
        self.button_export_media.setIconSize(QSize(30, 30))
        self.button_export_media.setText("")
        #self.button_export_media.setToolTip(Constants.TOOLTIP_BUTTON_NOTES)
        self.layout_features_area.addWidget(self.button_export_media, 1, 0)

        self.button_edit_media = QPushButton()
        self.button_edit_media.setFixedSize(50, 50)
        self.button_edit_media.setIcon(QIcon("res/icons/Task-List-Edit--Streamline-Plump-Gradient.png"))
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
        self.image_label = ImageViewerLabel(self.scroll_area)
        self.image_label.setBackgroundRole(QPalette.Base)
        self.image_label.setScaledContents(True)
        self.scroll_area.setWidget(self.image_label)

        # Center the image_label within the scroll area
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setVisible(True)

        # Create the frame for information at the bottom
        self.frame_bottom = FrameBottom()
        self.frame_bottom.setFixedHeight(110)
        main_layout.addWidget(self.frame_bottom)

        # Create and set the custom model
        thumbnail_keys = [media.thumbnail_key for media in self.media_data]
        self.thumbnail_model = ThumbListModel(thumbnail_keys, self.media_loader)
        self.thumbnail_list.setModel(self.thumbnail_model)

        # Set the custom delegate
        self.thumbnail_list.setItemDelegate(ThumbnailDelegate())

        # Connect the clicked signal to handle item selection
        self.thumbnail_list.clicked.connect(self.on_image_selected)

        self.thumbnail_list.setFocus()
    
    def keyPressEvent(self, event):
        """
        Handle key press events for navigating the thumbnails using the arrow keys.
        """
        selected_indexes = self.thumbnail_list.selectedIndexes()

        if selected_indexes:
            current_index = selected_indexes[0].row()

            # Handle the Right Arrow key (move to the next item)
            if event.key() == Qt.Key_Right:
                if current_index + 1 < self.thumbnail_model.rowCount():
                    next_index = self.thumbnail_model.index(current_index + 1)
                    self.thumbnail_list.setCurrentIndex(next_index)
                    self.on_image_selected(next_index)

            # Handle the Left Arrow key (move to the previous item)
            elif event.key() == Qt.Key_Left:
                if current_index - 1 >= 0:
                    prev_index = self.thumbnail_model.index(current_index - 1)
                    self.thumbnail_list.setCurrentIndex(prev_index)
                    self.on_image_selected(prev_index)

    def on_image_selected(self, index: QModelIndex):
        """
        When a preview image is clicked, display it in the main image label.
        """
        selected_media = self.media_data[index.row()]
        self.load_media_metadata(selected_media)
        self.load_image(selected_media)

    def load_media_metadata(self, media: Media):
        self.frame_bottom.set_media_info(media)

    def load_image(self, media: Media):
        """
        Load the selected image into the main display area.
        """
        self.image_label.scale_modifier = 0.0
        q_image = self.media_loader.get_image(media.media_key)
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
        if not aws.check_s3():
            pass
        dialog = DialogAddMedia(self.data_manager)
        dialog.exec_()
