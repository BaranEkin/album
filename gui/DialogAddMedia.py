import sys
import os
from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QVBoxLayout, 
                             QTreeView, QListWidget, QFrame, QFileSystemModel)
from PyQt5.QtCore import QDir, Qt
from PIL import Image

from gui.LabelImageAdd import LabelImageAdd
from gui.FrameAddInfo import FrameAddInfo

import face_detection


class DialogAddMedia(QDialog):
    def __init__(self):
        super().__init__()

        self.detections_with_names = []
        self.selected_media_path = ""
        self.setFixedSize(1450, 950)

        # Main layout of the dialog (horizontal layout for the 3 frames)
        main_layout = QHBoxLayout(self)

        # Create left frame: frame_navigation
        self.frame_navigation = QFrame(self)
        self.frame_navigation.setFixedWidth(300)  # Set fixed width for frame_navigation
        self.frame_navigation_layout = QVBoxLayout(self.frame_navigation)

        # Create and set up the folder tree view
        self.folder_tree = QTreeView(self.frame_navigation)
        self.file_system_model = QFileSystemModel(self.folder_tree)
        self.file_system_model.setRootPath('')  # Set the root path to show the entire filesystem
        self.file_system_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)  # Show only directories

        self.folder_tree.setModel(self.file_system_model)
        self.folder_tree.setRootIndex(self.file_system_model.index(''))  # Root path at the top
        self.folder_tree.setColumnWidth(0, 250)  # Set column width for the tree

        # Create the scrollable list widget for media files
        self.media_list = QListWidget(self.frame_navigation)

        # Add tree and list widgets to the frame_navigation layout
        self.frame_navigation_layout.addWidget(self.folder_tree)
        self.frame_navigation_layout.addWidget(self.media_list)

        # Add the frame_navigation to the main layout
        main_layout.addWidget(self.frame_navigation)

        # Create middle frame: frame_media
        self.frame_media = QFrame(self)
        self.frame_media.setFixedWidth(800)  # Set fixed width for frame_media
        self.frame_media_layout = QVBoxLayout(self.frame_media)
        self.frame_media.setContentsMargins(0, 0, 0, 0)

        # Create the clickable image label (top part of frame_media)
        self.image_label = LabelImageAdd(self.frame_media)
        self.image_label.setAlignment(Qt.AlignCenter)  # Center the image
        self.image_label.setFixedHeight(600)  # Set the fixed size for the image label
        self.frame_media_layout.addWidget(self.image_label)

        # Create the frame_details (bottom part of frame_media)
        self.frame_details = FrameAddInfo()
        self.frame_details.setFrameShape(QFrame.StyledPanel)
        self.frame_details.setFixedHeight(300)  # Set fixed height for frame_details
        self.frame_media_layout.addWidget(self.frame_details)

        # Add the frame_media to the main layout
        main_layout.addWidget(self.frame_media)

        # Create right frame: frame_action
        self.frame_action = QFrame(self)
        self.frame_action.setFixedWidth(300)  # Set fixed width for frame_action
        self.frame_action.setFrameShape(QFrame.StyledPanel)
        self.frame_action.setStyleSheet("background-color: red;")  # Set background color to red
        main_layout.addWidget(self.frame_action)

        # Set the layout for the dialog
        self.setLayout(main_layout)
        self.setWindowTitle('Media Dialog')

        # Connect the tree view selection change to update the media list
        self.folder_tree.selectionModel().selectionChanged.connect(self.on_folder_selected)

        # Connect the media list item click to print the file path
        self.media_list.itemClicked.connect(self.on_media_selected)

        # Variable to store the current folder path
        self.current_folder_path = ""

    def on_folder_selected(self, selected, deselected):
        # Get the currently selected folder
        index = self.folder_tree.selectionModel().currentIndex()
        folder_path = self.file_system_model.filePath(index)
        self.current_folder_path = folder_path  # Store the current folder path
        
        # Clear the media list and image label
        self.media_list.clear()
        self.image_label.clear()

        # Define the media file extensions
        image_extensions = [".png", ".jpg", ".jpeg"]
        video_extensions = [".mp4", ".avi", ".mov"]

        # List files from the selected directory and filter for images and videos
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    if any(file_name.lower().endswith(ext) for ext in image_extensions + video_extensions):
                        self.media_list.addItem(file_name)

    def on_media_selected(self, item):

        media_file_name = item.text()
        self.selected_media_path = os.path.join(self.current_folder_path, media_file_name)
        
        # Selected media is an image
        if media_file_name.lower().endswith((".png", ".jpg", ".jpeg",)):
            
            self.detect_people()
            self.draw_identifications()
            self.image_label.set_image("temp.jpg")
        
        # Selected media is a video
        else:
            self.image_label.clear()

    def detect_people(self):
        image = Image.open(self.selected_media_path)
        detections = face_detection.detect_people(image)
        self.detections_with_names = [det + [""] for det in detections]
        self.image_label.detections_with_names = self.detections_with_names
    
    def draw_identifications(self):
        image = Image.open(self.selected_media_path)
        image = face_detection.draw_identifications(image, self.detections_with_names)
        image.save("temp.jpg")

    def update_identifications(self, detections_with_names):
        self.detections_with_names = detections_with_names
        self.draw_identifications()
        self.image_label.set_image("temp.jpg")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = DialogAddMedia()
    dialog.show()
    sys.exit(app.exec_())
