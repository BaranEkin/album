from typing import Sequence
from PyQt5.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)
from PyQt5.QtCore import Qt, pyqtSignal

from data.orm import Album
from gui.constants import Constants

ALBUM_TAG_ROLE = Qt.UserRole


class FrameTreeAlbums(QFrame):
    selection_changed = pyqtSignal()

    def __init__(self, albums: Sequence[Album], include_children: bool = True):
        super().__init__()

        self.setFixedSize(600, 300)
        self._include_children = include_children

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignLeft)

        self._button_select_all = QPushButton(Constants.FILTER_SELECT_ALL_ALBUMS)
        self._button_select_all.setFixedSize(110, 22)
        self._button_select_all.clicked.connect(self._select_all)

        self._button_deselect_all = QPushButton(Constants.FILTER_DESELECT_ALL_ALBUMS)
        self._button_deselect_all.setFixedSize(140, 22)
        self._button_deselect_all.clicked.connect(self.clear_selection)

        button_layout.addWidget(self._button_select_all)
        button_layout.addWidget(self._button_deselect_all)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setSelectionMode(QTreeWidget.NoSelection)
        self._build_tree(albums)
        self.tree.itemChanged.connect(self._on_item_changed)

        self._layout.addLayout(button_layout)
        self._layout.addWidget(self.tree)

    def _build_tree(self, albums: Sequence[Album]):
        node_items: dict[str, QTreeWidgetItem] = {}
        sorted_albums = sorted(albums, key=lambda x: len(x.path))

        for album in sorted_albums:
            item = QTreeWidgetItem([album.name])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)
            item.setData(0, ALBUM_TAG_ROLE, album.tag)

            parent_path = album.path[: -len(album.tag)]
            parent_tag = parent_path[-3:] if parent_path else None

            if parent_tag and parent_tag in node_items:
                node_items[parent_tag].addChild(item)
            else:
                self.tree.addTopLevelItem(item)

            node_items[album.tag] = item

        self.tree.collapseAll()
        self._expand_top_level()

    def _expand_top_level(self):
        for i in range(self.tree.topLevelItemCount()):
            self.tree.topLevelItem(i).setExpanded(True)

    def _on_item_changed(self, item: QTreeWidgetItem, column: int):
        self.selection_changed.emit()

    def set_include_children(self, enabled: bool):
        self._include_children = enabled
        self.selection_changed.emit()

    def get_checked_count(self) -> int:
        return len(self._get_checked_items())

    def get_selected_album_groups(self) -> tuple[tuple[str, ...], ...]:
        checked_items = self._get_checked_items()
        if not checked_items:
            return (("",),)

        groups = []
        for item in checked_items:
            tags = [item.data(0, ALBUM_TAG_ROLE)]
            if self._include_children:
                self._collect_descendant_tags(item, tags)
            groups.append(tuple(tags))
        return tuple(groups)

    def _get_checked_items(self) -> list[QTreeWidgetItem]:
        checked = []
        iterator = self.tree.invisibleRootItem()
        self._walk_checked(iterator, checked)
        return checked

    def _walk_checked(
        self, parent: QTreeWidgetItem, result: list[QTreeWidgetItem]
    ):
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child.checkState(0) == Qt.Checked:
                result.append(child)
            self._walk_checked(child, result)

    @staticmethod
    def _collect_descendant_tags(item: QTreeWidgetItem, tags: list[str]):
        for i in range(item.childCount()):
            child = item.child(i)
            tags.append(child.data(0, ALBUM_TAG_ROLE))
            FrameTreeAlbums._collect_descendant_tags(child, tags)

    def _select_all(self):
        self.tree.blockSignals(True)
        self._set_all_check_state(Qt.Checked)
        self.tree.blockSignals(False)
        self.selection_changed.emit()

    def clear_selection(self):
        self.tree.blockSignals(True)
        self._set_all_check_state(Qt.Unchecked)
        self.tree.collapseAll()
        self._expand_top_level()
        self.tree.blockSignals(False)
        self.selection_changed.emit()

    def _set_all_check_state(self, state):
        root = self.tree.invisibleRootItem()
        self._walk_set_check(root, state)

    def _walk_set_check(self, parent: QTreeWidgetItem, state):
        for i in range(parent.childCount()):
            child = parent.child(i)
            child.setCheckState(0, state)
            self._walk_set_check(child, state)
