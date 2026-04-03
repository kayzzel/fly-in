import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel,
    QVBoxLayout, QWidget
)
from PyQt6.QtCore import Qt

from .steps_tool_bar import PlayerToolBar
from .draw_map import MapWidget
from .pannable_scroll_area import PannableScrollArea


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.steps = 0
        self.max_steps = 10
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

        scroll = PannableScrollArea()
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


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
