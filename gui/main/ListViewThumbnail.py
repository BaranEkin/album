from PyQt5.QtWidgets import QListView, QMenu, QAction, QVBoxLayout, QMainWindow
from PyQt5.QtCore import Qt, QPoint

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
            action_add_to_list = QAction("Seçili medyaları listeye Ekle...", self)
            
            action_add_to_list.setEnabled(False)
            action_add_to_list.triggered.connect(lambda: self.parent.ctrl_select_add())
            context_menu.addAction(action_add_to_list)

            action_remove_from_list = QAction("Seçili medyaları listeden Çıkar...", self)
            action_remove_from_list.setEnabled(False)
            action_remove_from_list.triggered.connect(lambda: self.parent.ctrl_select_remove())
            context_menu.addAction(action_remove_from_list)

            context_menu.addSeparator()

            action_select_all = QAction("Hepsini seç", self)
            action_select_all.triggered.connect(lambda: self.parent.ctrl_select_all())
            context_menu.addAction(action_select_all)

            action_deselect_all = QAction("Hiçbirini seçme", self)
            action_deselect_all.triggered.connect(lambda: self.parent.ctrl_select_clear())
            context_menu.addAction(action_deselect_all)

            action_reverse_selection = QAction("Seçimi tersine çevir", self)
            action_reverse_selection.triggered.connect(lambda: self.parent.ctrl_select_reverse())
            context_menu.addAction(action_reverse_selection)

            context_menu.addSeparator()

            action_reorder_date = QAction("Aynı güne ait medyaları yeniden sırala", self)
            action_reorder_date.triggered.connect(lambda: self.parent.reorder_date(index))
            context_menu.addAction(action_reorder_date)

            if self.parent.selected_rows:
                action_add_to_list.setEnabled(True)
                
                if self.parent.current_list_name:
                    action_remove_from_list.setEnabled(True)
                
            # Show the context menu at the position of the right-click event
            context_menu.exec_(event.globalPos())
