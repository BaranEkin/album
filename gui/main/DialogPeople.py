from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QApplication,
    QPushButton,
    QScrollArea,
    QWidget,
)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
import platform


class PersonButton(QPushButton):
    """A button representing a person in the list with hover/click signals."""

    hovered = pyqtSignal(int)  # Emits index on hover enter
    toggled_person = pyqtSignal(int)  # Emits index on click

    def __init__(self, name: str, index: int, parent=None):
        super().__init__(name, parent)
        self.index = index
        self.is_toggled = False
        self.setCheckable(True)
        self._apply_style()
        self.clicked.connect(self._on_clicked)

    def _apply_style(self):
        """Apply styling based on toggle state."""
        self.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #00c800;
                font-family: Arial;
                font-size: 16px;
                text-align: left;
                padding: 8px 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 200, 0, 40);
            }
            QPushButton:checked {
                background-color: rgba(0, 200, 0, 80);
                font-weight: bold;
            }
            """
        )

    def enterEvent(self, event):
        self.hovered.emit(self.index)
        super().enterEvent(event)

    def _on_clicked(self):
        self.is_toggled = self.isChecked()
        self.toggled_person.emit(self.index)


class DialogPeople(QDialog):
    # Signal emitted when dialog is closed by user (X button)
    closed_by_user = pyqtSignal()
    # Signals for overlay interaction
    person_hovered = pyqtSignal(int)  # index of hovered person
    person_unhovered = pyqtSignal()  # mouse left all buttons
    person_toggled = pyqtSignal(set)  # set of toggled indices (empty = all)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Use Tool flag for non-blocking floating window
        if platform.system() == "Linux":
            # Wayland needs different flags
            self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        else:
            self.setWindowFlags(Qt.Tool | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        self.setWindowTitle("Kişiler")
        self.setFixedSize(250, 250)

        self._people_names = []
        self._person_buttons = []
        self._toggled_indices = set()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Scroll area for buttons
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")

        # Container for buttons - no spacing to avoid hover gaps
        self.button_container = QWidget()
        self.button_layout = QVBoxLayout(self.button_container)
        self.button_layout.setSpacing(0)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.button_container)
        layout.addWidget(self.scroll_area)

        # Track if close was triggered programmatically
        self._closing_programmatically = False

    def set_people(self, people_names: list[str]):
        """Update the displayed people list with interactive buttons."""
        # Clear existing buttons
        for btn in self._person_buttons:
            btn.deleteLater()
        self._person_buttons.clear()
        self._toggled_indices.clear()
        self._people_names = people_names

        # Create new buttons
        for i, name in enumerate(people_names):
            btn = PersonButton(name, i, self.button_container)
            btn.hovered.connect(self._on_person_hovered)
            btn.toggled_person.connect(self._on_person_toggled)
            self.button_layout.addWidget(btn)
            self._person_buttons.append(btn)

    def set_people_from_string(self, people_str: str):
        """Update the displayed people list from comma-separated string."""
        if people_str:
            names = [n.strip() for n in people_str.split(",") if n.strip()]
        else:
            names = []
        self.set_people(names)

    def _on_person_hovered(self, index: int):
        """Handle hover on a person button."""
        # Only emit highlight if no toggles are active
        if not self._toggled_indices:
            self.person_hovered.emit(index)

    def _on_person_toggled(self, index: int):
        """Handle toggle of a person button."""
        btn = self._person_buttons[index]
        if btn.is_toggled:
            self._toggled_indices.add(index)
        else:
            self._toggled_indices.discard(index)

        # Emit the current set of toggled indices
        self.person_toggled.emit(self._toggled_indices.copy())

    def reset_state(self):
        """Reset all toggles and highlights."""
        self._toggled_indices.clear()
        for btn in self._person_buttons:
            btn.setChecked(False)
            btn.is_toggled = False
        self.person_toggled.emit(set())

    def show_at_position(self):
        """Show the dialog at its calculated position."""
        self.calculate_position()
        self.show()

    def close_programmatically(self):
        """Close the dialog without emitting closed_by_user signal."""
        self._closing_programmatically = True
        self.close()
        self._closing_programmatically = False

    def closeEvent(self, event):
        """Handle close event - emit signal if closed by user (X button)."""
        if not self._closing_programmatically:
            self.closed_by_user.emit()
        super().closeEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leaving the dialog - clear highlight."""
        if not self._toggled_indices:
            self.person_unhovered.emit()
        super().leaveEvent(event)

    def calculate_position(self):
        """Calculate and set the position of the dialog at the bottom right of the parent or screen."""
        # Get screen geometry
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # If we have a parent, position relative to it
        if self.parent() and self.parent().isVisible():
            # For Wayland, we need to use global position
            parent_global_pos = self.parent().mapToGlobal(QPoint(0, 0))
            parent_width = self.parent().width()
            parent_height = self.parent().height()

            # Calculate position - bottom right with clearance
            pos_x = parent_global_pos.x() + parent_width - self.width() - 100
            pos_y = parent_global_pos.y() + parent_height - self.height() - 200
        else:
            # No parent, position at bottom right of screen
            pos_x = screen_geometry.right() - self.width() - 100
            pos_y = screen_geometry.bottom() - self.height() - 100

        # Make sure we're on screen
        pos_x = max(
            screen_geometry.left(), min(pos_x, screen_geometry.right() - self.width())
        )
        pos_y = max(
            screen_geometry.top(), min(pos_y, screen_geometry.bottom() - self.height())
        )

        # Move the dialog to the calculated position
        self.move(pos_x, pos_y)
