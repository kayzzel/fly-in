from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QCursor, QMouseEvent
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
        self._drag_start = None
        self._scroll_start = None

    def mousePressEvent(self, event: QMouseEvent | None) -> None:
        if event is None:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.globalPosition().toPoint()
            horizontalScrollBar = self.horizontalScrollBar()
            verticalScrollBar = self.verticalScrollBar()
            if horizontalScrollBar and verticalScrollBar:
                self._scroll_start = QPoint(
                    horizontalScrollBar.value(),
                    verticalScrollBar.value()
                )
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        if event is None:
            return
        if (
                self._drag_start is not None and
                hasattr(self._scroll_start, "x") and
                hasattr(self._scroll_start, "y")
                ):
            delta = event.globalPosition().toPoint() - self._drag_start
            self.horizontalScrollBar().setValue(
                    self._scroll_start.x() - delta.x()
                    )
            self.verticalScrollBar().setValue(
                    self._scroll_start.y() - delta.y()
                    )

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        if event is None:
            return
        self._drag_start = None
        self._scroll_start = None
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
