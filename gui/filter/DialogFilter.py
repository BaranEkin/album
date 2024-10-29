from PyQt5.QtWidgets import (QDialog, QVBoxLayout)
from PyQt5.QtGui import QIcon

from data.data_manager import DataManager
from data.media_filter import MediaFilter
from gui.filter.FrameFilter import FrameFilter
from gui.filter.FrameTreeAlbums import FrameTreeAlbums


class DialogFilter(QDialog):
    def __init__(self, data_manager: DataManager):
        super().__init__()

        self.data_manager = data_manager
        self.albums = self.data_manager.get_all_albums()
        self.media_list = []

        self.frame_tree = FrameTreeAlbums(self.albums)
        self.frame_filter = FrameFilter()
        self.frame_filter.search_button.clicked.connect(self.filter_media)
        
        
        layout = QVBoxLayout()
        layout.addWidget(self.frame_tree)
        layout.addWidget(self.frame_filter)
        self.setLayout(layout)
        self.setWindowTitle("Süzgeç")
        self.setWindowIcon(QIcon("res/icons/Filter-2--Streamline-Sharp-Gradient--Free.png"))

    
    def update_albums(self):
        self.albums = self.data_manager.get_all_albums()
    
    def build_filter(self) -> MediaFilter:
        media_filter = MediaFilter(
            albums=self.frame_tree.get_selected_albums(),
            title=self.frame_filter.get_title(),
            location=self.frame_filter.get_location(),
            people=self.frame_filter.get_people(),
            people_count_range=self.frame_filter.get_people_count_range(),
            file_type=self.frame_filter.get_file_type(),
            file_ext=self.frame_filter.get_ext(),
            tags=self.frame_filter.get_tags(),
            date_range=self.frame_filter.get_date_range(),
            days=self.frame_filter.get_days(),
            months=self.frame_filter.get_months(),
            years=self.frame_filter.get_years(),
            days_of_week=self.frame_filter.get_days_of_week(),
            sort=self.frame_filter.get_sort()
        )

        return media_filter
    
    def filter_media(self):
        media_filter = self.build_filter()
        self.media_list = self.data_manager.get_filtered_media(media_filter)
        self.accept()

    