from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QCursor, QMouseEvent, QWheelEvent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .map_visu import MainWindow


class PannableScrollArea(QScrollArea):
    def __init__(self, parent: "MainWindow") -> None:
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
                )
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._drag_start: QPoint | None = None
        self._scroll_start: QPoint | None = None

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        """Handle zooming with the mouse wheel."""
        if event is None:
            return

        # Determine zoom direction
        angle = event.angleDelta().y()
        zoom_step = 1.1 if angle > 0 else 0.9

        # Access the MapWidget through the scroll area's widget()
        from .draw_map import MapWidget
        map_widget = self.widget()
        if isinstance(map_widget, MapWidget):
            map_widget.update_zoom(zoom_step)

        # Stop the event from scrolling the area vertically
        event.accept()

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        if event is None:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.globalPosition().toPoint()
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            if h_bar and v_bar:
                self._scroll_start = QPoint(h_bar.value(), v_bar.value())
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

    def mouseMoveEvent(
                self,
                event: QMouseEvent | None
            ) -> None:
        if (
                event is None or self._drag_start is None
                or self._scroll_start is None
                ):
            return

        delta = event.globalPosition().toPoint() - self._drag_start

        # Capture the scrollbars into variables
        h_bar = self.horizontalScrollBar()
        v_bar = self.verticalScrollBar()

        # Check if they exist and set values
        if h_bar and v_bar:
            h_bar.setValue(self._scroll_start.x() - delta.x())
            v_bar.setValue(self._scroll_start.y() - delta.y())

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        self._drag_start = None
        self._scroll_start = None
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
