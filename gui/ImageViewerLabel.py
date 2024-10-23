from PyQt5.QtWidgets import QLabel, QDialog
from PyQt5.QtCore import Qt, QPoint, QDateTime
from MediaLoader import MediaLoader
from gui.DialogDownload import DialogDownload


class ImageViewerLabel(QLabel):
    def __init__(self, scroll_area, media_loader: MediaLoader, parent=None):
        super(ImageViewerLabel, self).__init__(parent)
        self.scroll_area = scroll_area
        self.initial_scale = 1.0
        self.scale_modifier = 0
        self.original_size = None
        self.setScaledContents(True)

        self.is_panning = False  
        self.pan_start_position = QPoint()  
        self.mouse_press_time = QDateTime.currentDateTime()

        self.is_image = True
        self.media_loader = media_loader
        self.current_media_key = None

    def mousePressEvent(self, event):
        if self.is_image:
            if event.button() == Qt.LeftButton:
                # Record the time of mouse press to differentiate between click and drag
                self.mouse_press_time = QDateTime.currentDateTime()

                # Start the panning process if the image is large enough to be panned
                if self.size().width() > self.scroll_area.width() or self.size().height() > self.scroll_area.height():
                    self.is_panning = True
                    self.pan_start_position = event.globalPos()
                    self.horizontal_scroll_start = self.scroll_area.horizontalScrollBar().value()
                    self.vertical_scroll_start = self.scroll_area.verticalScrollBar().value()

            
            elif event.button() == Qt.RightButton:
                self.zoom_out(event.pos())
        
        else:
            if self.media_loader.check_video_audio(self.current_media_key):
                self.media_loader.play_video_audio_from_local(self.current_media_key)
            else:
                self.show_download_dialog(self.media_loader, self.current_media_key)

    def mouseMoveEvent(self, event):
        if self.is_image:
            if self.is_panning:
                self.setCursor(Qt.ClosedHandCursor)

                # Calculate the distance the mouse moved
                delta = event.globalPos() - self.pan_start_position

                # Scroll the scroll area based on the delta
                self.scroll_area.horizontalScrollBar().setValue(self.horizontal_scroll_start - delta.x())
                self.scroll_area.verticalScrollBar().setValue(self.vertical_scroll_start - delta.y())

    def mouseReleaseEvent(self, event):
        if self.is_image:
            if event.button() == Qt.LeftButton:
                self.unsetCursor()
                # If the time difference is short enough, consider it a click for zoom
                time_diff = self.mouse_press_time.msecsTo(QDateTime.currentDateTime())
                if time_diff < 200:
                    self.zoom_in(event.pos())  
                
                elif self.is_panning:
                    self.is_panning = False
                
    def zoom_in(self, click_pos):
        if self.scale_modifier < 5.0:
            self.scale_modifier += 0.5
        self.update_image_size(click_pos)

    def zoom_out(self, click_pos):
        if self.scale_modifier >= 1.0:
            self.scale_modifier -= 1.0
        elif self.scale_modifier > 0:
            self.scale_modifier = 0
        self.update_image_size(click_pos)

    def show_download_dialog(self, media_loader, media_key):
        dialog = DialogDownload(media_loader, media_key)
        dialog.exec_()


    def update_image_size(self, click_pos):
        if not self.pixmap():
            return

        scaling_factor = self.initial_scale * (self.scale_modifier + 1)

        # Scale the image based on the new scale factor
        new_width = self.original_size.width() * scaling_factor
        new_height = self.original_size.height() * scaling_factor

        # Update QLabel size
        self.setFixedSize(new_width, new_height)

        # Adjust the scroll area to center on the click position
        self.scroll_area.parent().parent().adjust_scroll_area(click_pos, scaling_factor)
