from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint, QDateTime
from PyQt5.QtGui import QCursor
from media_loader import MediaLoader
from gui.main.DialogProcess import DialogProcess
from gui.message import show_message


class LabelImageViewer(QLabel):
    def __init__(self, scroll_area, media_loader: MediaLoader, parent=None):
        super(LabelImageViewer, self).__init__(parent)
        self.scroll_area = scroll_area
        self.initial_scale = 1.0
        self.scale_modifier = 0
        self.original_size = None
        self.setScaledContents(True)

        self.is_panning = False
        self.pan_start_position = QPoint()
        self.mouse_press_time = QDateTime.currentDateTime()
        self.vertical_scroll_start = None
        self.horizontal_scroll_start = None

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
                procceed = show_message(("Medya bilgisayarınızda bulunmadığı için bulut sisteminden indirilecek.\n"
                                         "Bu işlem internet hızınıza bağlı olarak biraz zaman alabilir.\n\n"
                                         "Devam etmek istiyot musunuz?"), is_question=True)
                if procceed:
                    # Show download dialog
                    dialog = DialogProcess(operation=self.media_loader.play_video_audio_from_cloud,
                                           operation_args=(self.current_media_key,),
                                           title="Medya İndirme İşlemi",
                                           message="İndirme işlemi devam ediyor...")
                    dialog.exec_()

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
        if self.scale_modifier < 6:
            self.scale_modifier += 1.0
        self.update_image_size(click_pos)

    def zoom_out(self, click_pos):
        if self.scale_modifier >= 2.0:
            self.scale_modifier -= 2.0
        elif self.scale_modifier > 0:
            self.scale_modifier = 0
        self.update_image_size(click_pos)

    
    def update_image_size(self, click_pos):
        if not self.pixmap():
            return

        viewport_width = self.scroll_area.viewport().width()
        viewport_height = self.scroll_area.viewport().height()

        # Calculate the new scale factor
        scale_factor = self.initial_scale * (self.scale_modifier + 1)

        # Store current QLabel dimensions
        old_width = self.width()
        old_height = self.height()

        # Calculate new QLabel dimensions
        new_width = self.original_size.width() * scale_factor
        new_height = self.original_size.height() * scale_factor

        # Calculate the relative click position in the old image
        rel_click_x = click_pos.x() / old_width
        rel_click_y = click_pos.y() / old_height

        # Update QLabel size
        self.setFixedSize(int(new_width), int(new_height))

        # Map the relative position to the new image size
        new_click_x = new_width * rel_click_x
        new_click_y = new_height * rel_click_y

        # Calculate the scroll position to center the clicked pixel
        scroll_x = new_click_x - viewport_width // 2
        scroll_y = new_click_y - viewport_height // 2

        # Clamp scroll positions to valid range based on the new dimensions
        max_scroll_x = max(0, new_width - viewport_width)
        max_scroll_y = max(0, new_height - viewport_height)

        # Explicitly synchronize the scrollbar ranges to prevent overshooting
        self.scroll_area.horizontalScrollBar().setRange(0, max_scroll_x)
        self.scroll_area.verticalScrollBar().setRange(0, max_scroll_y)

        # Recalculate and clamp scroll positions
        scroll_x = max(0, min(scroll_x, max_scroll_x))
        scroll_y = max(0, min(scroll_y, max_scroll_y))

        # Set the scrollbar positions
        self.scroll_area.horizontalScrollBar().setValue(scroll_x)
        self.scroll_area.verticalScrollBar().setValue(scroll_y)

        # Calculate the pixel's position within the viewport
        if new_width < viewport_width:
            actual_x = new_click_x + (viewport_width - new_width) // 2
        else:
            actual_x = new_click_x - self.scroll_area.horizontalScrollBar().value()

        if new_height < viewport_height:
            actual_y = new_click_y + (viewport_height - new_height) // 2
        else:
            actual_y = new_click_y - self.scroll_area.verticalScrollBar().value()

        # Get the global position of the viewport
        global_viewport_position = self.scroll_area.viewport().mapToGlobal(QPoint(0, 0))

        # Calculate the global position of the pixel in the viewport
        cursor_x = global_viewport_position.x() + actual_x
        cursor_y = global_viewport_position.y() + actual_y

        # Move the cursor to the calculated position
        QCursor.setPos(cursor_x, cursor_y)
