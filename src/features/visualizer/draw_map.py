from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import (
    QPixmap, QPainter, QColor, QPen, QBrush, QPolygon,
    QConicalGradient, QFont
)
from PyQt6.QtCore import Qt, QPoint

if TYPE_CHECKING:
    from ..map.Map import Map
    from ..map.Hub import Hub
    from ..map.Drone import Drone


class MapWidget(QWidget):
    def __init__(
        self,
        canvas_width: int = 1600,
        canvas_height: int = 1600,
        padding: int = 100
    ) -> None:
        super().__init__()
        self.base_width: int = canvas_width
        self.base_height: int = canvas_height
        self.zoom_level: float = 1.0
        self.base_padding: int = padding

        self._last_map_obj: Map | None = None
        self._current_step: int = 0  # Track current visualization step

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
        self.zoom_level = max(0.5, min(new_zoom, 15.0))

        new_w: int = int(self.base_width * self.zoom_level)
        new_h: int = int(self.base_height * self.zoom_level)

        self.label.setFixedSize(new_w, new_h)
        self.setFixedSize(new_w, new_h)

        if self._last_map_obj:
            self.draw_map(self._last_map_obj, self._current_step)

    def set_step(self, step: int) -> None:
        """Update the visualization to show drones at a specific step"""
        self._current_step = step
        if self._last_map_obj:
            self.draw_map(self._last_map_obj, step)

    def _draw_smart_label(
        self, painter: QPainter, name: str, pos: QPoint, center: QPoint
    ) -> None:
        font_size: int = min(14, max(8, int(9 + self.zoom_level)))
        painter.setFont(QFont("Arial", font_size, QFont.Weight.Bold))

        metrics = painter.fontMetrics()
        text_w = metrics.horizontalAdvance(name)
        text_h = metrics.height()

        margin = int(12 * self.zoom_level)

        if pos.x() >= center.x():
            target_x = pos.x() + margin
        else:
            target_x = pos.x() - margin - text_w

        if pos.y() >= center.y():
            target_y = pos.y() + margin + (text_h // 2)
        else:
            target_y = pos.y() - margin

        # White halo
        painter.setPen(QPen(QColor(255, 255, 255, 200), 3))
        painter.drawText(target_x, target_y, name)

        # Actual text
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(target_x, target_y, name)

    def draw_map(self, map_obj: Map, current_step: int = 0) -> None:
        """Draw the map with drones at the specified step"""
        self._last_map_obj = map_obj
        self._current_step = current_step

        all_hubs: list[Hub] = [
            *map_obj.hubs, map_obj.start_hub, map_obj.end_hub
        ]
        if not all_hubs:
            return

        # Calculate bounds
        min_x = min(hub.x for hub in all_hubs)
        max_x = max(hub.x for hub in all_hubs)
        min_y = min(hub.y for hub in all_hubs)
        max_y = max(hub.y for hub in all_hubs)

        map_w = float(max_x - min_x) if max_x != min_x else 1.0
        map_h = float(max_y - min_y) if max_y != min_y else 1.0

        curr_w = self.label.width()
        curr_h = self.label.height()

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

        # Draw connections
        painter.setPen(QPen(QColor(220, 220, 220), 2))
        for conn in map_obj.connections:
            painter.drawLine(
                tr(conn.hub1.x, conn.hub1.y),
                tr(conn.hub2.x, conn.hub2.y)
            )

        # Draw hubs
        for hub in all_hubs:
            pos = tr(hub.x, hub.y)
            self._draw_hub_at(painter, hub, pos)
            self._draw_smart_label(painter, hub.name, pos, center_pt)

        # Draw drone paths (trails)
        self._draw_drone_paths(painter, map_obj, current_step, tr)

        # Draw drones at current positions
        self._draw_drones(painter, map_obj, current_step, tr)

        painter.end()
        self.label.setPixmap(canvas)

    def _draw_drone_paths(
        self, painter: QPainter, map_obj: Map, current_step: int,
        tr: Callable[[float, float], QPoint]
    ) -> None:
        """Draw the path trails for each drone up to current step

        Shows trails including midpoints for restricted zone entries
        """
        for drone in map_obj.drones:
            if not drone.path or current_step == 0:
                continue

            # Draw path from start to current position
            path_points = []

            # Start position
            current_hub = map_obj.start_hub
            path_points.append(tr(current_hub.x, current_hub.y))

            # Add each position up to current step
            for i in range(min(current_step, len(drone.path))):
                hub = drone.path[i]

                # Check if this is a restricted zone entry
                next_hub = None

                if i + 1 < len(drone.path):
                    next_hub = drone.path[i + 1]

                if (
                        hub is None and next_hub and
                        next_hub is not None and
                        next_hub.hub_type.value == "restricted"
                        ):

                    # Add midpoint for in-transit state
                    mid_x = (current_hub.x + next_hub.x) / 2.0
                    mid_y = (current_hub.y + next_hub.y) / 2.0
                    path_points.append(tr(mid_x, mid_y))

                elif hub is not None:
                    path_points.append(tr(hub.x, hub.y))
                    current_hub = hub

            # Draw the trail
            if len(path_points) > 1:
                # Use different colors for different drones
                drone_color = self._get_drone_color(drone.drone_id)
                painter.setPen(
                        QPen(drone_color, max(1, int(2 * self.zoom_level)),
                             Qt.PenStyle.DashLine)
                    )

                for i in range(len(path_points) - 1):
                    painter.drawLine(path_points[i], path_points[i + 1])

    def _draw_drones(
        self, painter: QPainter, map_obj: Map, current_step: int,
        tr: Callable[[float, float], QPoint]
    ) -> None:
        """Draw drones at their current positions"""
        for drone in map_obj.drones:
            pos = self._get_drone_position_at_step(
                    drone, map_obj, current_step
                )
            if pos:
                screen_pos = tr(pos[0], pos[1])
                self._draw_drone_at(painter, drone, screen_pos)

    def _get_drone_position_at_step(
        self, drone: Drone, map_obj: Map, step: int
    ) -> tuple[float, float] | None:
        """Calculate drone position at a given step

        Returns:
            (x, y) position, or None if drone doesn't exist at this step
            For restricted zones: returns midpoint of connection on first turn
        """
        if step == 0:
            # All drones start at start_hub
            return (map_obj.start_hub.x, map_obj.start_hub.y)

        if step > len(drone.path):
            # Drone has completed its journey
            if drone.path:
                last_hub = None
                for hub in reversed(drone.path):
                    if hub is not None:
                        last_hub = hub
                        break
                if last_hub:
                    return (last_hub.x, last_hub.y)
            return None

        # Find position at this step
        current_hub = map_obj.start_hub

        for i in range(step):
            if i >= len(drone.path):
                break

            hub = drone.path[i]
            # Check if this is the first turn of a restricted zone entry
            # Path has None followed by the restricted hub
            next_hub = None

            if i + 1 < len(drone.path):
                next_hub = drone.path[i + 1]

            if (
                    hub is None and next_hub and
                    next_hub is not None and
                    next_hub.hub_type.value == "restricted" and
                    i == step - 1
                    ):

                # Drone is in transit - show midway on connection
                mid_x = (current_hub.x + next_hub.x) / 2.0
                mid_y = (current_hub.y + next_hub.y) / 2.0
                return (mid_x, mid_y)

            if hub is not None:
                current_hub = hub

        return (current_hub.x, current_hub.y)

    def _draw_drone_at(
        self, painter: QPainter, drone: Drone, pos: QPoint
    ) -> None:
        """Draw a single drone at a position"""
        size = int(min(30, 12 * self.zoom_level))
        half = size // 2

        # Get drone color
        color = self._get_drone_color(drone.drone_id)

        # Draw drone as a filled circle
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(QBrush(color))
        painter.drawEllipse(pos.x() - half, pos.y() - half, size, size)

        # Draw drone ID
        font_size = max(6, min(10, int(8 * self.zoom_level)))
        painter.setFont(QFont("Arial", font_size, QFont.Weight.Bold))
        painter.setPen(Qt.GlobalColor.white)

        text = f"D{drone.drone_id}"
        metrics = painter.fontMetrics()
        text_w = metrics.horizontalAdvance(text)
        text_h = metrics.height()

        painter.drawText(
            pos.x() - text_w // 2,
            pos.y() + text_h // 4,
            text
        )

    def _get_drone_color(self, drone_id: int) -> QColor:
        """Get a consistent color for a drone based on its ID"""
        # Use a color palette
        colors = [
            QColor(255, 100, 100),  # Red
            QColor(100, 100, 255),  # Blue
            QColor(100, 255, 100),  # Green
            QColor(255, 200, 100),  # Orange
            QColor(255, 100, 255),  # Magenta
            QColor(100, 255, 255),  # Cyan
            QColor(200, 100, 255),  # Purple
            QColor(255, 255, 100),  # Yellow
        ]
        return colors[(drone_id - 1) % len(colors)]

    def _draw_hub_at(self, painter: QPainter, hub: Hub, pos: QPoint) -> None:
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
            pts = [
                QPoint(x, y - half),
                QPoint(x - half, y + half),
                QPoint(x + half, y + half)
            ]
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
