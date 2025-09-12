from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore

from app.core.controller import AppController


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, controller: Optional[AppController] = None, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Flash Data Logger")
        self.resize(1200, 800)

        self.controller = controller or AppController()

        central = QtWidgets.QWidget(self)
        root_layout = QtWidgets.QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 8)
        self.setCentralWidget(central)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, central)
        root_layout.addWidget(splitter, 1)

        # Controls panel
        controls = QtWidgets.QGroupBox("Controls", splitter)
        controls_layout = QtWidgets.QFormLayout(controls)
        controls.setMinimumWidth(320)
        controls.setMaximumWidth(420)
        splitter.addWidget(controls)

        self.button_start = QtWidgets.QPushButton("Start", controls)
        self.button_stop = QtWidgets.QPushButton("Stop", controls)
        self.button_reset = QtWidgets.QPushButton("Reset Plot", controls)
        self.button_stop.setEnabled(False)

        self.checkbox_record = QtWidgets.QCheckBox("Record to CSV", controls)
        self.lineedit_filename = QtWidgets.QLineEdit(str(Path.cwd() / "data.csv"))
        self.button_browse = QtWidgets.QPushButton("Browse…", controls)

        filename_row = QtWidgets.QHBoxLayout()
        filename_row.addWidget(self.lineedit_filename, 1)
        filename_row.addWidget(self.button_browse, 0)

        # Device controls
        self.combo_channel = QtWidgets.QComboBox(controls)
        self.combo_channel.addItem("A", userData=0)
        self.combo_channel.addItem("B", userData=1)

        self.combo_coupling = QtWidgets.QComboBox(controls)
        self.combo_coupling.addItem("DC", userData=1)
        self.combo_coupling.addItem("AC", userData=0)

        # Common ps4000 ranges; map text to enum index
        self.combo_range = QtWidgets.QComboBox(controls)
        ranges = [
            ("±10 mV", 0),
            ("±20 mV", 1),
            ("±50 mV", 2),
            ("±100 mV", 3),
            ("±200 mV", 4),
            ("±500 mV", 5),
            ("±1 V", 6),
            ("±5 V", 7),
            ("±10 V", 8),
            ("±20 V", 9),
        ]
        for label, enum_val in ranges:
            self.combo_range.addItem(label, userData=enum_val)
        self.combo_range.setCurrentIndex(7)  # ±5 V

        self.combo_resolution = QtWidgets.QComboBox(controls)
        for bits in (8, 12, 14, 15, 16):
            self.combo_resolution.addItem(f"{bits} bit", userData=bits)
        self.combo_resolution.setCurrentIndex(4)  # 16-bit

        self.combo_samplerate = QtWidgets.QComboBox(controls)
        for hz in (10, 50, 100, 200, 500, 1000, 2000, 5000):
            self.combo_samplerate.addItem(f"{hz} Hz", userData=hz)
        self.combo_samplerate.setCurrentIndex(2)  # 100 Hz default

        self.label_status = QtWidgets.QLabel("Idle", controls)

        # Button layout
        button_row = QtWidgets.QHBoxLayout()
        button_row.addWidget(self.button_start)
        button_row.addWidget(self.button_stop)
        button_row.addWidget(self.button_reset)
        
        controls_layout.addRow(button_row)
        controls_layout.addRow("Channel:", self.combo_channel)
        controls_layout.addRow("Coupling:", self.combo_coupling)
        controls_layout.addRow("Range:", self.combo_range)
        controls_layout.addRow("Resolution:", self.combo_resolution)
        controls_layout.addRow("Sample rate:", self.combo_samplerate)
        controls_layout.addRow(self.checkbox_record)
        controls_layout.addRow("Filename:", filename_row)
        controls_layout.addRow("Status:", self.label_status)

        # Plot area
        plot_container = QtWidgets.QGroupBox("Signal", splitter)
        plot_layout = QtWidgets.QVBoxLayout(plot_container)
        splitter.addWidget(plot_container)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self.plot_widget = pg.PlotWidget(plot_container)
        self.plot_widget.setBackground("w")
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_curve = self.plot_widget.plot(pen=pg.mkPen(color=(50, 100, 200), width=2))
        plot_layout.addWidget(self.plot_widget, 1)

        # Wire up controller
        self._connect_signals()
        self._apply_initial_state()
        # Probe device once UI is ready
        QtCore.QTimer.singleShot(0, self.controller.probe_device)

    # ----- UI wiring -----
    def _connect_signals(self) -> None:
        self.button_start.clicked.connect(self._on_start_clicked)
        self.button_stop.clicked.connect(self._on_stop_clicked)
        self.button_reset.clicked.connect(self._on_reset_clicked)
        self.button_browse.clicked.connect(self._on_browse_clicked)
        self.checkbox_record.toggled.connect(self._on_record_toggled)
        self.combo_samplerate.currentIndexChanged.connect(self._on_samplerate_changed)

        self.controller.signal_status.connect(self._on_status_changed)
        self.controller.signal_plot.connect(self._on_plot_data)
        self.combo_channel.currentIndexChanged.connect(lambda _i: self.controller.set_channel(int(self.combo_channel.currentData())))
        self.combo_coupling.currentIndexChanged.connect(lambda _i: self.controller.set_coupling(int(self.combo_coupling.currentData())))
        self.combo_range.currentIndexChanged.connect(lambda _i: self.controller.set_voltage_range(int(self.combo_range.currentData())))
        self.combo_resolution.currentIndexChanged.connect(lambda _i: self.controller.set_resolution(int(self.combo_resolution.currentData())))

    def _apply_initial_state(self) -> None:
        self.controller.set_sample_rate(int(self.combo_samplerate.currentData()))
        self.controller.set_channel(int(self.combo_channel.currentData()))
        self.controller.set_coupling(int(self.combo_coupling.currentData()))
        self.controller.set_voltage_range(int(self.combo_range.currentData()))
        self.controller.set_resolution(int(self.combo_resolution.currentData()))
        self.controller.set_filename(Path(self.lineedit_filename.text()))
        self.controller.set_recording(self.checkbox_record.isChecked())
        # Ensure controller stops when window closes to avoid dangling threads
        self._app_closing = False
        def _on_about_to_quit() -> None:
            if not self._app_closing:
                self._app_closing = True
                try:
                    self.controller.stop()
                except Exception:
                    pass
        QtWidgets.QApplication.instance().aboutToQuit.connect(_on_about_to_quit)  # type: ignore[arg-type]

    # ----- Controller callbacks -----
    def _on_start_clicked(self) -> None:
        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(True)
        self.controller.start()

    def _on_stop_clicked(self) -> None:
        self.controller.stop()
        self.button_start.setEnabled(True)
        self.button_stop.setEnabled(False)

    def _on_reset_clicked(self) -> None:
        # Clear the plot
        self.plot_curve.setData([], [])
        # Reset the controller's data source if there's a method for it
        if hasattr(self.controller, 'reset_data'):
            self.controller.reset_data()

    def _on_browse_clicked(self) -> None:
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Select CSV file",
            self.lineedit_filename.text(),
            "CSV Files (*.csv);;All Files (*.*)",
        )
        if filename:
            self.lineedit_filename.setText(filename)
            self.controller.set_filename(Path(filename))

    def _on_record_toggled(self, checked: bool) -> None:
        self.controller.set_recording(checked)

    def _on_samplerate_changed(self, _index: int) -> None:
        self.controller.set_sample_rate(int(self.combo_samplerate.currentData()))

    # ----- Signals from controller -----
    @QtCore.pyqtSlot(str)
    def _on_status_changed(self, message: str) -> None:
        self.label_status.setText(message)

    @QtCore.pyqtSlot(object)
    def _on_plot_data(self, payload: object) -> None:
        data: np.ndarray
        time_axis: np.ndarray
        data, time_axis = payload  # type: ignore[assignment]
        if data.size == 0:
            return
        self.plot_curve.setData(time_axis, data)


