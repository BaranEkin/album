from typing import Sequence
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QFrame, QVBoxLayout, QCheckBox

from data.orm import Album


class FrameTreeAlbums(QFrame):
    def __init__(self, albums: Sequence[Album]):
        super().__init__()

        self.setFixedSize(600, 300)
        self.layout = QVBoxLayout(self)

        self.albums = albums
        self.selected_album_tags = []
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)

        self.checkbox_include_child = QCheckBox("Alt albümleri dahil et")
        self.checkbox_include_child.setChecked(True)

        # Create a dictionary to store the QTreeWidgetItem references by their tags
        node_items = {}

        # Iterate over the data sorted by path length to ensure parents are added before children
        sorted_data = sorted(self.albums, key=lambda x: len(x.path))

        for item in sorted_data:
            tag = item.tag
            name = item.name
            path = item.path

            # Create a new tree item for this node (displaying only the name)
            tree_item = QTreeWidgetItem([name])

            # Determine the parent tag by taking the path excluding the last 3 characters (last node tag)
            parent_path = path[:-len(tag)]
            parent_tag = parent_path[-3:] if parent_path else None

            # If a parent exists, add this as a child of the parent; otherwise, add as a root node
            if parent_tag and parent_tag in node_items:
                parent_item = node_items[parent_tag]
                parent_item.addChild(tree_item)
            else:
                self.tree.addTopLevelItem(tree_item)

            # Store this item in the dictionary for potential child nodes
            node_items[tag] = tree_item

        self.tree.collapseAll()
        self.expand_tree_default()
        self.tree.itemSelectionChanged.connect(self.on_select_albums)
        self.checkbox_include_child.stateChanged.connect(self.on_select_albums)
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.checkbox_include_child)

    def clear_selection(self):
        self.selected_album_tags = []
        self.checkbox_include_child.setChecked(True)
        self.tree.collapseAll()
        self.expand_tree_default()

    def get_selected_albums(self):
        return tuple(self.selected_album_tags) if self.selected_album_tags else ("",)
    
    def expand_tree_default(self):
        # Iterate over all top-level items (root items)
        for i in range(self.tree.topLevelItemCount()):
            root_item = self.tree.topLevelItem(i)
            root_item.setExpanded(True)
            
            # Collapse all children of this root item
            for j in range(root_item.childCount()):
                child_item = root_item.child(j)
                child_item.setExpanded(False)
        
    def on_select_albums(self):
        selected_items = self.tree.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            if not self.checkbox_include_child.isChecked():
                self.selected_album_tags = [self.get_album_tag(selected_item.text(0))]
                return

            # Gather text for the selected item and its children
            with_children = [selected_item.text(0)]

            def collect_children(item):
                for i in range(item.childCount()):
                    child = item.child(i)
                    with_children.append(child.text(0))
                    collect_children(child)  # Recursive call to collect nested children

            # Start collecting children from the selected item
            collect_children(selected_item)

            self.selected_album_tags = [self.get_album_tag(album_name) for album_name in with_children]
        
    def get_album_tag(self, album_name):
        for album in self.albums:
            if album.name == album_name:
                return album.tag
            
