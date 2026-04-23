from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QToolBar, QWidget, QSizePolicy, QFileDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QTimer, pyqtSignal
from pathlib import Path

if TYPE_CHECKING:
    from .map_visu import MainWindow


class PlayerToolBar(QToolBar):
    """
        Description:
    A specialized toolbar providing playback controls for the drone simulation.
    It manages the simulation timer, handles user interactions for navigation
    (play, pause, next, previous, restart), and facilitates loading new map
    files through a file dialog.

        Attributes:
    request_next -> Signal emitted to advance the simulation by one step.
    request_prev -> Signal emitted to move the simulation back by one step.
    request_restart -> Signal emitted to reset the simulation to the beginning.
    request_tick -> Signal emitted by the internal timer to automate playback.
    request_map_load -> Signal emitted with a file path str to load a new map.
    playing -> Boolean tracking the current playback state.
    timer -> QTimer instance controlling the speed of the simulation playback.
    """

    request_next = pyqtSignal()
    request_prev = pyqtSignal()
    request_restart = pyqtSignal()
    request_tick = pyqtSignal()
    request_map_load = pyqtSignal(str)

    def __init__(self, parent: MainWindow) -> None:
        super().__init__("Controls", parent)

        self.load_action = QAction("📂", self)
        self.play_pause_action = QAction("⏵", self)
        self.restart_action = QAction("⟳", self)
        self.prev_action = QAction("⏮", self)
        self.next_action = QAction("⏭", self)

        self.load_action.triggered.connect(self.on_load_file)
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

        self.addAction(self.load_action)
        self.addWidget(make_spacer())

        self.addAction(self.prev_action)
        self.addAction(self.play_pause_action)
        self.addAction(self.next_action)
        self.addAction(self.restart_action)

        self.addWidget(make_spacer())

        self.setStyleSheet("QToolButton { font-size: 20px; padding: 5px; }")

        self.playing = False
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.request_tick)

    def on_load_file(self) -> None:
        """
            Description:
        Suspends playback and opens a native system file dialog to allow the
        user to select a map text file. If a file is selected, it emits the
        request_map_load signal.
        """
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
        """
            Description:
        Toggles the playback state between playing and paused. It updates
        the action icon, starts or stops the timer, and triggers a restart
        if the play button is pressed while at the end of a simulation.
        """
        self.playing = not self.playing
        parent = self.parent()

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
        """
            Description:
        Forces the playback to stop, halting the timer and resetting the
        internal state and UI button to the "paused" representation.
        """
        self.timer.stop()
        self.playing = False
        self.play_pause_action.setText("⏵")
