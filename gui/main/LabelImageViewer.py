from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint, QDateTime
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
        if self.scale_modifier < 5.0:
            self.scale_modifier += 0.5
        self.update_image_size(click_pos)

    def zoom_out(self, click_pos):
        if self.scale_modifier >= 1.0:
            self.scale_modifier -= 1.0
        elif self.scale_modifier > 0:
            self.scale_modifier = 0
        self.update_image_size(click_pos)

    def update_image_size(self, click_pos):
        if not self.pixmap():
            return

        # Calculate the new scale factor
        scale_factor = self.initial_scale * (self.scale_modifier + 1)

        # Store current QLabel dimensions
        old_width = self.width()
        old_height = self.height()

        # Calculate new QLabel dimensions
        new_width = self.original_size.width() * scale_factor
        new_height = self.original_size.height() * scale_factor

        # Access the scrollbars
        horizontal_scroll = self.scroll_area.horizontalScrollBar()
        vertical_scroll = self.scroll_area.verticalScrollBar()

        # Calculate the relative position of the clicked pixel within the QLabel
        rel_x = (horizontal_scroll.value() + click_pos.x()) / old_width
        rel_y = (vertical_scroll.value() + click_pos.y()) / old_height

        # Update QLabel size
        self.setFixedSize(int(new_width), int(new_height))

        # Calculate the new scroll positions based on the relative position
        new_h_scroll = int(rel_x * new_width - click_pos.x())
        new_v_scroll = int(rel_y * new_height - click_pos.y())

        # Clamp scroll values to ensure they stay within valid bounds
        new_h_scroll = max(0, min(new_h_scroll, horizontal_scroll.maximum()))
        new_v_scroll = max(0, min(new_v_scroll, vertical_scroll.maximum()))

        # Update the scrollbar positions
        horizontal_scroll.setValue(new_h_scroll)
        vertical_scroll.setValue(new_v_scroll)

