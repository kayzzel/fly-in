from PyQt6.QtWidgets import (
    QMainWindow, QLabel,
    QVBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt

from .steps_tool_bar import PlayerToolBar
from .draw_map import MapWidget
from .pannable_scroll_area import PannableScrollArea
from ..map.Map import Map
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
        self.map_widget.draw_map(self.drone_map)

        scroll: PannableScrollArea = PannableScrollArea(self)
        scroll.setWidget(self.map_widget)
        scroll.setWidgetResizable(False)  # False = map keeps its fixed size
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
                "font-size: 24px; background: rgba(255,255,255,180);"
                )
        wrapper_layout.addWidget(self.step_label)

        self.setCentralWidget(wrapper)

        # --- Toolbar ---
        self.player_bar = PlayerToolBar(self)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.player_bar)
        self.player_bar.request_next.connect(self.on_next)
        self.player_bar.request_prev.connect(self.on_prev)
        self.player_bar.request_restart.connect(self.on_restart)
        self.player_bar.request_tick.connect(self.on_tick)
        self.player_bar.request_map_load.connect(self.load_new_map)

    # ... rest of your slots unchanged
    def update_label(self) -> None:
        self.step_label.setText(f"Step: {self.steps} / {self.max_steps}")

    def on_tick(self) -> None:
        if self.steps < self.max_steps:
            self.steps += 1
            self.update_label()
        else:
            self.player_bar.stop()

    def on_next(self) -> None:
        if self.steps < self.max_steps:
            self.player_bar.stop()
            self.steps += 1
            self.update_label()

    def on_prev(self) -> None:
        if self.steps > 0:
            self.player_bar.stop()
            self.steps -= 1
            self.update_label()

    def on_restart(self) -> None:
        self.steps = 0
        self.player_bar.stop()
        self.update_label()

    def load_new_map(self, file_path: str) -> None:
        """Logic to parse the new file and update the MapWidget."""
        try:
            self.player_bar.stop()

            # 1. Parse your new map (assuming you have a parser)
            map_data: MapData = MapData()
            map_data.parsing(file_path)
            new_map: Map = Map(map_data.get_map_data())
            algo(new_map)

            # 2. Reset visualizer states
            self.steps = 0
            self.max_steps = new_map.max_steps

            # 3. Tell the widget to draw the new map
            self.drone_map = new_map
            self.map_widget.draw_map(new_map)

            self.player_bar.request_restart.emit()
        except Exception as e:
            error_dialog = QMessageBox(self)
            error_dialog.setIcon(QMessageBox.Icon.Critical)
            error_dialog.setWindowTitle("Map Loading Error")
            error_dialog.setText("Could not load the selected map file.")
            error_dialog.setInformativeText(str(e))
            error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_dialog.exec()
