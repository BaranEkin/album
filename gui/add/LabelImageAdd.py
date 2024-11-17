from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QImage, QMouseEvent
from PyQt5.QtCore import Qt, QSize

from gui.add.DialogAssignPerson import DialogAssignPerson


class LabelImageAdd(QLabel):
    def __init__(self, people_list, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.people_list = people_list
        self.start_pixel = None
        self.original_image_size = None
        self.displayed_pixmap_size = QSize(800, 500)
        self.detections_with_names = []

    def set_image(self, image_path: str):

        try:
            image = QImage(image_path)
            self.original_image_size = image.size()  # Store the original size (width, height)

            pixmap = QPixmap.fromImage(image)
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled_pixmap)  # Set the scaled pixmap in the QLabel

            self.displayed_pixmap_size = scaled_pixmap.size()  # Store the displayed pixmap size
        except Exception as e:
            print(f"EXCEPTION: {e}")

    def calculate_clicked_pixel(self, event_x, event_y):
        # Get the size of the displayed pixmap (scaled size)
        displayed_size = self.displayed_pixmap_size

        # Calculate the margins/padding if the image is smaller than the label
        margin_x = (self.width() - displayed_size.width()) // 2
        margin_y = (self.height() - displayed_size.height()) // 2

        # Check if the mouse click is inside the image area (exclude padding)
        if margin_x <= event_x <= (margin_x + displayed_size.width()) and \
                margin_y <= event_y <= (margin_y + displayed_size.height()):
            # Calculate the position inside the displayed pixmap
            click_x = event_x - margin_x
            click_y = event_y - margin_y

            # Calculate scaling factors to map from displayed size to original image size
            scale_w = self.original_image_size.width() / displayed_size.width()
            scale_h = self.original_image_size.height() / displayed_size.height()

            # Calculate the original image coordinates
            original_x = int(click_x * scale_w)
            original_y = int(click_y * scale_h)

            return original_x, original_y

    def find_detection_index(self, x, y):
        for i, det in enumerate(self.detections_with_names):
            det_x, det_y, det_w, det_h, _, _ = det
            if det_x <= x <= det_x + det_w:
                if det_y <= y <= det_y + det_h:
                    return i
        return None

    def mousePressEvent(self, event: QMouseEvent):
        if self.pixmap():
            if event.button() == Qt.LeftButton:
                clicked_pixel_coords = self.calculate_clicked_pixel(event.x(), event.y())
                det_index = self.find_detection_index(
                    x=clicked_pixel_coords[0],
                    y=clicked_pixel_coords[1]
                )
                if det_index is not None:
                    person = self.detections_with_names[det_index][4]

                    person = self.show_assign_person_dialog(event.globalPos(), person)
                    self.detections_with_names[det_index][4] = person
                    self.parent().parent().update_identifications(self.detections_with_names)
            elif event.button() == Qt.RightButton:
                self.start_pixel = self.calculate_clicked_pixel(event.x(), event.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton:
            x, y = self.start_pixel
            release_x, release_y = self.calculate_clicked_pixel(event.x(), event.y())
            w, h = release_x - x, release_y - y
            if w > 0 and h > 0:
                person = self.show_assign_person_dialog(event.globalPos(), "")
                detection = [x, y, w, h, person, "manual"]
                self.detections_with_names.append(detection)
                self.parent().parent().update_identifications(self.detections_with_names)

    def show_assign_person_dialog(self, position, person):

        dialog = DialogAssignPerson(person, self.people_list, self)
        dialog.move(position)
        previous_input = dialog.input_field.text()
        if dialog.exec_() != 0:
            return dialog.input_field.text()
        else:
            return previous_input
