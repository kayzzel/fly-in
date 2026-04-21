from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QToolBar, QWidget, QSizePolicy, QFileDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QTimer, pyqtSignal
from pathlib import Path

if TYPE_CHECKING:
    from .map_visu import MainWindow


class PlayerToolBar(QToolBar):
    """Toolbar for controlling playback and loading new maps."""

    # Signals for navigation
    request_next = pyqtSignal()
    request_prev = pyqtSignal()
    request_restart = pyqtSignal()
    request_tick = pyqtSignal()
    # New signal emitted when a new map file is selected
    request_map_load = pyqtSignal(str)

    def __init__(self, parent: MainWindow) -> None:
        super().__init__("Controls", parent)

        # 1. Create Actions
        self.load_action = QAction("📂", self)
        self.play_pause_action = QAction("⏵", self)
        self.restart_action = QAction("⟳", self)
        self.prev_action = QAction("⏮", self)
        self.next_action = QAction("⏭", self)

        # 2. Connect Signals
        self.load_action.triggered.connect(self.on_load_file)
        self.play_pause_action.triggered.connect(self.on_play_pause)
        self.restart_action.triggered.connect(self.request_restart)
        self.prev_action.triggered.connect(self.request_prev)
        self.next_action.triggered.connect(self.request_next)

        # 3. Layout Construction
        def make_spacer() -> QWidget:
            spacer = QWidget()
            spacer.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Preferred
            )
            return spacer

        # Add Load button to the far left
        self.addAction(self.load_action)
        self.addWidget(make_spacer())

        # Center the playback controls
        self.addAction(self.prev_action)
        self.addAction(self.play_pause_action)
        self.addAction(self.next_action)
        self.addAction(self.restart_action)

        self.addWidget(make_spacer())

        self.setStyleSheet("QToolButton { font-size: 20px; padding: 5px; }")

        # 4. Timer State
        self.playing = False
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.request_tick)

    def on_load_file(self) -> None:
        """Open a file dialog and emit the load signal if a file is chosen."""
        # Stop playback while choosing a file
        if self.playing:
            self.on_play_pause()

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Map File",
            str(Path.cwd()),
            "Map Files (*.txt);;All Files (*)"
        )

        if file_path:
            self.request_map_load.emit(file_path)

    def on_play_pause(self) -> None:
        """Toggle playback state."""
        self.playing = not self.playing
        parent = self.parent()

        # Safe check for MainWindow attributes to avoid mypy errors
        if self.playing:
            if (parent is not None and
                    hasattr(parent, "steps") and
                    hasattr(parent, "max_steps")):
                if getattr(parent, "steps") >= getattr(parent, "max_steps"):
                    self.request_restart.emit()

            self.play_pause_action.setText("⏸")
            self.timer.start()
        else:
            self.play_pause_action.setText("⏵")
            self.timer.stop()

    def stop(self) -> None:
        """Stop the timer and reset button text."""
        self.timer.stop()
        self.playing = False
        self.play_pause_action.setText("⏵")
