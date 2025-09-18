from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, List, Tuple

import numpy as np
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore, QtGui

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
        self.button_stop.setEnabled(False)

        self.button_save_csv = QtWidgets.QPushButton("Save CSV to...", controls)
        
        # Always-on multi-channel; remove toggle
        
        # Cache directory setting
        self.lineedit_cache_dir = QtWidgets.QLineEdit(str(Path.cwd() / "cache"))
        self.button_browse_cache = QtWidgets.QPushButton("Browse…", controls)
        
        cache_row = QtWidgets.QHBoxLayout()
        cache_row.addWidget(self.lineedit_cache_dir, 1)
        cache_row.addWidget(self.button_browse_cache, 0)
        
        # Y-axis controls removed - each plot has its own Y-axis settings
        
        self.spinbox_timeline = QtWidgets.QDoubleSpinBox(controls)
        self.spinbox_timeline.setRange(1.0, 3600.0)
        self.spinbox_timeline.setValue(60.0)
        self.spinbox_timeline.setSuffix(" s")
        self.spinbox_timeline.setDecimals(1)
        # Remove up/down arrows
        self.spinbox_timeline.setButtonSymbols(QtWidgets.QAbstractSpinBox.ButtonSymbols.NoButtons)

        # Minimal device/global controls
        self.combo_resolution = QtWidgets.QComboBox(controls)
        for bits in (8, 12, 14, 15, 16):
            self.combo_resolution.addItem(f"{bits} bit", userData=bits)
        self.combo_resolution.setCurrentIndex(4)  # 16-bit
        # Remove dropdown arrow
        self.combo_resolution.setStyleSheet("QComboBox::drop-down { border: none; }")

        self.combo_samplerate = QtWidgets.QComboBox(controls)
        for hz in (10, 50, 100, 200, 500, 1000, 2000, 5000):  # Added back high rates with streaming architecture
            self.combo_samplerate.addItem(f"{hz} Hz", userData=hz)
        self.combo_samplerate.setCurrentIndex(2)  # 100 Hz default
        # Remove dropdown arrow
        self.combo_samplerate.setStyleSheet("QComboBox::drop-down { border: none; }")

        self.label_status = QtWidgets.QLabel("Idle", controls)

        # Button layout
        button_row = QtWidgets.QHBoxLayout()
        button_row.addWidget(self.button_start)
        button_row.addWidget(self.button_stop)
        button_row.addWidget(self.button_reset)
        
        # Add Plot button in its own row (where Zero Offset was)
        self.button_add_plot = QtWidgets.QPushButton("Add Plot…", controls)
        add_plot_row = QtWidgets.QHBoxLayout()
        add_plot_row.addWidget(self.button_add_plot)
        
        controls_layout.addRow(button_row)
        controls_layout.addRow(add_plot_row)
        # Minimal controls: remove explicit multi-channel toggle row
        controls_layout.addRow("Resolution:", self.combo_resolution)
        controls_layout.addRow("Sample rate:", self.combo_samplerate)
        controls_layout.addRow("Timeline:", self.spinbox_timeline)
        controls_layout.addRow("CSV Cache:", cache_row)
        controls_layout.addRow(self.button_save_csv)
        controls_layout.addRow("Status:", self.label_status)

        # Plot area with splitter for Channel A and Channel B
        plot_container = QtWidgets.QGroupBox("Signal", splitter)
        plot_layout = QtWidgets.QVBoxLayout(plot_container)
        splitter.addWidget(plot_container)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        # 3x2 Plot Grid
        self.plot_grid_container = QtWidgets.QWidget(plot_container)
        self.plot_grid_layout = QtWidgets.QGridLayout(self.plot_grid_container)
        self.plot_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_grid_layout.setSpacing(6)
        plot_layout.addWidget(self.plot_grid_container, 1)

        # Track panels (row, col) -> PlotPanel
        self._plot_panels: List[Tuple[int, int, 'PlotPanel']] = []
        
        # Dynamic grid - no starter grid, grows as needed
        self.grid_state: List[List[Optional[str]]] = []
        self.grid_widgets: dict[Tuple[int, int], QtWidgets.QWidget] = {}
        self.max_cols = 2  # Start with 2 columns, expand to 3 when needed

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
        self.button_browse_cache.clicked.connect(self._on_browse_cache_clicked)
        self.button_save_csv.clicked.connect(self._on_save_csv_clicked)
        self.button_add_plot.clicked.connect(self._on_add_plot_clicked)
        self.spinbox_timeline.valueChanged.connect(self._on_timeline_changed)
        self.combo_samplerate.currentIndexChanged.connect(self._on_samplerate_changed)
        # Multi-channel is always on; no toggle wiring
        # No layout toggle; grid is fixed 3x2

        self.controller.signal_status.connect(self._on_status_changed)
        self.controller.signal_plot.connect(self._on_plot_data)
        self.controller.signal_clear_plot.connect(self._on_clear_plot)
        self.combo_resolution.currentIndexChanged.connect(lambda _i: self.controller.set_resolution(int(self.combo_resolution.currentData())))
        
        # Synchronized scrolling will be handled differently

    def _apply_initial_state(self) -> None:
        self.controller.set_sample_rate(int(self.combo_samplerate.currentData()))
        self.controller.set_resolution(int(self.combo_resolution.currentData()))
        self.controller.set_cache_directory(Path(self.lineedit_cache_dir.text()))
        self.controller.set_timeline(self.spinbox_timeline.value())
        # Always-on multi-channel with default DC, ±10V for both
        self.controller.set_multi_channel_mode(True)
        self.controller.set_channel_a_config(True, 1, 9, 0.0)
        self.controller.set_channel_b_config(True, 1, 9, 0.0)
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
        
        # Connect to controller signals for plot updates
        self.controller.signal_status.connect(self._on_status_update)
        
        # Start a timer to update plots with data from the streaming controller
        self._plot_update_timer = QtCore.QTimer()
        self._plot_update_timer.timeout.connect(self._update_plots)
        self._plot_update_timer.start(100)  # Update every 100ms (10 Hz)


    def _on_status_update(self, message: str) -> None:
        """Handle status updates from the controller."""
        # You can add status display logic here if needed
        pass

    def _update_plots(self) -> None:
        """Update all plots with current data from the streaming controller."""
        if not hasattr(self.controller, '_ram_buffer') or not self.controller._ram_buffer:
            return
        
        # Get the latest data from the streaming controller
        with self.controller._ram_buffer_lock:
            if not self.controller._ram_buffer:
                return
            # Get the last data point
            latest_data = self.controller._ram_buffer[-1]
        
        timestamp, channel_a_value, channel_b_value = latest_data[:3]
        
        # Update physical channel plots
        for row, col, plot_panel in self._plot_panels:
            if plot_panel.channel == 'A':
                plot_panel.update_data(timestamp, channel_a_value)
            elif plot_panel.channel == 'B':
                plot_panel.update_data(timestamp, channel_b_value)
            elif plot_panel.channel == 'MATH':
                # Get math channel value from the streaming controller
                math_channels = self.controller.get_math_channels()
                if plot_panel.config.title in math_channels:
                    # Get the latest math channel calculation from the stored results
                    if hasattr(self.controller, '_math_results') and plot_panel.config.title in self.controller._math_results:
                        math_value = self.controller._math_results[plot_panel.config.title]
                        # Skip NaN values - don't plot them
                        if not (math.isnan(math_value) or math.isinf(math_value)):
                            plot_panel.update_data(timestamp, math_value)

    # ----- Controller callbacks -----
    def _on_start_clicked(self) -> None:
        print(f"DEBUG: _on_start_clicked() called")
        print(f"DEBUG: controller._pico_source = {getattr(self.controller, '_pico_source', 'NOT_FOUND')}")
        print(f"DEBUG: controller._pico_6000_source = {getattr(self.controller, '_pico_6000_source', 'NOT_FOUND')}")
        
        # Check if PicoScope is connected before starting
        has_pico_source = hasattr(self.controller, '_pico_source') and self.controller._pico_source is not None
        has_pico_6000_source = hasattr(self.controller, '_pico_6000_source') and self.controller._pico_6000_source is not None
        
        print(f"DEBUG: has_pico_source = {has_pico_source}")
        print(f"DEBUG: has_pico_6000_source = {has_pico_6000_source}")
        
        if not has_pico_source and not has_pico_6000_source:
            print(f"DEBUG: No device detected, showing warning")
            QtWidgets.QMessageBox.warning(self, "Device Not Connected", 
                "No PicoScope device detected. Please connect a PicoScope and try again.")
            return
        
        # Check if any plots have been added
        if len(self._plot_panels) == 0:
            QtWidgets.QMessageBox.warning(self, "No Plots Added", 
                "No plots have been added to the view. Please add at least one plot before starting a logging session.")
            return
        
        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(True)
        self.button_add_plot.setEnabled(False)  # Disable Add Plot during logging
        # Disable controls during logging with consistent styling
        self.combo_resolution.setEnabled(False)
        self.combo_samplerate.setEnabled(False)
        self.spinbox_timeline.setEnabled(False)
        # Apply consistent disabled styling
        self._apply_disabled_styling()
        self.controller.start()

    def _on_stop_clicked(self) -> None:
        self.controller.stop()
        self.button_start.setEnabled(True)
        self.button_stop.setEnabled(False)
        # Keep controls disabled - only Reset will re-enable them

    def _on_reset_clicked(self) -> None:
        # Clear data from all plots but keep the plots themselves
        for _r, _c, panel in self._plot_panels:
            panel.clear()
        
        # Reset the controller's data source if there's a method for it
        if hasattr(self.controller, 'reset_data'):
            self.controller.reset_data()

        # Re-enable all controls
        self.button_add_plot.setEnabled(True)
        self.combo_resolution.setEnabled(True)
        self.combo_samplerate.setEnabled(True)
        self.spinbox_timeline.setEnabled(True)
        # Remove disabled styling
        self._remove_disabled_styling()

    # Zero offset functionality preserved but button hidden
    def _zero_offset(self) -> None:
        """Zero offset functionality - can be called programmatically if needed."""
        self.controller.zero_offset()
        
    # Y-axis range handling removed - each plot manages its own Y-axis

    def _on_timeline_changed(self) -> None:
        self.controller.set_timeline(self.spinbox_timeline.value())
    
    def _sync_all_plots_x_range(self, x_min: float, x_max: float, source_plot: 'PlotPanel') -> None:
        """Synchronize X range across all main grid plots except the source."""
        for _r, _c, panel in self._plot_panels:
            if panel != source_plot:  # Don't sync the plot that triggered the change
                # Set flag to prevent infinite loop
                panel._syncing = True
                panel.plot.setXRange(x_min, x_max, padding=0)
                panel._syncing = False
    
    
    def _apply_disabled_styling(self) -> None:
        """Apply consistent disabled styling to all controls."""
        print("Applying disabled styling to controls")
        # Use standard disabled styling - no custom CSS needed
        print("Disabled styling applied")
    
    def _remove_disabled_styling(self) -> None:
        """Remove custom styling to restore default appearance."""
        print("Removing disabled styling from controls")
        # Restore the original styling for combo boxes (dropdown arrows)
        self.combo_resolution.setStyleSheet("QComboBox::drop-down { border: none; }")
        self.combo_samplerate.setStyleSheet("QComboBox::drop-down { border: none; }")
        print("Disabled styling removed")

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

    # Multi-channel is always on; no toggle handler

    # ----- Signals from controller -----
    @QtCore.pyqtSlot(str)
    def _on_status_changed(self, message: str) -> None:
        self.label_status.setText(message)

    @QtCore.pyqtSlot()
    def _on_clear_plot(self) -> None:
        """Clear the plot data for a fresh session."""
        for _r, _c, panel in self._plot_panels:
            panel.clear()

    @QtCore.pyqtSlot(object)
    def _on_plot_data(self, payload: object) -> None:
        # Handle single-channel, dual-channel, and extended multi-channel data
        if isinstance(payload, tuple) and len(payload) == 9:
            # Extended multi-channel data: (data_a, data_b, data_c, data_d, data_e, data_f, data_g, data_h, time_axis)
            data_a, data_b, data_c, data_d, data_e, data_f, data_g, data_h, time_axis = payload
        elif isinstance(payload, tuple) and len(payload) == 3:
            # Dual-channel data: (data_a, data_b, time_axis)
            data_a, data_b, time_axis = payload
            data_c = data_d = data_e = data_f = data_g = data_h = np.array([], dtype=float)
        elif isinstance(payload, tuple) and len(payload) == 2:
            # Single-channel data: (data, time_axis)
            data_a, time_axis = payload
            data_b = data_c = data_d = data_e = data_f = data_g = data_h = np.array([], dtype=float)
        else:
            # Fallback for unexpected format
            return
        
        # Update panels - use efficient array-based updates
        for _r, _c, panel in self._plot_panels:
            if panel.channel == 'A' and data_a.size > 0:
                panel.update_data_array(time_axis, data_a)
            elif panel.channel == 'B' and isinstance(data_b, np.ndarray) and data_b.size > 0:
                panel.update_data_array(time_axis, data_b)
            elif panel.channel == 'C' and isinstance(data_c, np.ndarray) and data_c.size > 0:
                panel.update_data_array(time_axis, data_c)
            elif panel.channel == 'D' and isinstance(data_d, np.ndarray) and data_d.size > 0:
                panel.update_data_array(time_axis, data_d)
            elif panel.channel == 'E' and isinstance(data_e, np.ndarray) and data_e.size > 0:
                panel.update_data_array(time_axis, data_e)
            elif panel.channel == 'F' and isinstance(data_f, np.ndarray) and data_f.size > 0:
                panel.update_data_array(time_axis, data_f)
            elif panel.channel == 'G' and isinstance(data_g, np.ndarray) and data_g.size > 0:
                panel.update_data_array(time_axis, data_g)
            elif panel.channel == 'H' and isinstance(data_h, np.ndarray) and data_h.size > 0:
                panel.update_data_array(time_axis, data_h)
            elif panel.channel == 'MATH':
                # Math channels will be computed later
                pass

    # ----- Grid/Plot management -----
    def _ensure_grid_size(self, min_rows: int, min_cols: int) -> None:
        """Ensure grid is large enough for the requested dimensions."""
        # Expand rows if needed
        while len(self.grid_state) < min_rows:
            self.grid_state.append([None for _ in range(self.max_cols)])
        
        # Expand columns if needed
        if min_cols > self.max_cols:
            self.max_cols = min_cols
            for row in self.grid_state:
                while len(row) < self.max_cols:
                    row.append(None)

    def _add_plot_to_grid(self, cfg: 'PlotConfig') -> None:
        print(f"Adding plot to grid: {cfg.channel}")
        # Check if a plot for this channel already exists (only for physical channels A and B)
        if cfg.channel in ['A', 'B']:
            for r in range(len(self.grid_state)):
                for c in range(len(self.grid_state[r])):
                    if self.grid_state[r][c] == f"plot_{cfg.channel}":
                        print(f"Channel {cfg.channel} plot already exists at ({r}, {c})")
                        # Show warning message
                        QtWidgets.QMessageBox.warning(self, "Duplicate Channel", 
                            f"A Channel {cfg.channel} plot already exists. Only one plot per channel is allowed.")
                        return
        
        # For math channels, add them to the streaming controller
        if cfg.channel == 'MATH' and hasattr(cfg, 'formula') and cfg.formula:
            # Create math channel configuration
            from app.processing.math_engine import MathChannelConfig
            math_config = MathChannelConfig(
                name=cfg.title,
                formula=cfg.formula,
                enabled=True,
                y_min=cfg.y_min,
                y_max=cfg.y_max,
                y_label=cfg.y_label,
                color=cfg.color
            )
            
            # Add to streaming controller
            success = self.controller.add_math_channel(cfg.title, cfg.formula, math_config)
            if not success:
                QtWidgets.QMessageBox.warning(self, "Invalid Formula", 
                    f"Failed to add math channel '{cfg.title}': Invalid formula '{cfg.formula}'")
                return
        
        # For physical channels, enable them in the streaming controller
        elif cfg.channel in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            # Enable the channel in the controller
            coupling = 1 if cfg.coupling == 0 else 0  # Convert UI coupling to controller coupling
            voltage_range = cfg.voltage_range
            
            if cfg.channel == 'A':
                self.controller.set_channel_a_config(True, coupling, voltage_range)
            elif cfg.channel == 'B':
                self.controller.set_channel_b_config(True, coupling, voltage_range)
            elif cfg.channel == 'C':
                self.controller.set_channel_c_config(True, coupling, voltage_range)
            elif cfg.channel == 'D':
                self.controller.set_channel_d_config(True, coupling, voltage_range)
            elif cfg.channel == 'E':
                self.controller.set_channel_e_config(True, coupling, voltage_range)
            elif cfg.channel == 'F':
                self.controller.set_channel_f_config(True, coupling, voltage_range)
            elif cfg.channel == 'G':
                self.controller.set_channel_g_config(True, coupling, voltage_range)
            elif cfg.channel == 'H':
                self.controller.set_channel_h_config(True, coupling, voltage_range)
        
        # Determine grid size based on number of plots
        num_plots = len(self._plot_panels)
        print(f"Current number of plots: {num_plots}")
        if num_plots == 0:
            # First plot: 1x1
            rows, cols = 1, 1
        elif num_plots == 1:
            # Second plot: 2x1
            rows, cols = 2, 1
        elif num_plots <= 3:
            # 3rd-4th plots: 2x2
            rows, cols = 2, 2
        elif num_plots <= 5:
            # 5th-6th plots: 3x2
            rows, cols = 3, 2
        else:
            # 7th+ plots: 3x3
            rows, cols = 3, 3
        
        print(f"Grid sizing: {num_plots} plots -> {rows}x{cols}")
        
        # Ensure grid is large enough
        self._ensure_grid_size(rows, cols)
        print(f"Grid state after ensure: {self.grid_state}")
        
        # Find first available cell
        for r in range(rows):
            for c in range(cols):
                print(f"Checking cell ({r}, {c}): state = {self.grid_state[r][c] if r < len(self.grid_state) and c < len(self.grid_state[r]) else 'OUT_OF_BOUNDS'}")
                if r < len(self.grid_state) and c < len(self.grid_state[r]):
                    if self.grid_state[r][c] is None:
                        print(f"Found available cell at ({r}, {c})")
                        self._place_plot_in_cell(r, c, cfg)
                        return
        
        # If no available cell found, place in first cell (shouldn't happen but safety net)
        print(f"Warning: No available cell found, placing in (0,0)")
        self._place_plot_in_cell(0, 0, cfg)

    def _place_plot_in_cell(self, row: int, col: int, cfg: 'PlotConfig') -> None:
        """Place a plot in a specific grid cell using robust widget management."""
        try:
            # Remove existing widget if any
            existing_widget = self.grid_widgets.get((row, col))
            if existing_widget:
                self.plot_grid_layout.removeWidget(existing_widget)
                existing_widget.deleteLater()
                self.grid_widgets.pop((row, col))
            
            # Create and add new plot panel
            panel = PlotPanel(cfg, parent=self.plot_grid_container)
            self.plot_grid_layout.addWidget(panel, row, col)
            self.grid_widgets[(row, col)] = panel
            self.grid_state[row][col] = f"plot_{cfg.channel}"
            self._plot_panels.append((row, col, panel))
            
        except Exception as e:
            print(f"Error placing plot in cell ({row}, {col}): {e}")
            import traceback
            traceback.print_exc()

    def _delete_plot(self, plot_panel: 'PlotPanel') -> None:
        """Delete a specific plot from the grid."""
        # Find the plot in the grid
        for i, (r, c, panel) in enumerate(self._plot_panels):
            if panel == plot_panel:
                # Remove from grid
                self.plot_grid_layout.removeWidget(panel)
                panel.deleteLater()
                self.grid_widgets.pop((r, c), None)
                self.grid_state[r][c] = None
                self._plot_panels.pop(i)
                print(f"Deleted plot at ({r}, {c})")
                break

    # ----- Add Plot Dialog -----
    def _on_add_plot_clicked(self) -> None:
        try:
            print("Add Plot button clicked")
            dialog = PlotConfigDialog(self)
            print("Dialog created successfully")
            if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                cfg = dialog.get_config()
                print(f"Dialog accepted, config: {cfg.channel}, {cfg.title}")
                self._add_plot_to_grid(cfg)
                print(f"Plot added successfully. Total plots: {len(self._plot_panels)}")
            else:
                print("Dialog cancelled")
        except Exception as e:
            print(f"Error in _on_add_plot_clicked: {e}")
            import traceback
            traceback.print_exc()


# ----- Data classes & UI components -----
class PlotConfig:
    def __init__(self, channel: str, coupling: int, voltage_range: int,
                 y_min: float, y_max: float, y_label: str, title: str, color: QtGui.QColor, formula: str = "") -> None:
        self.channel = channel  # 'A' | 'B' | 'MATH'
        self.coupling = coupling
        self.voltage_range = voltage_range
        self.y_min = y_min
        self.y_max = y_max
        self.y_label = y_label
        self.title = title
        self.color = color
        self.formula = formula  # For math channels


class PlotPanel(QtWidgets.QWidget):
    def __init__(self, config: PlotConfig, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.config = config
        self.channel = config.channel
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        self.plot = pg.PlotWidget(self)
        self.plot.setBackground("w")
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        self.plot.setLabel('left', config.y_label)
        self.plot.setTitle(config.title)
        self.curve = self.plot.plot(pen=pg.mkPen(color=config.color, width=2))
        self.plot.setXRange(0, 60, padding=0)
        self.plot.setYRange(config.y_min, config.y_max, padding=0)
        
        # Allow horizontal scrolling but disable vertical pan/zoom
        self.plot.setMouseEnabled(x=True, y=False)  # Allow horizontal scrolling
        self.plot.hideButtons()
        self.plot.setLimits(xMin=0, xMax=None, yMin=config.y_min, yMax=config.y_max)
        
        # Connect to X range changes for synchronized scrolling
        self.plot.sigRangeChanged.connect(self._on_x_range_changed)
        
        layout.addWidget(self.plot, 1)
        
        # Edit Plot button
        self.edit_button = QtWidgets.QPushButton("Edit Plot", self)
        self.edit_button.clicked.connect(self._on_edit_clicked)
        layout.addWidget(self.edit_button)
        
        # Mirror window on double-click (simplified)
        self._mirror_window: Optional[QtWidgets.QMainWindow] = None
        self._mirror_curve = None
        self._mirror_plot = None
        
        # Simple double-click detection
        self.plot.scene().sigMouseClicked.connect(self._on_mouse_clicked)  # type: ignore[attr-defined]
        
        # Data storage for plotting
        self._data_buffer = []
        self._time_buffer = []

    def update_data(self, timestamp: float, value: float) -> None:
        """Update the plot with new data point."""
        # Ensure we have valid numeric values
        try:
            timestamp = float(timestamp)
            value = float(value)
        except (ValueError, TypeError):
            return  # Skip invalid data
        
        self._time_buffer.append(timestamp)
        self._data_buffer.append(value)
        
        # Dynamic buffer sizing based on timeline and sample rate
        main = self.window()
        if isinstance(main, MainWindow):
            timeline = main.spinbox_timeline.value()
            sample_rate = main.combo_samplerate.currentText().replace(' Hz', '')
            try:
                sample_rate_hz = float(sample_rate)
                # Calculate buffer size: timeline * sample_rate * 1.5 (50% extra for smooth scrolling)
                buffer_size = int(timeline * sample_rate_hz * 1.5)
                buffer_size = max(1000, min(buffer_size, 100000))  # Min 1000, max 100k points
            except (ValueError, AttributeError):
                buffer_size = 1000  # Fallback
        else:
            buffer_size = 1000  # Fallback
        
        # Keep only the last buffer_size points for performance
        if len(self._time_buffer) > buffer_size:
            self._time_buffer = self._time_buffer[-buffer_size:]
            self._data_buffer = self._data_buffer[-buffer_size:]
        
        # Update the plot
        if self._time_buffer and self._data_buffer:
            # Check if curve still exists before updating
            try:
                self.curve.setData(self._time_buffer, self._data_buffer)
            except RuntimeError as e:
                if "wrapped C/C++ object" in str(e):
                    # Curve was deleted, recreate it
                    self.curve = self.plot.plot(pen=pg.mkPen(color=self.config.color, width=2))
                    self.curve.setData(self._time_buffer, self._data_buffer)
                else:
                    raise
            
            # Scroll X range
            if self._time_buffer:
                max_time = float(self._time_buffer[-1])
                min_time = float(self._time_buffer[0])
                # Use global timeline from main window if available
                main = self.window()
                if isinstance(main, MainWindow):
                    timeline = main.spinbox_timeline.value()
                else:
                    timeline = 10.0  # Default timeline
                
                # Always follow the data with a rolling window
                if max_time <= timeline:
                    # If we haven't reached the timeline yet, show from 0 to current max
                    self.plot.setXRange(0, max(timeline, max_time), padding=0)
                else:
                    # Rolling window: show the last 'timeline' seconds of data
                    self.plot.setXRange(max_time - timeline, max_time, padding=0)
                self.plot.setYRange(self.config.y_min, self.config.y_max, padding=0)
            
            # Update mirror window if it exists
            if hasattr(self, '_mirror_curve') and self._mirror_curve is not None:
                try:
                    self._mirror_curve.setData(self._time_buffer, self._data_buffer)
                    # Sync X range with main plot
                    if hasattr(self, '_mirror_plot') and self._mirror_plot is not None:
                        x_range = self.plot.getAxis('bottom').range
                        self._mirror_plot.setXRange(x_range[0], x_range[1], padding=0)
                except RuntimeError:
                    # Mirror curve was deleted, clear the reference
                    self._mirror_curve = None

    def update_data_array(self, time_axis: np.ndarray, data_array: np.ndarray) -> None:
        """Update the plot with an array of data points efficiently."""
        # Ensure we have valid numeric arrays
        try:
            time_axis = np.array(time_axis, dtype=float)
            data_array = np.array(data_array, dtype=float)
        except (ValueError, TypeError):
            return  # Skip invalid data
        
        # Add new data to buffers
        self._time_buffer.extend(time_axis.tolist())
        self._data_buffer.extend(data_array.tolist())
        
        # Dynamic buffer sizing based on timeline and sample rate
        main = self.window()
        if isinstance(main, MainWindow):
            timeline = main.spinbox_timeline.value()
            sample_rate = main.combo_samplerate.currentText().replace(' Hz', '')
            try:
                sample_rate_hz = float(sample_rate)
                # Calculate buffer size: timeline * sample_rate * 1.5 (50% extra for smooth scrolling)
                buffer_size = int(timeline * sample_rate_hz * 1.5)
                buffer_size = max(1000, min(buffer_size, 100000))  # Min 1000, max 100k points
            except (ValueError, AttributeError):
                buffer_size = 1000  # Fallback
        else:
            buffer_size = 1000  # Fallback
        
        # Keep only the last buffer_size points for performance
        if len(self._time_buffer) > buffer_size:
            excess = len(self._time_buffer) - buffer_size
            self._time_buffer = self._time_buffer[excess:]
            self._data_buffer = self._data_buffer[excess:]
        
        # Update the plot
        if self._time_buffer and self._data_buffer:
            # Check if curve still exists before updating
            try:
                self.curve.setData(self._time_buffer, self._data_buffer)
            except RuntimeError as e:
                if "wrapped C/C++ object" in str(e):
                    # Curve was deleted, recreate it
                    self.curve = self.plot.plot(pen=pg.mkPen(color=self.config.color, width=2))
                    self.curve.setData(self._time_buffer, self._data_buffer)
                else:
                    raise
            
            # Scroll X range
            if self._time_buffer:
                max_time = float(self._time_buffer[-1])
                min_time = float(self._time_buffer[0])
                # Use global timeline from main window if available
                main = self.window()
                if isinstance(main, MainWindow):
                    timeline = main.spinbox_timeline.value()
                else:
                    timeline = 10.0  # Default timeline
                
                # Always follow the data with a rolling window
                if max_time <= timeline:
                    # If we haven't reached the timeline yet, show from 0 to current max
                    self.plot.setXRange(0, max(timeline, max_time), padding=0)
                else:
                    # Rolling window: show the last 'timeline' seconds of data
                    self.plot.setXRange(max_time - timeline, max_time, padding=0)
                self.plot.setYRange(self.config.y_min, self.config.y_max, padding=0)
            
            # Update mirror window if it exists
            if hasattr(self, '_mirror_curve') and self._mirror_curve is not None:
                try:
                    self._mirror_curve.setData(self._time_buffer, self._data_buffer)
                    # Sync X range with main plot
                    if hasattr(self, '_mirror_plot') and self._mirror_plot is not None:
                        x_range = self.plot.getAxis('bottom').range
                        self._mirror_plot.setXRange(x_range[0], x_range[1], padding=0)
                except RuntimeError:
                    # Mirror curve was deleted, clear the reference
                    self._mirror_curve = None

    def _on_mouse_clicked(self, ev) -> None:
        # Simple double-click detection - open mirror window
        if ev.double():
            self._open_mirror()

    def _on_edit_clicked(self) -> None:
        """Open edit dialog for this plot."""
        main = self.window()
        if isinstance(main, MainWindow):
            # Create dialog with current config
            dialog = PlotConfigDialog(main)
            dialog.set_config(self.config)
            result = dialog.exec()
            if result == QtWidgets.QDialog.DialogCode.Accepted:
                new_config = dialog.get_config()
                
                # Handle math channel updates
                if self.config.channel == 'MATH' and new_config.channel == 'MATH':
                    # Update math channel configuration in streaming controller
                    from app.processing.math_engine import MathChannelConfig
                    math_config = MathChannelConfig(
                        name=new_config.title,
                        formula=new_config.formula,
                        enabled=True,
                        y_min=new_config.y_min,
                        y_max=new_config.y_max,
                        y_label=new_config.y_label,
                        color=new_config.color
                    )
                    
                    # Update the math channel in the controller
                    success = main.controller.update_math_channel(self.config.title, new_config.title, new_config.formula, math_config)
                    if not success:
                        QtWidgets.QMessageBox.warning(main, "Invalid Formula", 
                            f"Failed to update math channel '{new_config.title}': Invalid formula '{new_config.formula}'")
                        return
                
                # Update this plot's configuration
                self.config = new_config
                self.channel = new_config.channel
                self.plot.setLabel('left', new_config.y_label)
                self.plot.setTitle(new_config.title)
                self.curve.setPen(pg.mkPen(color=new_config.color, width=2))
                self.plot.setYRange(new_config.y_min, new_config.y_max, padding=0)
            elif result == QtWidgets.QDialog.DialogCode.Rejected and dialog.is_edit_mode:
                # Check if delete button was clicked
                if hasattr(dialog, '_delete_clicked') and dialog._delete_clicked:
                    # Delete this plot
                    main._delete_plot(self)
                # Otherwise, just cancel - don't delete

    def _open_mirror(self) -> None:
        if self._mirror_window is None:
            self._mirror_window = QtWidgets.QMainWindow(self)
            self._mirror_window.setWindowTitle(self.config.title or "Plot")
            # Set size to match single plot display (similar to 1x1 grid)
            self._mirror_window.resize(600, 400)
            w = pg.PlotWidget(self._mirror_window)
            w.setBackground("w")
            w.showGrid(x=True, y=True, alpha=0.3)
            w.setLabel('left', self.config.y_label)
            w.setTitle(self.config.title + " (Mirror)")
            
            # Allow horizontal scrolling but disable vertical pan/zoom
            w.setMouseEnabled(x=True, y=False)
            w.hideButtons()
            w.setLimits(xMin=0, xMax=None, yMin=self.config.y_min, yMax=self.config.y_max)
            
            self._mirror_curve = w.plot(pen=pg.mkPen(color=self.config.color, width=2))
            self._mirror_plot = w
            self._mirror_window.setCentralWidget(w)
            
            # Copy current data if available
            if hasattr(self, 'curve') and self.curve is not None:
                try:
                    x_data, y_data = self.curve.getData()
                    if x_data is not None and y_data is not None and len(x_data) > 0 and len(y_data) > 0:
                        self._mirror_curve.setData(x_data, y_data)
                except:
                    # If data is not available, just set empty data
                    self._mirror_curve.setData([], [])
            
            # Always copy the current Y and X axis ranges from the main plot
            w.setYRange(self.config.y_min, self.config.y_max, padding=0)
            x_range = self.plot.getAxis('bottom').range
            w.setXRange(x_range[0], x_range[1], padding=0)
        
        self._mirror_window.show()
        self._mirror_window.raise_()


    def clear(self) -> None:
        # Clear data buffers
        self._time_buffer.clear()
        self._data_buffer.clear()
        
        try:
            self.curve.setData([], [])
        except RuntimeError as e:
            if "wrapped C/C++ object" in str(e):
                # Curve was deleted, recreate it
                self.curve = self.plot.plot(pen=pg.mkPen(color=self.config.color, width=2))
                self.curve.setData([], [])
            else:
                raise
        
        self.plot.setXRange(0,  self._get_timeline(), padding=0)
        self.plot.setYRange(self.config.y_min, self.config.y_max, padding=0)
        
        if hasattr(self, '_mirror_curve') and self._mirror_curve is not None:
            try:
                self._mirror_curve.setData([], [])
            except RuntimeError as e:
                if "wrapped C/C++ object" in str(e):
                    # Mirror curve was deleted, clear the reference
                    self._mirror_curve = None
                else:
                    raise

    def _get_timeline(self) -> float:
        main = self.window()
        if isinstance(main, MainWindow):
            return main.spinbox_timeline.value()
        return 60.0
    
    def _on_x_range_changed(self, plot, ranges) -> None:
        """Handle X range changes and sync with other plots."""
        # Only sync if this is a user interaction (not programmatic)
        if hasattr(self, '_syncing') and self._syncing:
            return
        
        # Get the main window and sync all other plots
        main = self.window()
        if isinstance(main, MainWindow):
            x_range = ranges[0]  # X range is first element
            main._sync_all_plots_x_range(x_range[0], x_range[1], self)


class PlotConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Plot")
        layout = QtWidgets.QFormLayout(self)

        self.combo_channel = QtWidgets.QComboBox(self)
        
        # Get available channels from controller if available
        if parent and hasattr(parent, 'controller') and hasattr(parent.controller, 'get_available_channels'):
            available_channels = parent.controller.get_available_channels()
            # Add physical channels
            for channel in available_channels:
                self.combo_channel.addItem(channel)
        else:
            # Fallback to default channels
            self.combo_channel.addItems(["A", "B"])
        
        # Always add Math channel
        self.combo_channel.addItem("Math")
        layout.addRow("Channel:", self.combo_channel)

        # Create containers for coupling and range to hide entire rows
        self.coupling_container = QtWidgets.QWidget(self)
        coupling_layout = QtWidgets.QHBoxLayout(self.coupling_container)
        coupling_layout.setContentsMargins(0, 0, 0, 0)
        self.combo_coupling = QtWidgets.QComboBox(self)
        self.combo_coupling.addItems(["DC", "AC"])
        coupling_layout.addWidget(self.combo_coupling)
        coupling_layout.addStretch()  # Add stretch to align with other fields
        layout.addRow("Coupling:", self.coupling_container)

        self.range_container = QtWidgets.QWidget(self)
        range_layout = QtWidgets.QHBoxLayout(self.range_container)
        range_layout.setContentsMargins(0, 0, 0, 0)
        self.combo_range = QtWidgets.QComboBox(self)
        for label, enum_val in [("±10 mV",0),("±20 mV",1),("±50 mV",2),("±100 mV",3),("±200 mV",4),("±500 mV",5),("±1 V",6),("±2 V",7),("±5 V",8),("±10 V",9)]:
            self.combo_range.addItem(label, userData=enum_val)
        self.combo_range.setCurrentIndex(9)
        range_layout.addWidget(self.combo_range)
        range_layout.addStretch()  # Add stretch to align with other fields
        layout.addRow("Range:", self.range_container)

        self.spin_ymax = QtWidgets.QDoubleSpinBox(self); self.spin_ymax.setRange(0.1, 100.0); self.spin_ymax.setValue(10.0); self.spin_ymax.setSuffix(" V"); self.spin_ymax.setDecimals(1)
        self.spin_ymin = QtWidgets.QDoubleSpinBox(self); self.spin_ymin.setRange(-100.0, -0.1); self.spin_ymin.setValue(-10.0); self.spin_ymin.setSuffix(" V"); self.spin_ymin.setDecimals(1)
        layout.addRow("Y-Axis Max:", self.spin_ymax)
        layout.addRow("Y-Axis Min:", self.spin_ymin)

        self.edit_ylabel = QtWidgets.QLineEdit(self)
        layout.addRow("Y-Axis Label:", self.edit_ylabel)

        self.edit_title = QtWidgets.QLineEdit(self)
        layout.addRow("Plot Title:", self.edit_title)

        # Formula input field for Math channels
        self.edit_formula = QtWidgets.QLineEdit(self)
        self.edit_formula.setPlaceholderText("Enter formula (e.g., A + B, A * B, sqrt(A))")
        self.edit_formula.setToolTip("Use A and B as variables. Supported functions: +, -, *, /, ^, sqrt(), sin(), cos(), log(), etc.")
        layout.addRow("Formula:", self.edit_formula)
        
        # Formula validation label
        self.label_formula_status = QtWidgets.QLabel("")
        self.label_formula_status.setStyleSheet("color: red; font-size: 10px;")
        layout.addRow("", self.label_formula_status)

        self.button_color = QtWidgets.QPushButton("Choose Color", self)
        # Random color assignment
        import random
        self._color = QtGui.QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.button_color.clicked.connect(self._choose_color)
        self.button_color.setStyleSheet(f"background-color: {self._color.name()};")
        layout.addRow("Color:", self.button_color)

        # Create buttons based on mode
        self.is_edit_mode = False
        self._delete_clicked = False
        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Save | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

        # Hide coupling/range when Math selected and auto-update title
        self.combo_channel.currentTextChanged.connect(self._on_channel_changed)
        self._on_channel_changed(self.combo_channel.currentText())
        self._update_default_labels()
        self.combo_channel.currentTextChanged.connect(self._update_default_labels)

    def _choose_color(self) -> None:
        color = QtWidgets.QColorDialog.getColor(self._color, self, "Select Line Color")
        if color.isValid():
            self._color = color
            self.button_color.setStyleSheet(f"background-color: {color.name()};")

    def _on_channel_changed(self, text: str) -> None:
        is_math = text.lower() == 'math'
        
        # Hide/show containers (which include the labels)
        self.coupling_container.setVisible(not is_math)
        self.range_container.setVisible(not is_math)
        
        # Show/hide formula fields
        self.edit_formula.setVisible(is_math)
        self.label_formula_status.setVisible(is_math)
        
        # Connect formula validation when Math is selected
        if is_math:
            self.edit_formula.textChanged.connect(self._validate_formula)
        else:
            try:
                self.edit_formula.textChanged.disconnect(self._validate_formula)
            except TypeError:
                pass  # Not connected yet

    def _update_default_labels(self) -> None:
        ch = self.combo_channel.currentText().upper()
        if ch == 'A' or ch == 'B':
            self.edit_ylabel.setText('Volts')
            # Always update title to match channel selection
            self.edit_title.setText(f"Channel {ch}")
        else:
            if not self.edit_ylabel.text():
                self.edit_ylabel.setText('')
            # Always update title to match channel selection
            self.edit_title.setText('Math Channel')

    def _validate_formula(self) -> None:
        """Validate the current formula and update status label."""
        formula = self.edit_formula.text().strip()
        
        if not formula:
            self.label_formula_status.setText("")
            return
        
        # Import math engine for validation
        try:
            from app.processing.math_engine import MathEngine
            engine = MathEngine()
            is_valid, error_msg = engine.validate_formula(formula)
            
            if is_valid:
                self.label_formula_status.setText("✓ Formula is valid")
                self.label_formula_status.setStyleSheet("color: green; font-size: 10px;")
            else:
                self.label_formula_status.setText(f"✗ {error_msg}")
                self.label_formula_status.setStyleSheet("color: red; font-size: 10px;")
        except Exception as e:
            self.label_formula_status.setText(f"✗ Validation error: {e}")
            self.label_formula_status.setStyleSheet("color: red; font-size: 10px;")

    def set_config(self, config: PlotConfig) -> None:
        """Set the dialog fields from an existing config."""
        # Set formula first (for math channels) before changing channel
        if hasattr(config, 'formula'):
            self.edit_formula.setText(config.formula)
        
        # Set channel (this will trigger _on_channel_changed)
        channel_index = self.combo_channel.findText(config.channel)
        if channel_index >= 0:
            self.combo_channel.setCurrentIndex(channel_index)
        
        # Set coupling
        coupling_text = "DC" if config.coupling == 1 else "AC"
        coupling_index = self.combo_coupling.findText(coupling_text)
        if coupling_index >= 0:
            self.combo_coupling.setCurrentIndex(coupling_index)
        
        # Set range
        for i in range(self.combo_range.count()):
            if self.combo_range.itemData(i) == config.voltage_range:
                self.combo_range.setCurrentIndex(i)
                break
        
        # Set Y-axis values
        self.spin_ymin.setValue(config.y_min)
        self.spin_ymax.setValue(config.y_max)
        
        # Set labels
        self.edit_ylabel.setText(config.y_label)
        self.edit_title.setText(config.title)
        
        # Set color
        self._color = config.color
        self.button_color.setStyleSheet(f"background-color: {config.color.name()};")
        
        # Set edit mode
        self.set_edit_mode(True)

    def set_edit_mode(self, is_edit: bool) -> None:
        """Set the dialog to edit mode and add delete button if needed."""
        self.is_edit_mode = is_edit
        if is_edit:
            # Add delete button
            delete_button = self.buttons.addButton("Delete", QtWidgets.QDialogButtonBox.ButtonRole.DestructiveRole)
            delete_button.clicked.connect(self._on_delete_clicked)
            self.setWindowTitle("Edit Plot")
        else:
            self.setWindowTitle("Add Plot")

    def _on_delete_clicked(self) -> None:
        """Handle delete button click."""
        self._delete_clicked = True
        self.done(QtWidgets.QDialog.DialogCode.Rejected)  # Use rejected to signal delete

    def get_config(self) -> PlotConfig:
        ch_text = self.combo_channel.currentText().upper()
        channel = 'MATH' if ch_text == 'MATH' else ch_text
        coupling = 1 if self.combo_coupling.currentText() == 'DC' else 0
        voltage_range = int(self.combo_range.currentData() or 9)
        formula = self.edit_formula.text().strip() if ch_text == 'MATH' else ""
        return PlotConfig(
            channel=channel,
            coupling=coupling,
            voltage_range=voltage_range,
            y_min=self.spin_ymin.value(),
            y_max=self.spin_ymax.value(),
            y_label=self.edit_ylabel.text(),
            title=self.edit_title.text(),
            color=self._color,
            formula=formula,
        )



