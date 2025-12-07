from PyQt5.QtWidgets import QWidget, QFrame, QLabel
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint
from PyQt5.QtGui import QFont, QPainter, QPen, QColor

import face_detection


class FaceNameLabel(QLabel):
    """A styled label for displaying a person's name above their detection box."""

    clicked = pyqtSignal(int)  # Emits detection index when clicked

    def __init__(
        self,
        name: str,
        detection_index: int = -1,
        interactive: bool = False,
        font_size: int = 18,
        parent=None,
    ):
        super().__init__(parent)
        self.full_name = name
        self.detection_index = detection_index
        self.interactive = interactive
        self.font_size = font_size
        self._set_formatted_text(name)
        self._apply_style()

        if interactive:
            self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if self.interactive and event.button() == Qt.LeftButton:
            self.clicked.emit(self.detection_index)
        else:
            super().mousePressEvent(event)

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
        self.setFont(QFont("Arial", self.font_size))
        self.setAlignment(Qt.AlignCenter)
        # Scale padding with font size
        pad_v = max(2, self.font_size // 3)
        pad_h = max(4, self.font_size // 2)
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: rgba(0, 0, 0, 160);
                padding: {pad_v}px {pad_h}px;
                border-radius: 4px;
            }}
            """
        )
        self.adjustSize()


class FaceBoxWidget(QFrame):
    """A styled frame representing a face detection bounding box."""

    clicked = pyqtSignal(int)  # Emits detection index when clicked

    def __init__(
        self,
        has_name: bool = True,
        detection_index: int = -1,
        interactive: bool = False,
        border_width: int = 3,
        parent=None,
    ):
        super().__init__(parent)
        self.has_name = has_name
        self.detection_index = detection_index
        self.interactive = interactive
        self.border_width = border_width
        self._apply_style()

        if interactive:
            self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if self.interactive and event.button() == Qt.LeftButton:
            self.clicked.emit(self.detection_index)
        else:
            super().mousePressEvent(event)

    def _apply_style(self):
        """Apply styling based on whether the face has a name assigned."""
        # Green for named faces, white for unnamed
        border_color = "rgb(0, 200, 0)" if self.has_name else "rgb(255, 255, 255)"
        hover_width = self.border_width + 1
        hover_style = (
            f"""
            QFrame:hover {{
                border: {hover_width}px solid {border_color};
                background-color: rgba(0, 200, 0, 30);
            }}
        """
            if self.interactive
            else ""
        )

        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: transparent;
                border: {self.border_width}px solid {border_color};
            }}
            {hover_style}
            """
        )


class FaceOverlayWidget(QWidget):
    """
    Transparent overlay widget that displays face detection boxes and name labels.

    This widget is designed to be placed on top of a LabelImageViewer and manages
    the positioning of face boxes and name labels based on the image's current
    scale and position.

    When interactive=True, boxes are clickable and users can draw new boxes.

    Args:
        interactive: Enable click/draw interactions
        font_size: Font size for name labels (default 18 for main window, use ~10 for dialogs)
        border_width: Border width for boxes (default 3 for main window, use ~2 for dialogs)
    """

    # Signals for interactive mode
    box_clicked = pyqtSignal(int, QPoint)  # detection index, global position
    box_drawn = pyqtSignal(
        int, int, int, int, QPoint
    )  # x, y, w, h in image coords, global pos

    def __init__(
        self,
        parent=None,
        interactive: bool = False,
        font_size: int = 18,
        border_width: int = 3,
    ):
        super().__init__(parent)

        self.interactive = interactive
        self.font_size = font_size
        self.border_width = border_width

        # Make widget transparent; only pass-through mouse events if not interactive
        if not interactive:
            self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.setMouseTracking(True)

        # Store detection data and child widgets
        self._detections = []  # List of [x, y, w, h, name, method]
        self._box_widgets = []
        self._label_widgets = []

        # Reference to image label for coordinate transformation
        self._image_label = None

        # Drawing state (for interactive mode)
        self._is_drawing = False
        self._draw_start = None  # Screen coordinates
        self._draw_current = None  # Screen coordinates

    def set_image_label(self, image_label):
        """Set reference to the image label for coordinate calculations."""
        self._image_label = image_label

    def set_detections(self, people_detect: str | None, people: str | None):
        """
        Set face detection data from media fields (for MainWindow).

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

    def set_detections_list(self, detections_with_names: list):
        """
        Set face detection data directly from a list (for Add/Edit dialogs).

        Args:
            detections_with_names: List of [x, y, w, h, name, method] entries
        """
        self.clear_overlays()
        self._detections = detections_with_names.copy() if detections_with_names else []
        self._create_overlay_widgets()

    def get_detections(self) -> list:
        """Return current detections list."""
        return self._detections

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
        for i, detection in enumerate(self._detections):
            x, y, w, h, name, method = detection

            # Create box widget
            has_name = bool(name)
            box = FaceBoxWidget(
                has_name=has_name,
                detection_index=i,
                interactive=self.interactive,
                border_width=self.border_width,
                parent=self,
            )
            if self.interactive:
                box.clicked.connect(self._on_box_clicked)
            self._box_widgets.append(box)

            # Create label widget only if there's a name
            if name:
                label = FaceNameLabel(
                    name,
                    detection_index=i,
                    interactive=self.interactive,
                    font_size=self.font_size,
                    parent=self,
                )
                if self.interactive:
                    label.clicked.connect(self._on_box_clicked)
                self._label_widgets.append(label)
            else:
                self._label_widgets.append(None)

        # Position all widgets
        self.update_positions()

    def _on_box_clicked(self, detection_index: int):
        """Handle box or label click in interactive mode."""
        global_pos = self.mapToGlobal(self.mapFromGlobal(self.cursor().pos()))
        self.box_clicked.emit(detection_index, global_pos)

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

    # === Interactive Drawing Support ===

    def _screen_to_image_coords(self, screen_x: int, screen_y: int):
        """Convert screen coordinates to image coordinates."""
        if not self._image_label or not self._image_label.pixmap():
            return None

        scale = self._image_label.initial_scale * (self._image_label.scale_modifier + 1)
        if scale <= 0:
            return None

        image_x = int(screen_x / scale)
        image_y = int(screen_y / scale)
        return image_x, image_y

    def mousePressEvent(self, event):
        """Handle mouse press for drawing new boxes (interactive mode only)."""
        if self.interactive and event.button() == Qt.RightButton:
            self._is_drawing = True
            self._draw_start = event.pos()
            self._draw_current = event.pos()
            self.update()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for live drawing preview."""
        if self._is_drawing:
            self._draw_current = event.pos()
            self.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release to complete drawing."""
        if self.interactive and event.button() == Qt.RightButton and self._is_drawing:
            self._is_drawing = False

            # Convert start and end to image coordinates
            start_img = self._screen_to_image_coords(
                self._draw_start.x(), self._draw_start.y()
            )
            end_img = self._screen_to_image_coords(
                self._draw_current.x(), self._draw_current.y()
            )

            if start_img and end_img:
                x = min(start_img[0], end_img[0])
                y = min(start_img[1], end_img[1])
                w = abs(end_img[0] - start_img[0])
                h = abs(end_img[1] - start_img[1])

                # Only emit if box has reasonable size
                if w > 10 and h > 10:
                    global_pos = event.globalPos()
                    self.box_drawn.emit(x, y, w, h, global_pos)

            self._draw_start = None
            self._draw_current = None
            self.update()
        else:
            super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        """Paint the drawing rectangle preview."""
        super().paintEvent(event)

        if self._is_drawing and self._draw_start and self._draw_current:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            # Draw rectangle with dashed green line
            pen = QPen(QColor(0, 200, 0), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(QColor(0, 200, 0, 30))

            rect = QRect(self._draw_start, self._draw_current).normalized()
            painter.drawRect(rect)

            painter.end()
