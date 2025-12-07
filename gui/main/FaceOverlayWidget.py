from PyQt5.QtWidgets import QWidget, QFrame, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import face_detection


class FaceNameLabel(QLabel):
    """A styled label for displaying a person's name above their detection box."""

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.full_name = name
        self._set_formatted_text(name)
        self._apply_style()

    def _set_formatted_text(self, name: str):
        """Set text with HTML to force green color (bypasses theme palette)."""
        # Split at last space for two-line display
        surname_index = name.rfind(" ")
        if surname_index != -1:
            formatted = name[:surname_index] + "<br>" + name[surname_index + 1 :]
        else:
            formatted = name
        # HTML with inline style forces the color
        self.setText(f'<font color="#00c800">{formatted}</font>')

    def _apply_style(self):
        """Apply consistent styling to the name label."""
        self.setFont(QFont("Arial", 18))
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            """
            QLabel {
                background-color: rgba(0, 0, 0, 160);
                padding: 6px 12px;
                border-radius: 4px;
            }
            """
        )
        self.adjustSize()


class FaceBoxWidget(QFrame):
    """A styled frame representing a face detection bounding box."""

    def __init__(self, has_name: bool = True, parent=None):
        super().__init__(parent)
        self.has_name = has_name
        self._apply_style()

    def _apply_style(self):
        """Apply styling based on whether the face has a name assigned."""
        # Green for named faces, white for unnamed
        border_color = "rgb(0, 200, 0)" if self.has_name else "rgb(255, 255, 255)"
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: transparent;
                border: 3px solid {border_color};
            }}
            """
        )


class FaceOverlayWidget(QWidget):
    """
    Transparent overlay widget that displays face detection boxes and name labels.

    This widget is designed to be placed on top of a LabelImageViewer and manages
    the positioning of face boxes and name labels based on the image's current
    scale and position.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Make widget transparent and pass-through for mouse events
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        # Store detection data and child widgets
        self._detections = []  # List of [x, y, w, h, name, method]
        self._box_widgets = []
        self._label_widgets = []

        # Reference to image label for coordinate transformation
        self._image_label = None

    def set_image_label(self, image_label):
        """Set reference to the image label for coordinate calculations."""
        self._image_label = image_label

    def set_detections(self, people_detect: str | None, people: str | None):
        """
        Set face detection data from media fields.

        Args:
            people_detect: Comma-separated detection boxes as "x-y-w-h" format
            people: Comma-separated names corresponding to each detection
        """
        self.clear_overlays()

        if not people_detect or not people:
            return

        try:
            self._detections = face_detection.build_detections_with_names(
                people_detect, people
            )
            self._detections = face_detection.preprocess_detections(self._detections)
            self._create_overlay_widgets()
        except Exception:
            # If parsing fails, just show nothing
            self._detections = []

    def clear_overlays(self):
        """Remove all overlay widgets."""
        for widget in self._box_widgets + self._label_widgets:
            if widget:
                widget.deleteLater()
        self._box_widgets.clear()
        self._label_widgets.clear()
        self._detections.clear()

    def _create_overlay_widgets(self):
        """Create box and label widgets for each detection."""
        for detection in self._detections:
            x, y, w, h, name, method = detection

            # Create box widget
            has_name = bool(name)
            box = FaceBoxWidget(has_name=has_name, parent=self)
            self._box_widgets.append(box)

            # Create label widget only if there's a name
            if name:
                label = FaceNameLabel(name, parent=self)
                self._label_widgets.append(label)
            else:
                self._label_widgets.append(None)

        # Position all widgets
        self.update_positions()

    def update_positions(self):
        """Update positions of all overlay widgets based on current image scale."""
        if not self._image_label or not self._image_label.pixmap():
            return

        # Calculate scale factor
        # initial_scale is set in fit_to_window to scale image to viewport
        # scale_modifier adds zoom on top of that
        scale = self._image_label.initial_scale * (self._image_label.scale_modifier + 1)

        for i, detection in enumerate(self._detections):
            x, y, w, h, name, _ = detection

            # Transform coordinates from image space to widget space
            screen_x = int(x * scale)
            screen_y = int(y * scale)
            screen_w = int(w * scale)
            screen_h = int(h * scale)

            # Position the box
            box = self._box_widgets[i]
            box.setGeometry(screen_x, screen_y, screen_w, screen_h)
            box.show()

            # Position the label (if exists)
            label = self._label_widgets[i]
            if label:
                label.adjustSize()
                label_w = label.width()
                label_h = label.height()

                # Default position: above the box, left-aligned with small offset
                label_x = screen_x + 4
                label_y = screen_y - label_h - 4

                # If label goes above the widget, move it below the box
                if label_y < 0:
                    label_y = screen_y + screen_h + 4

                # If label goes beyond right edge, shift left
                if label_x + label_w > self.width():
                    label_x = screen_x + screen_w - label_w - 4

                label.move(label_x, label_y)
                label.show()

    def resizeEvent(self, event):
        """Handle resize to reposition overlays."""
        super().resizeEvent(event)
        self.update_positions()

    def has_detections(self) -> bool:
        """Check if there are any active detections."""
        return len(self._detections) > 0
