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
    QIODevice,
    QDataStream,
    QMimeData,
    QByteArray,
)
from PyQt5.QtGui import QPixmap, QBrush, QColor
from PyQt5.QtWidgets import QApplication, QStyledItemDelegate, QStyle


class ThumbnailSignal(QObject):
    loaded = pyqtSignal()


class ListModelThumbnail(QAbstractListModel):
    def __init__(self, thumbnail_keys, media_loader, is_reorder=False, parent=None):
        super().__init__(parent)
        self.media_loader = media_loader
        self.is_reorder = is_reorder
        self.thumbnail_keys = thumbnail_keys
        self.thumbnail_keys_loaded = []
        self.thumbnails = {}  # Cache of loaded thumbnails
        self.threadpool = QThreadPool()
        self.batch_size = 30000
        self.loaded_count = 0
        self.placeholder_pixmap = QPixmap(160, 80)
        self.placeholder_pixmap.fill(Qt.gray)
        self.signal = ThumbnailSignal()

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
                return self.placeholder_pixmap

        elif role == Qt.UserRole:
            return self.thumbnail_keys_loaded[index.row()]

        elif role == Qt.SizeHintRole:
            return QSize(160, 105)

        elif role == Qt.BackgroundRole:
            # Ask the MainWindow for selection state
            if index.row() in self.parent().selected_rows:
                return QBrush(QColor(200, 255, 0))  # Highlight selected items

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
            self.thumbnail_keys[self.loaded_count : self.loaded_count + items_to_fetch]
        )
        self.loaded_count += items_to_fetch
        self.endInsertRows()
        self.signal.loaded.emit()

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

    def flags(self, index):
        """Enable dragging and dropping for the thumbnails."""
        default_flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.isValid():
            # Allow dragging from valid indices
            return default_flags | Qt.ItemIsDragEnabled
        else:
            # Allow dropping only between items, not on top of them
            return default_flags | Qt.ItemIsDropEnabled

    def supportedDropActions(self):
        """Specify the drop actions supported by the model."""
        return Qt.MoveAction

    def mimeTypes(self):
        """Specify the MIME types supported by the model."""
        return ["application/x-qabstractitemmodeldatalist"]

    def mimeData(self, indexes):
        """Package the data for dragging."""
        mime_data = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.WriteOnly)

        for index in indexes:
            if index.isValid() and 0 <= index.row() < len(self.thumbnail_keys_loaded):
                stream.writeInt32(index.row())  # Only valid indices are written
            else:
                print(f"Skipping invalid index: {index.row()}")

        mime_data.setData("application/x-qabstractitemmodeldatalist", encoded_data)
        return mime_data

    def dropMimeData(self, data, action, row, column, parent):
        """Handle dropping an item into the list."""

        if action != Qt.MoveAction or not data.hasFormat(
            "application/x-qabstractitemmodeldatalist"
        ):
            print("Action not MoveAction or invalid MIME format.")
            return False

        # Reject drops directly ON an item (parent is valid when dropping ON)
        if parent.isValid():
            print("Dropping ON an item is disallowed.")
            return False

        # Decode the MIME data
        encoded_data = data.data("application/x-qabstractitemmodeldatalist")
        stream = QDataStream(encoded_data, QIODevice.ReadOnly)
        rows = []
        while not stream.atEnd():
            src_row = stream.readInt32()
            if 0 <= src_row < len(self.thumbnail_keys_loaded):  # Validate src_row
                rows.append(src_row)

        if not rows:
            return False

        rows.sort()

        # Adjust the drop row
        if row == -1:
            row = self.rowCount()  # Dropping at the end of the list

        if row > len(self.thumbnail_keys_loaded):
            row = len(self.thumbnail_keys_loaded)  # Prevent overflow

        # Collect the items to move
        items_to_move = [
            self.thumbnail_keys_loaded.pop(src_row) for src_row in reversed(rows)
        ]

        # Adjust the destination row for downward movement
        if row > rows[-1]:
            row -= len(items_to_move)

        # Insert the items at the new position
        for i, item in enumerate(items_to_move):
            self.thumbnail_keys_loaded.insert(row + i, item)

        # Update the full list to reflect the changes in loaded items
        self.thumbnail_keys = (
            self.thumbnail_keys_loaded
            + self.thumbnail_keys[len(self.thumbnail_keys_loaded) :]
        )

        # Reinitialize and reattach the model to the view
        parent_dialog = self.parent()
        parent_view = getattr(parent_dialog, "thumbnail_list", None)
        if parent_view:
            new_model = ListModelThumbnail(
                self.thumbnail_keys,
                self.media_loader,
                is_reorder=self.is_reorder,
                parent=parent_dialog,
            )
            # Keep the dialog's reference in sync with the view's model
            if hasattr(parent_dialog, "thumbnail_model"):
                parent_dialog.thumbnail_model = new_model
            parent_view.setModel(new_model)

        return True

    def moveRow(self, sourceParent, sourceRow, destinationParent, destinationRow):
        """Reorder the underlying thumbnail data."""
        if sourceRow == destinationRow or sourceRow < 0 or destinationRow < 0:
            return False

        self.beginMoveRows(
            sourceParent, sourceRow, sourceRow, destinationParent, destinationRow
        )

        item = self.thumbnail_keys_loaded.pop(sourceRow)
        self.thumbnail_keys_loaded.insert(
            destinationRow if destinationRow > sourceRow else destinationRow, item
        )

        self.endMoveRows()
        return True


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
        if q_image is not None:
            pixmap = QPixmap.fromImage(q_image).scaled(
                160, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            # Emit the signal with the row and pixmap
            self.signals.finished.emit(self.row, pixmap)
        else:
            placeholder_pixmap = QPixmap(160, 80)
            placeholder_pixmap.fill(Qt.gray)
            self.signals.finished.emit(self.row, placeholder_pixmap)


class ThumbnailDelegate(QStyledItemDelegate):
    def __init__(self, is_reorder=False):
        super().__init__()
        self.is_reorder = is_reorder

    def paint(self, painter, option, index):
        # Save the painter's state
        painter.save()

        # Check if the item is selected
        if self.is_reorder:
            is_selected = False
        else:
            is_selected = index.row() in index.model().parent().selected_rows

        # If selected, fill the background with yellow, otherwise use default behavior
        if is_selected:
            painter.fillRect(
                option.rect, QColor(255, 255, 0)
            )  # Yellow background for selected items
        elif option.state & QStyle.State_Selected:
            # Default selection behavior (blue highlight)
            painter.fillRect(option.rect, option.palette.highlight())

        # Draw the default item (background, selection, etc.)
        else:
            painter.fillRect(option.rect, option.palette.base())

        # Get the pixmap from the model and draw it centered
        pixmap = index.data(Qt.DecorationRole)
        if pixmap:
            item_rect = option.rect
            pixmap_size = pixmap.size()
            x = item_rect.x() + (item_rect.width() - pixmap_size.width()) / 2
            y = item_rect.y() + (item_rect.height() - pixmap_size.height()) / 2
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
