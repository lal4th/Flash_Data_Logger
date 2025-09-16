from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore

from app.core.streaming_controller import StreamingController


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, controller: Optional[StreamingController] = None, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Flash Data Logger")
        self.resize(1200, 800)

        self.controller = controller or StreamingController()

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
        self.button_zero_offset = QtWidgets.QPushButton("Zero Offset", controls)
        self.button_stop.setEnabled(False)

        self.button_save_csv = QtWidgets.QPushButton("Save CSV to...", controls)
        
        # v0.7 Multi-channel mode toggle
        self.checkbox_multi_channel = QtWidgets.QCheckBox("Multi-Channel Mode", controls)
        self.checkbox_multi_channel.setToolTip("Enable simultaneous Channel A and B acquisition")
        
        # Cache directory setting
        self.lineedit_cache_dir = QtWidgets.QLineEdit(str(Path.cwd() / "cache"))
        self.button_browse_cache = QtWidgets.QPushButton("Browse…", controls)
        
        cache_row = QtWidgets.QHBoxLayout()
        cache_row.addWidget(self.lineedit_cache_dir, 1)
        cache_row.addWidget(self.button_browse_cache, 0)
        
        # Plot controls
        self.spinbox_y_max = QtWidgets.QDoubleSpinBox(controls)
        self.spinbox_y_max.setRange(0.1, 100.0)
        self.spinbox_y_max.setValue(10.0)  # Match default ±10V range (corrected)
        self.spinbox_y_max.setSuffix(" V")
        self.spinbox_y_max.setDecimals(1)
        
        self.spinbox_y_min = QtWidgets.QDoubleSpinBox(controls)
        self.spinbox_y_min.setRange(-100.0, -0.1)
        self.spinbox_y_min.setValue(-10.0)  # Match default ±10V range (corrected)
        self.spinbox_y_min.setSuffix(" V")
        self.spinbox_y_min.setDecimals(1)
        
        self.spinbox_timeline = QtWidgets.QDoubleSpinBox(controls)
        self.spinbox_timeline.setRange(1.0, 3600.0)
        self.spinbox_timeline.setValue(60.0)
        self.spinbox_timeline.setSuffix(" s")
        self.spinbox_timeline.setDecimals(1)

        # Device controls
        self.combo_channel = QtWidgets.QComboBox(controls)
        self.combo_channel.addItem("A", userData=0)
        self.combo_channel.addItem("B", userData=1)

        self.combo_coupling = QtWidgets.QComboBox(controls)
        self.combo_coupling.addItem("DC", userData=1)
        self.combo_coupling.addItem("AC", userData=0)

        # Common ps4000 ranges; map text to enum index - CORRECTED MAPPINGS
        self.combo_range = QtWidgets.QComboBox(controls)
        ranges = [
            ("±10 mV", 0),
            ("±20 mV", 1),
            ("±50 mV", 2),
            ("±100 mV", 3),
            ("±200 mV", 4),
            ("±500 mV", 5),
            ("±1 V", 6),
            ("±2 V", 7),    # CORRECTED: This was labeled ±5V but is actually ±2V
            ("±5 V", 8),    # CORRECTED: This was labeled ±10V but is actually ±5V
            ("±10 V", 9),   # CORRECTED: This was labeled ±20V but is actually ±10V
        ]
        for label, enum_val in ranges:
            self.combo_range.addItem(label, userData=enum_val)
        self.combo_range.setCurrentIndex(9)  # ±10 V (default range) - now at index 9

        self.combo_resolution = QtWidgets.QComboBox(controls)
        for bits in (8, 12, 14, 15, 16):
            self.combo_resolution.addItem(f"{bits} bit", userData=bits)
        self.combo_resolution.setCurrentIndex(4)  # 16-bit

        self.combo_samplerate = QtWidgets.QComboBox(controls)
        for hz in (10, 50, 100, 200, 500, 1000, 2000, 5000):  # Added back high rates with streaming architecture
            self.combo_samplerate.addItem(f"{hz} Hz", userData=hz)
        self.combo_samplerate.setCurrentIndex(2)  # 100 Hz default

        self.label_status = QtWidgets.QLabel("Idle", controls)

        # Button layout
        button_row = QtWidgets.QHBoxLayout()
        button_row.addWidget(self.button_start)
        button_row.addWidget(self.button_stop)
        button_row.addWidget(self.button_reset)
        
        # Zero offset button row
        zero_offset_row = QtWidgets.QHBoxLayout()
        zero_offset_row.addWidget(self.button_zero_offset)
        
        controls_layout.addRow(button_row)
        controls_layout.addRow(zero_offset_row)
        controls_layout.addRow(self.checkbox_multi_channel)
        controls_layout.addRow("Channel:", self.combo_channel)
        controls_layout.addRow("Coupling:", self.combo_coupling)
        controls_layout.addRow("Range:", self.combo_range)
        controls_layout.addRow("Resolution:", self.combo_resolution)
        controls_layout.addRow("Sample rate:", self.combo_samplerate)
        controls_layout.addRow("Y-axis Max:", self.spinbox_y_max)
        controls_layout.addRow("Y-axis Min:", self.spinbox_y_min)
        controls_layout.addRow("Timeline:", self.spinbox_timeline)
        controls_layout.addRow("CSV Cache:", cache_row)
        controls_layout.addRow(self.button_save_csv)
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
        
        # Initialize plot with correct axis ranges
        self.plot_widget.setXRange(0, 60, padding=0)  # Default 60 seconds
        self.plot_widget.setYRange(-10, 10, padding=0)  # Default ±10V
        
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
        self.button_zero_offset.clicked.connect(self._on_zero_offset_clicked)
        self.button_browse_cache.clicked.connect(self._on_browse_cache_clicked)
        self.button_save_csv.clicked.connect(self._on_save_csv_clicked)
        self.spinbox_y_max.valueChanged.connect(self._on_y_range_changed)
        self.spinbox_y_min.valueChanged.connect(self._on_y_range_changed)
        self.spinbox_timeline.valueChanged.connect(self._on_timeline_changed)
        self.combo_samplerate.currentIndexChanged.connect(self._on_samplerate_changed)
        self.checkbox_multi_channel.toggled.connect(self._on_multi_channel_toggled)

        self.controller.signal_status.connect(self._on_status_changed)
        self.controller.signal_plot.connect(self._on_plot_data)
        self.controller.signal_clear_plot.connect(self._on_clear_plot)
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
        self.controller.set_cache_directory(Path(self.lineedit_cache_dir.text()))
        self.controller.set_y_range(self.spinbox_y_min.value(), self.spinbox_y_max.value())
        self.controller.set_timeline(self.spinbox_timeline.value())
        # Ensure controller stops when window closes to avoid dangling threads
        self._app_closing = False
        def _on_about_to_quit() -> None:
            if not self._app_closing:
                self._app_closing = True
                try:
                    self.controller.cleanup()
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
        # Clear the plot and reset axes
        self.plot_curve.setData([], [])
        self.plot_widget.setXRange(0, self.spinbox_timeline.value(), padding=0)  # Reset to user-specified timeline
        self.plot_widget.setYRange(self.spinbox_y_min.value(), self.spinbox_y_max.value(), padding=0)  # Reset to user-specified range
        # Reset the controller's data source if there's a method for it
        if hasattr(self.controller, 'reset_data'):
            self.controller.reset_data()

    def _on_zero_offset_clicked(self) -> None:
        """Handle zero offset button click."""
        # Disable the button temporarily to prevent multiple clicks
        self.button_zero_offset.setEnabled(False)
        self.button_zero_offset.setText("Zeroing...")
        
        # Call the controller's zero offset function
        self.controller.zero_offset()
        
        # Re-enable the button after a short delay
        QtCore.QTimer.singleShot(2000, self._re_enable_zero_offset_button)
    
    def _re_enable_zero_offset_button(self) -> None:
        """Re-enable the zero offset button after zeroing is complete."""
        self.button_zero_offset.setEnabled(True)
        self.button_zero_offset.setText("Zero Offset")

    def _on_y_range_changed(self) -> None:
        self.controller.set_y_range(self.spinbox_y_min.value(), self.spinbox_y_max.value())

    def _on_timeline_changed(self) -> None:
        self.controller.set_timeline(self.spinbox_timeline.value())

    def _on_browse_cache_clicked(self) -> None:
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Cache Directory",
            self.lineedit_cache_dir.text(),
        )
        if directory:
            self.lineedit_cache_dir.setText(directory)
            self.controller.set_cache_directory(Path(directory))

    def _on_save_csv_clicked(self) -> None:
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save CSV File",
            "Flash_Data_Logger_CSV.csv",
            "CSV Files (*.csv);;All Files (*.*)",
        )
        if filename:
            success = self.controller.save_cache_csv(Path(filename))
            if not success:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Save Failed",
                    "Failed to save CSV file. Make sure data acquisition is running."
                )


    def _on_samplerate_changed(self, _index: int) -> None:
        self.controller.set_sample_rate(int(self.combo_samplerate.currentData()))

    def _on_multi_channel_toggled(self, enabled: bool) -> None:
        """Handle multi-channel mode toggle."""
        self.controller.set_multi_channel_mode(enabled)
        if enabled:
            # Configure both channels with current settings
            self.controller.set_channel_a_config(
                enabled=True,
                coupling=int(self.combo_coupling.currentData()),
                voltage_range=int(self.combo_range.currentData()),
                offset=0.0
            )
            self.controller.set_channel_b_config(
                enabled=True,
                coupling=int(self.combo_coupling.currentData()),
                voltage_range=int(self.combo_range.currentData()),
                offset=0.0
            )

    # ----- Signals from controller -----
    @QtCore.pyqtSlot(str)
    def _on_status_changed(self, message: str) -> None:
        self.label_status.setText(message)

    @QtCore.pyqtSlot()
    def _on_clear_plot(self) -> None:
        """Clear the plot data for a fresh session."""
        self.plot_curve.setData([], [])
        # Reset plot to show from 0 with current timeline
        self.plot_widget.setXRange(0, self.spinbox_timeline.value(), padding=0)
        self.plot_widget.setYRange(self.spinbox_y_min.value(), self.spinbox_y_max.value(), padding=0)

    @QtCore.pyqtSlot(object)
    def _on_plot_data(self, payload: object) -> None:
        # Handle both single-channel and multi-channel data
        if isinstance(payload, tuple) and len(payload) == 3:
            # Multi-channel data: (timestamps, channel_a_data, channel_b_data)
            time_axis, channel_a_data, channel_b_data = payload
            # For now, just plot Channel A data (we'll add separate plots later)
            data = channel_a_data
        elif isinstance(payload, tuple) and len(payload) == 2:
            # Single-channel data: (data, time_axis)
            data, time_axis = payload
        else:
            # Fallback for unexpected format
            return
        
        if data.size == 0:
            return
        
        # Update the plot data
        self.plot_curve.setData(time_axis, data)
        
        # Implement fixed timeline with scrolling when data exceeds timeline
        if len(time_axis) > 0:
            max_time = time_axis[-1]
            timeline = self.spinbox_timeline.value()
            
            if max_time <= timeline:
                # Data is within timeline, show from 0 to timeline
                self.plot_widget.setXRange(0, timeline, padding=0)
            else:
                # Data exceeds timeline, scroll to show last timeline seconds
                min_time = max_time - timeline
                self.plot_widget.setXRange(min_time, max_time, padding=0)
            
            # Keep Y axis fixed at user-specified range
            self.plot_widget.setYRange(self.spinbox_y_min.value(), self.spinbox_y_max.value(), padding=0)



