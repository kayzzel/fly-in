from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QCursor, QMouseEvent, QWheelEvent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .map_visu import MainWindow


class PannableScrollArea(QScrollArea):
    """
        Description:
    A specialized QScrollArea that provides intuitive map navigation. It
    disables traditional scrollbars in favor of click-and-drag panning and
    mouse-wheel zooming, creating a seamless "infinite canvas" feel for
    exploring the simulation map.

        Attributes:
    __drag_start -> Stores the global screen coordinates where a mouse drag
                   began.
    __scroll_start -> Stores the initial scrollbar positions at the start of
                     a drag.
    """
    def __init__(self, parent: "MainWindow") -> None:
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
                )
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.__drag_start: QPoint | None = None
        self.__scroll_start: QPoint | None = None

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        """
            Description:
        Captures mouse wheel movement to calculate a zoom factor. It then
        delegates the scaling logic to the underlying MapWidget's
        update_zoom method.

            Parameters:
        event -> The wheel event containing information about the scroll
                 direction and delta.
        """
        if event is None:
            return

        angle = event.angleDelta().y()
        zoom_step = 1.1 if angle > 0 else 0.9

        from .draw_map import MapWidget
        map_widget = self.widget()
        if isinstance(map_widget, MapWidget):
            map_widget.update_zoom(zoom_step)

        event.accept()

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        """
            Description:
        Triggered when the user clicks the mouse. If the left button is pressed
        it capture the current position and changes the cursor to a closed hand
        to indicate that panning is active.

            Parameters:
        event -> The mouse press event containing the button type and position.
        """
        if event is None:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.__drag_start = event.globalPosition().toPoint()
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            if h_bar and v_bar:
                self.__scroll_start = QPoint(h_bar.value(), v_bar.value())
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        """
            Description:
        Updates the view position as the user drags the mouse. It calculates
        the movement distance (delta) relative to the start of the drag and
        adjusts the horizontal and vertical scrollbars accordingly to pan the
        map.

            Parameters:
        event -> The mouse movement event containing current position data.
        """
        if (
                event is None or self.__drag_start is None
                or self.__scroll_start is None
                ):
            return

        delta = event.globalPosition().toPoint() - self.__drag_start

        h_bar = self.horizontalScrollBar()
        v_bar = self.verticalScrollBar()

        if h_bar and v_bar:
            h_bar.setValue(self.__scroll_start.x() - delta.x())
            v_bar.setValue(self.__scroll_start.y() - delta.y())

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        """
            Description:
        Resets the drag state once the mouse button is released, returning
        the cursor to its default arrow shape.

            Parameters:
        event -> The mouse release event.
        """
        self.__drag_start = None
        self.__scroll_start = None
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
