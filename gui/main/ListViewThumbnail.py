from PyQt5.QtWidgets import QListView, QMenu, QAction


class ListViewThumbnail(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def contextMenuEvent(self, event):
        # Get the index of the item clicked on
        index = self.indexAt(event.pos())

        # Only show the context menu if a valid item is clicked
        if index.isValid():
            # Create the context menu
            context_menu = QMenu(self)

            # Add actions to the context menu
            action_select_all = QAction("Hepsini seç", self)
            action_select_all.triggered.connect(lambda: self.parent.select_all())
            context_menu.addAction(action_select_all)

            action_deselect_all = QAction("Hiçbirini seçme", self)
            action_deselect_all.triggered.connect(lambda: self.parent.clear_selection())
            context_menu.addAction(action_deselect_all)

            action_reverse_selection = QAction("Seçimi tersine çevir", self)
            action_reverse_selection.triggered.connect(
                lambda: self.parent.reverse_selection()
            )
            context_menu.addAction(action_reverse_selection)

            context_menu.addSeparator()

            action_reorder_date = QAction(
                "Aynı güne ait medyaları yeniden sırala...", self
            )
            action_reorder_date.triggered.connect(
                lambda: self.parent.reorder_date(index)
            )
            context_menu.addAction(action_reorder_date)

            context_menu.addSeparator()

            action_edit_bulk = QAction("Seçili medyaları toplu düzenle...", self)
            action_edit_bulk.setEnabled(False)
            action_edit_bulk.triggered.connect(
                lambda: self.parent.on_bulk_edit_selected()
            )
            context_menu.addAction(action_edit_bulk)

            action_export_media = QAction("Seçili medyaları dışa aktar...", self)
            action_export_media.setEnabled(False)
            action_export_media.triggered.connect(
                lambda: self.parent.on_export_selected()
            )
            context_menu.addAction(action_export_media)

            context_menu.addSeparator()

            action_add_to_list = QAction("Seçili medyaları bir listeye ekle...", self)
            action_add_to_list.setEnabled(False)
            action_add_to_list.triggered.connect(
                lambda: self.parent.add_selection_to_list()
            )
            context_menu.addAction(action_add_to_list)

            action_remove_from_list = QAction(
                "Seçili medyaları bu listeden çıkar", self
            )
            action_remove_from_list.setEnabled(False)
            action_remove_from_list.triggered.connect(
                lambda: self.parent.remove_selection()
            )
            context_menu.addAction(action_remove_from_list)

            if self.parent.selected_rows:
                action_add_to_list.setEnabled(True)
                action_edit_bulk.setEnabled(True)
                action_export_media.setEnabled(True)

                if self.parent.media_list_name:
                    action_remove_from_list.setEnabled(True)

            # Show the context menu at the position of the right-click event
            context_menu.exec_(event.globalPos())
