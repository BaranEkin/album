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
    def __init__(self, row, image_path):
        super().__init__()
        self.row = row
        self.image_path = image_path
        self.signals = WorkerSignals()

    def run(self):
        # Load the image thumbnail
        pixmap = QPixmap(self.image_path).scaled(
            160, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        # Emit the signal with the row and pixmap
        self.signals.finished.emit(self.row, pixmap)


class ImageListModel(QAbstractListModel):
    def __init__(self, image_paths, parent=None):
        super().__init__(parent)
        self.thumbnail_paths = image_paths  # Full list of image paths
        self.image_paths = []  # Currently loaded image paths
        self.thumbnails = {}  # Cache of loaded thumbnails
        self.threadpool = QThreadPool()
        self.batch_size = 30000  # Adjust the batch size as needed
        self.loaded_count = 0  # Number of items currently loaded

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
            return self.image_paths[index.row()]
        elif role == Qt.SizeHintRole:
            return QSize(160, 100)
        return None

    def canFetchMore(self, parent=QModelIndex()):
        return self.loaded_count < len(self.thumbnail_paths)

    def fetchMore(self, parent=QModelIndex()):
        remaining = len(self.thumbnail_paths) - self.loaded_count
        items_to_fetch = min(self.batch_size, remaining)
        self.beginInsertRows(
            QModelIndex(), self.loaded_count, self.loaded_count + items_to_fetch - 1
        )
        self.image_paths.extend(
            self.thumbnail_paths[self.loaded_count : self.loaded_count + items_to_fetch]
        )
        self.loaded_count += items_to_fetch
        self.endInsertRows()

    def load_thumbnail(self, row):
        if row in self.thumbnails:
            return  # Thumbnail already loaded

        image_path = self.image_paths[row]
        runnable = ThumbnailLoaderRunnable(row, image_path)
        runnable.signals.finished.connect(self.on_thumbnail_loaded)
        self.threadpool.start(runnable)

    def on_thumbnail_loaded(self, row, pixmap):
        self.thumbnails[row] = pixmap
        index = self.index(row)
        self.dataChanged.emit(index, index, [Qt.DecorationRole])


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
    def __init__(self, thumbnail_paths, media_paths):
        super().__init__()
        self.media_loader = MediaLoader()
        self.thumbnail_paths = thumbnail_paths
        self.media_paths = media_paths

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
        self.image_label = QLabel()
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
        self.model = ImageListModel(self.thumbnail_paths)
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
        # Retrieve the image path from the model's data
        selected_image_path = self.media_paths[index.row()]
        self.load_image(selected_image_path)

    def load_image(self, image_path):
        """
        Load the selected image into the main display area.
        """
        image_key = image_path[10:].replace("\\", "/")
        q_image = self.media_loader.get_image(image_key)
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

            self.image_label.resize(new_width, new_height)

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)
        self.fit_to_window()
