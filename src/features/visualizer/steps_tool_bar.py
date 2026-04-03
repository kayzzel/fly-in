from PyQt6.QtWidgets import QToolBar, QWidget, QSizePolicy
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QTimer, pyqtSignal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .map_visu import MainWindow


class PlayerToolBar(QToolBar):
    # Signals emitted when the toolbar wants to change the step
    request_next = pyqtSignal()
    request_prev = pyqtSignal()
    request_restart = pyqtSignal()
    request_tick = pyqtSignal()

    def __init__(self, parent: "MainWindow") -> None:
        super().__init__("Controls", parent)

        self.play_pause_action = QAction("⏵", self)
        self.restart_action = QAction("⟳", self)
        self.prev_action = QAction("⏮", self)
        self.next_action = QAction("⏭", self)

        self.play_pause_action.triggered.connect(self.on_play_pause)
        self.restart_action.triggered.connect(self.request_restart)
        self.prev_action.triggered.connect(self.request_prev)
        self.next_action.triggered.connect(self.request_next)

        def make_spacer() -> QWidget:
            spacer = QWidget()
            spacer.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred
            )
            return spacer

        self.addWidget(make_spacer())
        self.addAction(self.prev_action)
        self.addAction(self.play_pause_action)
        self.addAction(self.next_action)
        self.addAction(self.restart_action)
        self.addWidget(make_spacer())

        self.setStyleSheet("QToolButton { font-size: 20px; }")

        self.playing = False

        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.request_tick)

    def on_play_pause(self) -> None:
        self.playing = not self.playing
        if self.playing:
            parent = self.parent()
            if (
                    parent is not None and hasattr(parent, "steps") and
                    hasattr(parent, "max_steps") and
                    parent.steps >= parent.max_steps
                    ):
                self.request_restart.emit()

            self.play_pause_action.setText("⏸")
            self.timer.start()
        else:
            self.play_pause_action.setText("⏵")
            self.timer.stop()

    # Called by MainWindow when max steps is reached
    def stop(self) -> None:
        self.timer.stop()
        self.playing = False
        self.play_pause_action.setText("⏵")
