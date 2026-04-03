from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import Qt


class MapWidget(QWidget):
    def __init__(self, canvas_width: int = 800, canvas_height: int = 600):
        super().__init__()
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

        self.label = QLabel()
        self.label.setAlignment(
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
                )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)

        self._init_canvas()
        self.draw_something()

    def _init_canvas(self) -> None:
        canvas = QPixmap(self.canvas_width, self.canvas_height)
        canvas.fill(Qt.GlobalColor.white)
        self.label.setPixmap(canvas)
        # Make the label (and thus widget) exactly the canvas size
        self.label.setFixedSize(self.canvas_width, self.canvas_height)

    def resize_canvas(self, width: int, height: int) -> None:
        """Resize the canvas, preserving existing content."""
        old_pixmap = self.label.pixmap()
        new_pixmap = QPixmap(width, height)
        new_pixmap.fill(Qt.GlobalColor.white)
        painter = QPainter(new_pixmap)
        painter.drawPixmap(0, 0, old_pixmap)  # copy old content
        painter.end()
        self.canvas_width = width
        self.canvas_height = height
        self.label.setFixedSize(width, height)
        self.label.setPixmap(new_pixmap)

    def draw_something(self) -> None:
        canvas = self.label.pixmap()
        painter = QPainter(canvas)
        painter.drawLine(10, 10, 300, 200)
        painter.end()
        self.label.setPixmap(canvas)
