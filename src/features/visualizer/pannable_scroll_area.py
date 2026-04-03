from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QCursor
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

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.globalPosition().toPoint()
            self._scroll_start = QPoint(
                self.horizontalScrollBar().value(),
                self.verticalScrollBar().value()
            )
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

    def mouseMoveEvent(self, event) -> None:
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

    def mouseReleaseEvent(self, event) -> None:
        self._drag_start = None
        self._scroll_start = None
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
