from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QFrame, QWidget, QVBoxLayout, QCheckBox

from data.orm import Album


class FrameTree(QFrame):
    def __init__(self, albums: List[Album]):
        super().__init__()

        self.setFixedSize(550,350)
        self.layout = QVBoxLayout(self)

        self.albums = albums
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)

        self.checkbox_include_child = QCheckBox("Alt albümleri dahil et")
        
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

        self.tree.itemSelectionChanged.connect(self.get_selected_albums)
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.checkbox_include_child)


    def get_selected_albums(self):
            selected_items = self.tree.selectedItems()
            if selected_items:
                selected_item = selected_items[0]
                if self.checkbox_include_child.isChecked():
                    return (selected_item.text(0),)
                
                with_child = []
                current_item = selected_item
                while current_item:
                    with_child.append(current_item.text(0))  
                    current_item = current_item.child()

                return tuple(with_child)


