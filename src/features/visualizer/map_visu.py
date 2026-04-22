from PyQt6.QtWidgets import (
    QMainWindow, QLabel,
    QVBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt

from .steps_tool_bar import PlayerToolBar
from .draw_map import MapWidget
from .pannable_scroll_area import PannableScrollArea
from ..map.Map import Map
from ..map.Drone import Drone
from ..map.Hub import Hub
from ..parser.map_data import MapData
from ..algo.algo import algo


class MainWindow(QMainWindow):
    def __init__(self, drone_map: Map) -> None:
        super().__init__()
        self.drone_map: Map = drone_map
        algo(drone_map)
        self.steps = 0
        self.max_steps = drone_map.max_steps
        self.canvas_size = (1600, 1600)

        # --- set window sizes ---
        self.setMinimumSize(400, 300)
        self.setMaximumSize(self.canvas_size[0], self.canvas_size[1])
        self.resize(800, 600)

        # --- Scroll area wrapping the map ---
        self.map_widget = MapWidget(
            canvas_width=self.canvas_size[0],
            canvas_height=self.canvas_size[1]
        )
        # Initialize map at step 0
        self.map_widget.draw_map(self.drone_map, current_step=0)

        scroll: PannableScrollArea = PannableScrollArea(self)
        scroll.setWidget(self.map_widget)
        scroll.setWidgetResizable(False)
        scroll.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        # Overlay the step label on top via a wrapper
        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(scroll)

        self.step_label = QLabel(f"Step: {self.steps} / {self.max_steps}")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_label.setStyleSheet(
            "font-size: 24px; background: rgba(255,255,255,180); "
            "padding: 10px; border-radius: 5px;"
        )
        wrapper_layout.addWidget(self.step_label)

        # Add drone info panel
        self.info_label = QLabel(self._get_drone_info())
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.info_label.setStyleSheet(
            "font-size: 12px; background: rgba(255,255,255,200); "
            "padding: 10px; border-radius: 5px;"
        )
        self.info_label.setMaximumHeight(150)
        wrapper_layout.addWidget(self.info_label)

        self.setCentralWidget(wrapper)

        # --- Toolbar ---
        self.player_bar = PlayerToolBar(self)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.player_bar)
        self.player_bar.request_next.connect(self.on_next)
        self.player_bar.request_prev.connect(self.on_prev)
        self.player_bar.request_restart.connect(self.on_restart)
        self.player_bar.request_tick.connect(self.on_tick)
        self.player_bar.request_map_load.connect(self.load_new_map)

    def _get_drone_info(self) -> str:
        """Generate info text about drone positions at current step"""
        if self.steps == 0:
            return (
                f"Total Drones: {len(self.drone_map.drones)}\n"
                "All drones at START position"
            )

        info_lines = [f"Total Drones: {len(self.drone_map.drones)}"]

        # Count drones at each location
        locations: dict[str, list[int]] = {}
        for drone in self.drone_map.drones:
            pos = self._get_drone_current_hub(drone)
            if pos:
                hub_name = pos.name
                if hub_name not in locations:
                    locations[hub_name] = []
                locations[hub_name].append(drone.drone_id)

        # Display locations
        for hub_name, drone_ids in sorted(locations.items()):
            drone_list = ", ".join(f"D{did}" for did in sorted(drone_ids))
            info_lines.append(f"{hub_name}: {drone_list}")

        return "\n".join(info_lines)

    def _get_drone_current_hub(self, drone: Drone) -> Hub | None:
        """Get the hub where a drone is at the current step"""
        if self.steps == 0:
            return self.drone_map.start_hub

        if self.steps > len(drone.path):
            # Drone completed - find last non-None hub
            for hub in reversed(drone.path):
                if hub is not None:
                    return hub
            return None

        # Find current position
        current_hub = self.drone_map.start_hub
        for i in range(self.steps):
            if i >= len(drone.path):
                break
            hub = drone.path[i]
            if hub is not None:
                current_hub = hub

        return current_hub

    def update_display(self) -> None:
        """Update both the label and the map visualization"""
        self.step_label.setText(f"Step: {self.steps} / {self.max_steps}")
        self.info_label.setText(self._get_drone_info())
        self.map_widget.set_step(self.steps)

    def on_tick(self) -> None:
        if self.steps < self.max_steps:
            self.steps += 1
            self.update_display()
        else:
            self.player_bar.stop()

    def on_next(self) -> None:
        if self.steps < self.max_steps:
            self.player_bar.stop()
            self.steps += 1
            self.update_display()

    def on_prev(self) -> None:
        if self.steps > 0:
            self.player_bar.stop()
            self.steps -= 1
            self.update_display()

    def on_restart(self) -> None:
        self.steps = 0
        self.player_bar.stop()
        self.update_display()

    def load_new_map(self, file_path: str) -> None:
        """Logic to parse the new file and update the MapWidget."""
        try:
            self.player_bar.stop()

            # 1. Parse your new map
            map_data: MapData = MapData()
            map_data.parsing(file_path)
            new_map: Map = Map(map_data.get_map_data())
            algo(new_map)

            # 2. Reset visualizer states
            self.steps = 0
            self.max_steps = new_map.max_steps

            # 3. Tell the widget to draw the new map
            self.drone_map = new_map
            self.map_widget.draw_map(new_map, current_step=0)

            self.update_display()
            self.player_bar.request_restart.emit()
        except Exception as e:
            error_dialog = QMessageBox(self)
            error_dialog.setIcon(QMessageBox.Icon.Critical)
            error_dialog.setWindowTitle("Map Loading Error")
            error_dialog.setText("Could not load the selected map file.")
            error_dialog.setInformativeText(str(e))
            error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_dialog.exec()
