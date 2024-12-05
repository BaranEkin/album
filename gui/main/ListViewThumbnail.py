from PyQt5.QtWidgets import QListView, QMenu, QAction, QVBoxLayout, QMainWindow
from PyQt5.QtCore import Qt, QPoint

class ListViewThumbnail(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def contextMenuEvent(self, event):
        # Get the index of the item clicked on
        index = self.indexAt(event.pos())
        
        # Only show the context menu if a valid item is clicked
        if index.isValid():
            # Create the context menu
            context_menu = QMenu(self)

            # Add actions to the context menu
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.on_delete(index))  # Connect to delete slot
            context_menu.addAction(delete_action)

            add_to_playlist_action = QAction("Add to Playlist", self)
            add_to_playlist_action.triggered.connect(lambda: self.on_add_to_playlist(index))  # Connect to add-to-playlist slot
            context_menu.addAction(add_to_playlist_action)

            rename_action = QAction("Rename", self)
            rename_action.triggered.connect(lambda: self.on_rename(index))  # Connect to rename slot
            context_menu.addAction(rename_action)

            # Show the context menu at the position of the right-click event
            context_menu.exec_(event.globalPos())

    # Slots for each action
    def on_delete(self, index):
        print(f"Delete item at row {index.row()}")
        # Implement your delete logic here

    def on_add_to_playlist(self, index):
        print(f"Add item at row {index.row()} to playlist")
        # Implement your add-to
