from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QPen, QBrush, QPolygon,
    QConicalGradient, QFont
)
from PyQt6.QtCore import Qt, QPoint

if TYPE_CHECKING:
    from ..models.Map import Map
    from ..models.Hub import Hub


class MapWidget(QWidget):
    def __init__(
        self,
        canvas_width: int = 1600,
        canvas_height: int = 1600,
        padding: int = 100  # Increased base padding for edge labels
    ) -> None:
        super().__init__()
        self.base_width: int = canvas_width
        self.base_height: int = canvas_height
        self.zoom_level: float = 1.0
        self.base_padding: int = padding

        self._last_map_obj: Map | None = None

        self.label: QLabel = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self._init_canvas()

    def _init_canvas(self) -> None:
        canvas: QPixmap = QPixmap(self.base_width, self.base_height)
        canvas.fill(Qt.GlobalColor.white)
        self.label.setPixmap(canvas)
        self.label.setFixedSize(self.base_width, self.base_height)

    def update_zoom(self, step: float) -> None:
        new_zoom: float = self.zoom_level * step
        # Allow deeper zoom to spread hubs more
        self.zoom_level = max(0.5, min(new_zoom, 15.0))

        new_w: int = int(self.base_width * self.zoom_level)
        new_h: int = int(self.base_height * self.zoom_level)

        self.label.setFixedSize(new_w, new_h)
        self.setFixedSize(new_w, new_h)

        if self._last_map_obj:
            self.draw_map(self._last_map_obj)

    def _draw_smart_label(
        self, painter: QPainter, name: str, pos: QPoint, center: QPoint
    ) -> None:
        # CAP FONT SIZE: Growing text too big is what causes the "glitch" look
        # Text starts at 9pt and caps at 14pt regardless of zoom
        font_size: int = min(14, max(8, int(9 + self.zoom_level)))
        painter.setFont(QFont("Arial", font_size, QFont.Weight.Bold))

        metrics = painter.fontMetrics()
        text_w = metrics.horizontalAdvance(name)
        text_h = metrics.height()

        # Margin scales so text stays clear of the hub
        margin = int(12 * self.zoom_level)

        # Calculate target position based on quadrant
        if pos.x() >= center.x():
            target_x = pos.x() + margin
        else:
            target_x = pos.x() - margin - text_w

        if pos.y() >= center.y():
            target_y = pos.y() + margin + (text_h // 2)
        else:
            target_y = pos.y() - margin

        # White Halo for readability
        painter.setPen(QPen(QColor(255, 255, 255, 200), 3))
        painter.drawText(target_x, target_y, name)

        # Actual Text
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(target_x, target_y, name)

    def draw_map(self, map_obj: Map) -> None:
        self._last_map_obj = map_obj
        all_hubs: list[Hub] = [
                *map_obj.hubs, map_obj.start_hub, map_obj.end_hub
                ]
        if not all_hubs:
            return

        # 1. Bounds
        min_x = min(hub.x for hub in all_hubs)
        max_x = max(hub.x for hub in all_hubs)
        min_y = min(hub.y for hub in all_hubs)
        max_y = max(hub.y for hub in all_hubs)

        map_w = float(max_x - min_x) if max_x != min_x else 1.0
        map_h = float(max_y - min_y) if max_y != min_y else 1.0

        curr_w = self.label.width()
        curr_h = self.label.height()

        # Use large padding that grows with zoom to keep labels in view
        dyn_padding = self.base_padding * self.zoom_level

        draw_w = float(curr_w - (dyn_padding * 2))
        draw_h = float(curr_h - (dyn_padding * 2))

        scale = min(draw_w / map_w, draw_h / map_h)
        off_x = (curr_w - (map_w * scale)) / 2 - (min_x * scale)
        off_y = (curr_h - (map_h * scale)) / 2 - (min_y * scale)

        canvas = QPixmap(curr_w, curr_h)
        canvas.fill(Qt.GlobalColor.white)
        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        def tr(x: float, y: float) -> QPoint:
            return QPoint(int(x * scale + off_x), int(y * scale + off_y))

        center_pt = QPoint(curr_w // 2, curr_h // 2)

        # 2. Draw Connections (Thinner lines look better at high zoom)
        painter.setPen(QPen(QColor(220, 220, 220), 2))
        for conn in map_obj.connections:
            painter.drawLine(tr(conn.hub1.x, conn.hub1.y),
                             tr(conn.hub2.x, conn.hub2.y))

        # 3. Draw Hubs & Labels
        for hub in all_hubs:
            pos = tr(hub.x, hub.y)
            self._draw_hub_at(painter, hub, pos)
            self._draw_smart_label(painter, hub.name, pos, center_pt)

        painter.end()
        self.label.setPixmap(canvas)

    def _draw_hub_at(self, painter: QPainter, hub: Hub, pos: QPoint) -> None:
        # Hub size scales, but we cap it so it doesn't dominate the screen
        size: int = int(min(60, 20 * self.zoom_level))
        half: int = size // 2

        color_val = hub.color.value if hub.color else None
        brush = self._get_hub_brush(color_val, pos)

        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(brush)
        x, y = pos.x(), pos.y()
        h_type = hub.hub_type.value

        if h_type == "normal":
            painter.drawEllipse(x - half, y - half, size, size)
        elif h_type == "priority":
            pts = [QPoint(x, y - half), QPoint(x - half, y + half),
                   QPoint(x + half, y + half)]
            painter.drawPolygon(QPolygon(pts))
        elif h_type == "restricted":
            painter.drawRect(x - half, y - half, size, size)
        elif h_type == "blocked":
            p_col = QColor("red") if color_val == "rainbow" else brush.color()
            painter.setPen(QPen(p_col, max(2, int(3 * self.zoom_level))))
            painter.drawLine(x - half, y - half, x + half, y + half)
            painter.drawLine(x + half, y - half, x - half, y + half)

    def _get_hub_brush(self, color_val: str | None, pos: QPoint) -> QBrush:
        if color_val == "rainbow":
            gradient = QConicalGradient(float(pos.x()), float(pos.y()), 0.0)
            stops = [
                (0.0, "red"), (0.16, "orange"), (0.33, "yellow"),
                (0.5, "green"), (0.66, "blue"), (0.83, "purple"), (1.0, "red")
            ]
            for s, c in stops:
                gradient.setColorAt(s, QColor(c))
            return QBrush(gradient)
        return QBrush(QColor(color_val if color_val else "black"))
