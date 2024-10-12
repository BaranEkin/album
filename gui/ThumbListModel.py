from PyQt5.QtCore import (
    Qt,
    QSize,
    QThreadPool,
    QRunnable,
    pyqtSignal,
    QObject,
    QModelIndex,
    QAbstractListModel,
    QRect
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QStyledItemDelegate, QStyle


class ThumbListModel(QAbstractListModel):
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
