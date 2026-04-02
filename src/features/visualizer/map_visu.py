import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

from . steps_tool_bar import PlayerToolBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.steps = 0
        self.max_steps = 10

        # Central widget showing the step counter
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.step_label = QLabel(f"Step: {self.steps} / {self.max_steps}")
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.step_label)

        # Toolbar
        self.player_bar = PlayerToolBar(self)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.player_bar)

        # Connect toolbar signals to MainWindow slots
        self.player_bar.request_next.connect(self.on_next)
        self.player_bar.request_prev.connect(self.on_prev)
        self.player_bar.request_restart.connect(self.on_restart)
        self.player_bar.request_tick.connect(self.on_tick)

    def update_label(self):
        self.step_label.setText(f"Step: {self.steps} / {self.max_steps}")

    def on_tick(self):
        if self.steps < self.max_steps:
            self.steps += 1
            self.update_label()
        else:
            self.player_bar.stop()

    def on_next(self):
        if self.steps < self.max_steps:
            self.player_bar.stop()
            self.steps += 1
            self.update_label()

    def on_prev(self):
        if self.steps > 0:
            self.player_bar.stop()
            self.steps -= 1
            self.update_label()

    def on_restart(self):
        self.steps = 0
        self.player_bar.stop()
        self.update_label()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
