import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QWidget,
    QListView,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionViewItem,
)
from PyQt5.QtCore import (
    Qt,
    QSize,
    QThreadPool,
    QRunnable,
    pyqtSignal,
    QObject,
    QModelIndex,
    QAbstractListModel,
    QRect,
)
from PyQt5.QtGui import QPixmap, QImage, QPalette
from MediaLoader import MediaLoader


class WorkerSignals(QObject):
    # Signal to emit the row and loaded pixmap
    finished = pyqtSignal(int, QPixmap)


class ThumbnailLoaderRunnable(QRunnable):
    def __init__(self, row, thumbnail_key, media_loader):
        super().__init__()
        self.row = row
        self.thumbnail_key = thumbnail_key
        self.media_loader = media_loader
        self.signals = WorkerSignals()

    def run(self):
        # Load the image thumbnail
        q_image = self.media_loader.get_thumbnail(self.thumbnail_key)
        pixmap = QPixmap.fromImage(q_image).scaled(160, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # Emit the signal with the row and pixmap
        self.signals.finished.emit(self.row, pixmap)


class ImageListModel(QAbstractListModel):
    def __init__(self, thumbnail_keys, media_loader, parent=None):
        super().__init__(parent)
        self.media_loader = media_loader
        self.thumbnail_keys = thumbnail_keys
        self.thumbnail_keys_loaded = []
        self.thumbnails = {}  # Cache of loaded thumbnails
        self.threadpool = QThreadPool()
        self.batch_size = 30000
        self.loaded_count = 0

    def rowCount(self, parent=QModelIndex()):
        return self.loaded_count

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DecorationRole:
            # Return the thumbnail image
            if index.row() in self.thumbnails:
                return self.thumbnails[index.row()]
            else:
                # Start loading the image asynchronously
                self.load_thumbnail(index.row())
                # Return a placeholder pixmap
                placeholder = QPixmap(160, 80)
                placeholder.fill(Qt.gray)
                return placeholder
        elif role == Qt.UserRole:
            return self.thumbnail_keys_loaded[index.row()]
        elif role == Qt.SizeHintRole:
            return QSize(160, 100)
        return None

    def canFetchMore(self, parent=QModelIndex()):
        return self.loaded_count < len(self.thumbnail_keys)

    def fetchMore(self, parent=QModelIndex()):
        remaining = len(self.thumbnail_keys) - self.loaded_count
        items_to_fetch = min(self.batch_size, remaining)
        self.beginInsertRows(
            QModelIndex(), self.loaded_count, self.loaded_count + items_to_fetch - 1
        )
        self.thumbnail_keys_loaded.extend(
            self.thumbnail_keys[self.loaded_count: self.loaded_count + items_to_fetch]
        )
        self.loaded_count += items_to_fetch
        self.endInsertRows()

    def load_thumbnail(self, row):
        if row in self.thumbnails:
            return  # Thumbnail already loaded

        thumbnail_key = self.thumbnail_keys_loaded[row]
        runnable = ThumbnailLoaderRunnable(row, thumbnail_key, self.media_loader)
        runnable.signals.finished.connect(self.on_thumbnail_loaded)
        self.threadpool.start(runnable)

    def on_thumbnail_loaded(self, row, pixmap):
        self.thumbnails[row] = pixmap
        index = self.index(row)
        self.dataChanged.emit(index, index, [Qt.DecorationRole])


class ZoomableLabel(QLabel):
    def __init__(self, parent=None):
        super(ZoomableLabel, self).__init__(parent)
        self.initial_scale = 1.0
        self.scale_modifier = 0
        self.original_size = None
        self.setScaledContents(True)  # Ensure the image scales with QLabel

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.zoom_in(event.pos())
        elif event.button() == Qt.RightButton:
            self.zoom_out(event.pos())

    def zoom_in(self, click_pos):
        if self.scale_modifier < 5.0:
            self.scale_modifier += 0.50
        self.update_image_size(click_pos)

    def zoom_out(self, click_pos):
        if self.scale_modifier > 0:
            self.scale_modifier -= 0.50
        self.update_image_size(click_pos)

    def update_image_size(self, click_pos):
        if not self.pixmap():
            return

        scaling_factor = self.initial_scale * (self.scale_modifier + 1)

        # Scale the image based on the new scale factor
        new_width = self.original_size.width() * scaling_factor
        new_height = self.original_size.height() * scaling_factor

        # Update QLabel size
        self.setFixedSize(new_width, new_height)

        # Adjust the scroll area to center on the click position
        self.parentWidget().parentWidget().parentWidget().parentWidget().adjust_scroll_area(click_pos, scaling_factor)

class ThumbnailDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Save the painter's state
        painter.save()

        # Draw the default item (background, selection, etc.)
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            painter.fillRect(option.rect, option.palette.base())

        # Get the pixmap from the model
        pixmap = index.data(Qt.DecorationRole)
        if pixmap:
            # Calculate the position to center the pixmap
            item_rect = option.rect
            pixmap_size = pixmap.size()
            x = item_rect.x() + (item_rect.width() - pixmap_size.width()) / 2
            y = item_rect.y() + (item_rect.height() - pixmap_size.height()) / 2

            # Draw the pixmap centered
            painter.drawPixmap(int(x), int(y), pixmap)

        # Draw focus rectangle if item has focus
        if option.state & QStyle.State_HasFocus:
            option_rect = QRect(
                int(x), int(y), pixmap_size.width(), pixmap_size.height()
            )
            option.rect = option_rect
            QApplication.style().drawPrimitive(
                QStyle.PE_FrameFocusRect, option, painter
            )

        # Restore the painter's state
        painter.restore()


class MainWindow(QMainWindow):
    def __init__(self, data_manager, media_loader):
        super().__init__()
        self.data_manager = data_manager
        self.media_loader = media_loader

        self.media_data = self.data_manager.get_all_media()

        # Set window title and initial dimensions
        self.setWindowTitle("ALBUM 2.0")
        self.setGeometry(100, 100, 800, 600)

        # Main container widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create the layout for the main widget
        main_layout = QVBoxLayout(main_widget)

        # Create a horizontal layout to hold the left frame and image container
        horizontal_layout = QHBoxLayout()
        main_layout.addLayout(horizontal_layout)

        # Create the frame for the menu on the left side (to hold the preview roll)
        self.frame_menu = QFrame()
        self.frame_menu.setFrameShape(QFrame.StyledPanel)
        self.frame_menu.setFixedWidth(160)
        horizontal_layout.addWidget(self.frame_menu)

        # Set a layout for the frame_menu
        menu_layout = QVBoxLayout(self.frame_menu)
        # Remove margins for full use of space
        menu_layout.setContentsMargins(0, 100, 0, 0)

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

        # Create a QLabel for the image and add it to the scroll area
        self.image_label = ZoomableLabel()
        self.image_label.setBackgroundRole(QPalette.Base)
        self.image_label.setScaledContents(True)
        self.scroll_area.setWidget(self.image_label)

        # Center the image_label within the scroll area
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setVisible(True)

        # Create the frame for information at the bottom
        self.frame_info = QFrame()
        self.frame_info.setFrameShape(QFrame.StyledPanel)
        self.frame_info.setFixedHeight(100)
        main_layout.addWidget(self.frame_info)

        # Create and set the custom model
        thumbnail_keys = [media.thumbnail_key for media in self.media_data]
        self.model = ImageListModel(thumbnail_keys, self.media_loader)
        self.thumbnail_list.setModel(self.model)

        # Set the custom delegate
        self.thumbnail_list.setItemDelegate(ThumbnailDelegate())

        # Connect the clicked signal to handle item selection
        self.thumbnail_list.clicked.connect(self.on_image_selected)

    def keyPressEvent(self, event):
        """
        Handle key press events for navigating the thumbnails using the arrow keys.
        """
        selected_indexes = self.thumbnail_list.selectedIndexes()

        if selected_indexes:
            current_index = selected_indexes[0].row()

            # Handle the Right Arrow key (move to the next item)
            if event.key() == Qt.Key_Right:
                if current_index + 1 < self.model.rowCount():
                    next_index = self.model.index(current_index + 1)
                    self.thumbnail_list.setCurrentIndex(next_index)
                    self.on_image_selected(next_index)

            # Handle the Left Arrow key (move to the previous item)
            elif event.key() == Qt.Key_Left:
                if current_index - 1 >= 0:
                    prev_index = self.model.index(current_index - 1)
                    self.thumbnail_list.setCurrentIndex(prev_index)
                    self.on_image_selected(prev_index)

    def on_image_selected(self, index: QModelIndex):
        """
        When a preview image is clicked, display it in the main image label.
        """
        selected_media = self.media_data[index.row()]
        self.load_image(selected_media)

    def load_image(self, media):
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
