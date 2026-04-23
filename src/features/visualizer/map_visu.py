from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QScrollArea,
    QVBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt

from .steps_tool_bar import PlayerToolBar
from .draw_map import MapWidget
from .pannable_scroll_area import PannableScrollArea
from ..map.Map import Map
from ..map.Hub import Hub
from ..map.Drone import Drone
from ..parser.map_data import MapData
from ..algo.algo import algo


class MainWindow(QMainWindow):
    """
        Description:
    The primary application window that integrates the map visualization,
    simulation controls, and data display. It manages the simulation state
    (current steps), handles UI events from the toolbar, and facilitates
    the loading of new map configurations and re-running the pathfinding
    algorithm.

        Attributes:
    drone_map -> The current Map instance being visualized.
    steps -> The current step index of the simulation.
    max_steps -> The total number of steps in the current simulation.
    canvas_size -> A tuple defining the base dimensions of the map canvas.
    map_widget -> The custom widget responsible for drawing hubs and drones.
    player_bar -> The toolbar containing simulation playback controls.
    step_label -> UI label displaying the current progress through the
                  simulation.
    info_label -> UI label displaying detailed text about drone locations.
    """
    def __init__(self, drone_map: Map) -> None:
        super().__init__()
        self.drone_map: Map = drone_map
        algo(drone_map)
        self.steps = 1
        self.max_steps = drone_map.max_steps
        self.canvas_size = (1600, 1600)

        self.setMinimumSize(400, 300)
        self.setMaximumSize(self.canvas_size[0], self.canvas_size[1])
        self.resize(800, 600)

        self.map_widget = MapWidget(
            canvas_width=self.canvas_size[0],
            canvas_height=self.canvas_size[1]
        )
        self.map_widget.draw_map(self.drone_map, current_step=0)

        scroll: PannableScrollArea = PannableScrollArea(self)
        scroll.setWidget(self.map_widget)
        scroll.setWidgetResizable(False)
        scroll.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(scroll)

        self.step_label = QLabel(
                f"Step: {self.steps - 1} / {self.max_steps - 1}"
            )
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_label.setStyleSheet(
            "font-size: 24px; background: rgba(255,255,255,180); "
            "padding: 10px; border-radius: 5px;"
        )
        wrapper_layout.addWidget(self.step_label)

        self.info_label = QLabel(self._get_drone_info())
        self.info_label.setAlignment(
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
                )
        self.info_label.setStyleSheet(
            "font-size: 12px; background: transparent; padding: 5px;"
        )
        self.info_label.setWordWrap(True)

        info_scroll = QScrollArea()
        info_scroll.setWidget(self.info_label)
        info_scroll.setWidgetResizable(True)
        info_scroll.setMaximumHeight(150)
        info_scroll.setStyleSheet(
            "background: rgba(255,255,255,200); "
            "border-radius: 5px; border: 1px solid #ccc;"
        )

        wrapper_layout.addWidget(info_scroll)

        self.setCentralWidget(wrapper)

        self.player_bar = PlayerToolBar(self)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.player_bar)
        self.player_bar.request_next.connect(self.on_next)
        self.player_bar.request_prev.connect(self.on_prev)
        self.player_bar.request_restart.connect(self.on_restart)
        self.player_bar.request_tick.connect(self.on_tick)
        self.player_bar.request_map_load.connect(self.load_new_map)

    def _get_drone_info(self) -> str:
        """
            Description:
        Generates a detailed summary of the simulation's current state,
        listing which drones are at which hubs and identifying any drones
        currently in a transit state between hubs.

            Return value:
        A formatted string containing total drone count, hub occupancy,
        and transit status.
        """
        if self.steps == 0:
            return (
                f"Total Drones: {len(self.drone_map.drones)}\n"
                "All drones at START position"
            )

        info_lines = [f"Total Drones: {len(self.drone_map.drones)}"]

        locations: dict[str, list[int]] = {}
        in_transit: list[tuple[int, str, str]] = []

        for drone in self.drone_map.drones:
            transit_info = self._get_drone_transit_status(drone)
            if transit_info:
                in_transit.append((
                    drone.drone_id,
                    transit_info[0],
                    transit_info[1]
                ))
            else:
                pos = self._get_drone_current_hub(drone)
                if pos:
                    hub_name = pos.name
                    if hub_name not in locations:
                        locations[hub_name] = []
                    locations[hub_name].append(drone.drone_id)

        for hub_name, drone_ids in sorted(locations.items()):
            drone_list = ", ".join(f"D{did}" for did in sorted(drone_ids))
            info_lines.append(f"{hub_name}: {drone_list}")

        if in_transit:
            info_lines.append("")
            info_lines.append("In Transit:")
            for drone_id, from_hub, to_hub in sorted(in_transit):
                info_lines.append(f"  D{drone_id}: {from_hub} → {to_hub}")

        return "\n".join(info_lines)

    def _get_drone_transit_status(
                self,
                drone: Drone
           ) -> tuple[str, str] | None:
        """
            Description:
        Determines if a specific drone is currently moving through a 2-turn
        restricted zone sequence at the current simulation step.

            Parameters:
        drone -> The Drone instance to check for transit status.

            Return value:
        A tuple of (from_hub, to_hub) names if in transit, otherwise None.
        """
        if self.steps == 0 or self.steps > len(drone.path):
            return None

        current_hub = self.drone_map.start_hub

        for i in range(self.steps):
            if i >= len(drone.path):
                break

            hub = drone.path[i]

            if i == self.steps - 1:
                next_hub = None

                if i + 1 < len(drone.path):
                    next_hub = drone.path[i + 1]

                if (
                        hub is None and next_hub and
                        next_hub is not None and
                        next_hub.hub_type.value == "restricted"
                        ):

                    return (current_hub.name, next_hub.name)

            if hub is not None:
                current_hub = hub

        return None

    def _get_drone_current_hub(self, drone: Drone) -> Hub | None:
        """
            Description:
        Retrieves the Hub object where a drone is currently located,
        accounting for its initial position and movement history up
        to the current step.

            Parameters:
        drone -> The Drone instance whose location is being queried.

            Return value:
        The Hub object currently occupied by the drone, or None.
        """
        if self.steps == 0:
            return self.drone_map.start_hub

        if self.steps > len(drone.path):
            for hub in reversed(drone.path):
                if hub is not None:
                    return hub
            return None

        current_hub = self.drone_map.start_hub
        for i in range(self.steps):
            if i >= len(drone.path):
                break
            hub = drone.path[i]
            if hub is not None:
                current_hub = hub

        return current_hub

    def update_display(self) -> None:
        """
            Description:
        Synchronizes the UI components by updating the step label,
        the drone information text, and triggering a repaint of the
        MapWidget to reflect the current step.
        """
        self.step_label.setText(
                f"Step: {self.steps - 1} / {self.max_steps - 1}"
            )
        self.info_label.setText(self._get_drone_info())
        self.map_widget.set_step(self.steps)

    def on_tick(self) -> None:
        """
            Description:
        Automatically advances the simulation by one step. This is
        triggered by the playback timer and stops the timer once
        the maximum step count is reached.
        """
        if self.steps < self.max_steps:
            self.steps += 1
            self.update_display()
        else:
            self.player_bar.stop()

    def on_next(self) -> None:
        """
            Description:
        Manually advances the simulation to the next step and pauses
        automatic playback if it was running.
        """
        if self.steps < self.max_steps:
            self.player_bar.stop()
            self.steps += 1
            self.update_display()

    def on_prev(self) -> None:
        """
            Description:
        Manually reverses the simulation to the previous step and
        pauses automatic playback if it was running.
        """
        if self.steps > 1:
            self.player_bar.stop()
            self.steps -= 1
            self.update_display()

    def on_restart(self) -> None:
        """
            Description:
        Resets the simulation state back to step one and stops
        the playback timer.
        """
        self.steps = 1
        self.player_bar.stop()
        self.update_display()

    def load_new_map(self, file_path: str) -> None:
        """
            Description:
        Attempts to parse a new file, construct a new Map, run the
        pathfinding algorithm, and reset the visualization. Displays
        a critical error dialog if parsing or algorithm execution fails.

            Parameters:
        file_path -> The absolute system path to the map text file.
        """
        try:
            self.player_bar.stop()

            map_data: MapData = MapData()
            map_data.parsing(file_path)
            new_map: Map = Map(map_data.get_map_data())
            algo(new_map)

            self.steps = 1
            self.max_steps = new_map.max_steps

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
