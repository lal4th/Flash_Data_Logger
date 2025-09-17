#!/usr/bin/env python3
"""
6824E Test GUI
Simple PyQt6 application to test connection and configuration of PicoScope 6824E

This demonstrates that we can successfully communicate with the 6824E device.
"""

import sys
import traceback
from typing import Optional, Dict, Any
import ctypes
from ctypes import c_int16, byref, create_string_buffer

try:
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                                QGroupBox, QComboBox, QSpinBox, QCheckBox,
                                QMessageBox, QProgressBar)
    from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
    from PyQt6.QtGui import QFont
except ImportError:
    print("PyQt6 not available, trying PyQt5...")
    try:
        from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                    QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                                    QGroupBox, QComboBox, QSpinBox, QCheckBox,
                                    QMessageBox, QProgressBar)
        from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
        from PyQt5.QtGui import QFont
    except ImportError:
        print("Neither PyQt6 nor PyQt5 available. Please install PyQt6: pip install PyQt6")
        sys.exit(1)

try:
    from picosdk.ps6000a import ps6000a as ps
    PICO_AVAILABLE = True
except ImportError:
    PICO_AVAILABLE = False
    print("Warning: picosdk.ps6000a not available")


class PicoScopeWorker(QThread):
    """Worker thread for PicoScope operations"""
    status_update = pyqtSignal(str)
    operation_complete = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self.operation = None
        self.params = {}
        self.device_handle = None
        self.is_connected = False
        
    def set_operation(self, operation: str, **params):
        self.operation = operation
        self.params = params
        
    def run(self):
        if not PICO_AVAILABLE:
            self.operation_complete.emit(False, "PicoSDK not available")
            return
            
        try:
            if self.operation == "connect":
                self._connect_device()
            elif self.operation == "get_info":
                self._get_device_info()
            elif self.operation == "configure_channel":
                self._configure_channel()
            elif self.operation == "disconnect":
                self._disconnect_device()
            else:
                self.operation_complete.emit(False, f"Unknown operation: {self.operation}")
                
        except Exception as e:
            self.operation_complete.emit(False, f"Error: {str(e)}")
            
    def _connect_device(self):
        self.status_update.emit("Opening 6824E device...")
        
        # Create handle
        chandle = c_int16()
        status = ps.ps6000aOpenUnit(byref(chandle), None, 1)
        
        if status == 0:
            self.device_handle = chandle.value
            self.is_connected = True
            self.status_update.emit("✓ Successfully connected to 6824E")
            self.operation_complete.emit(True, f"Connected with handle: {chandle.value}")
        else:
            error_msg = self._get_status_message(status)
            self.status_update.emit(f"❌ Connection failed: {error_msg}")
            self.operation_complete.emit(False, f"Status {status}: {error_msg}")
            
    def _get_device_info(self):
        self.status_update.emit("Getting device information...")
        
        if not self.is_connected or self.device_handle is None:
            self.operation_complete.emit(False, "Device not connected. Please connect first.")
            return
            
        try:
            # Use existing handle
            chandle = c_int16(self.device_handle)
            
            # Get unit info
            buffer = create_string_buffer(256)
            required_len = c_int16()
            
            # Get model info
            ps.ps6000aGetUnitInfo(chandle, buffer, c_int16(len(buffer)), byref(required_len), 3)
            model = buffer.value.decode(errors="ignore")
            
            # Get serial number
            ps.ps6000aGetUnitInfo(chandle, buffer, c_int16(len(buffer)), byref(required_len), 0)
            serial = buffer.value.decode(errors="ignore")
            
            # Get firmware version
            ps.ps6000aGetUnitInfo(chandle, buffer, c_int16(len(buffer)), byref(required_len), 1)
            firmware = buffer.value.decode(errors="ignore")
            
            info = f"Model: {model}\nSerial: {serial}\nFirmware: {firmware}"
            self.status_update.emit("✓ Device information retrieved")
            self.operation_complete.emit(True, info)
            
        except Exception as e:
            self.operation_complete.emit(False, f"Error getting device info: {str(e)}")
            
    def _configure_channel(self):
        self.status_update.emit("Configuring channel...")
        
        if not self.is_connected or self.device_handle is None:
            self.operation_complete.emit(False, "Device not connected. Please connect first.")
            return
            
        try:
            # Use existing handle
            chandle = c_int16(self.device_handle)
            
            channel = self.params.get('channel', 0)  # Channel A
            coupling = self.params.get('coupling', 1)  # DC
            range_val = self.params.get('range', 7)  # 5V range
            enabled = self.params.get('enabled', True)
            
            status = ps.ps6000aSetChannel(chandle, channel, 1 if enabled else 0, coupling, range_val, 0, 0)
            
            if status == 0:
                self.status_update.emit("✓ Channel configured successfully")
                self.operation_complete.emit(True, f"Channel {channel} configured")
            else:
                self.operation_complete.emit(False, f"Channel configuration failed: {self._get_status_message(status)}")
                
        except Exception as e:
            self.operation_complete.emit(False, f"Error configuring channel: {str(e)}")
            
    def _disconnect_device(self):
        self.status_update.emit("Disconnecting device...")
        
        if self.is_connected and self.device_handle is not None:
            try:
                chandle = c_int16(self.device_handle)
                ps.ps6000aCloseUnit(chandle)
                self.device_handle = None
                self.is_connected = False
                self.status_update.emit("✓ Device disconnected")
                self.operation_complete.emit(True, "Device disconnected")
            except Exception as e:
                self.operation_complete.emit(False, f"Error disconnecting: {str(e)}")
        else:
            self.status_update.emit("✓ Device already disconnected")
            self.operation_complete.emit(True, "Device was not connected")
        
    def _get_status_message(self, status: int) -> str:
        status_codes = {
            0: "Success",
            3: "PICO_NOT_FOUND - Device not found or PicoScope app running",
            4: "PICO_INVALID_PARAMETER",
            5: "PICO_INVALID_HANDLE - Device already open",
            288: "PICO_DEVICE_TIME_STAMP_RESET - Device timestamp reset",
            268435457: "DLL dependency issue"
        }
        return status_codes.get(status, f"Unknown status {status}")


class Test6824EGUI(QMainWindow):
    """Main GUI window for testing 6824E connection and configuration"""
    
    def __init__(self):
        super().__init__()
        self.worker = PicoScopeWorker()
        self.worker.status_update.connect(self.update_status)
        self.worker.operation_complete.connect(self.operation_complete)
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("6824E PicoScope Test GUI")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("PicoScope 6824E Connection Test")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Status section
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("Ready to test 6824E connection")
        self.status_label.setStyleSheet("color: blue; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_group)
        
        # Control buttons
        control_group = QGroupBox("Device Operations")
        control_layout = QVBoxLayout(control_group)
        
        # Connection buttons
        conn_layout = QHBoxLayout()
        
        self.btn_connect = QPushButton("Connect to 6824E")
        self.btn_connect.clicked.connect(self.connect_device)
        conn_layout.addWidget(self.btn_connect)
        
        self.btn_info = QPushButton("Get Device Info")
        self.btn_info.clicked.connect(self.get_device_info)
        conn_layout.addWidget(self.btn_info)
        
        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.clicked.connect(self.disconnect_device)
        conn_layout.addWidget(self.btn_disconnect)
        
        control_layout.addLayout(conn_layout)
        
        # Channel configuration
        channel_group = QGroupBox("Channel Configuration")
        channel_layout = QVBoxLayout(channel_group)
        
        # Channel selection
        channel_row = QHBoxLayout()
        channel_row.addWidget(QLabel("Channel:"))
        
        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["A", "B", "C", "D"])
        channel_row.addWidget(self.channel_combo)
        
        channel_row.addWidget(QLabel("Coupling:"))
        self.coupling_combo = QComboBox()
        self.coupling_combo.addItems(["AC", "DC"])
        channel_row.addWidget(self.coupling_combo)
        
        channel_row.addWidget(QLabel("Range:"))
        self.range_combo = QComboBox()
        self.range_combo.addItems(["10mV", "20mV", "50mV", "100mV", "200mV", "500mV", "1V", "2V", "5V", "10V", "20V"])
        self.range_combo.setCurrentText("5V")
        channel_row.addWidget(self.range_combo)
        
        channel_layout.addLayout(channel_row)
        
        # Channel enable
        self.channel_enable = QCheckBox("Enable Channel")
        self.channel_enable.setChecked(True)
        channel_layout.addWidget(self.channel_enable)
        
        self.btn_configure = QPushButton("Configure Channel")
        self.btn_configure.clicked.connect(self.configure_channel)
        channel_layout.addWidget(self.btn_configure)
        
        control_layout.addWidget(channel_group)
        layout.addWidget(control_group)
        
        # Results section
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
        # Log section
        log_group = QGroupBox("Operation Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Initial status
        self.log_message("6824E Test GUI initialized")
        if not PICO_AVAILABLE:
            self.log_message("WARNING: PicoSDK not available - install with: pip install picosdk")
            self.status_label.setText("PicoSDK not available")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            
    def log_message(self, message: str):
        """Add message to log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def update_status(self, message: str):
        """Update status from worker thread"""
        self.status_label.setText(message)
        self.log_message(message)
        
    def operation_complete(self, success: bool, result: str):
        """Handle operation completion"""
        self.progress_bar.setVisible(False)
        
        if success:
            self.results_text.append(f"✓ SUCCESS: {result}")
            self.log_message(f"Operation completed successfully: {result}")
        else:
            self.results_text.append(f"❌ FAILED: {result}")
            self.log_message(f"Operation failed: {result}")
            
    def connect_device(self):
        """Connect to 6824E device"""
        if not PICO_AVAILABLE:
            QMessageBox.warning(self, "Error", "PicoSDK not available")
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.worker.set_operation("connect")
        self.worker.start()
        
    def get_device_info(self):
        """Get device information"""
        if not PICO_AVAILABLE:
            QMessageBox.warning(self, "Error", "PicoSDK not available")
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.worker.set_operation("get_info")
        self.worker.start()
        
    def configure_channel(self):
        """Configure selected channel"""
        if not PICO_AVAILABLE:
            QMessageBox.warning(self, "Error", "PicoSDK not available")
            return
            
        # Map UI values to API values
        channel_map = {"A": 0, "B": 1, "C": 2, "D": 3}
        coupling_map = {"AC": 0, "DC": 1}
        range_map = {"10mV": 0, "20mV": 1, "50mV": 2, "100mV": 3, "200mV": 4, 
                    "500mV": 5, "1V": 6, "2V": 7, "5V": 8, "10V": 9, "20V": 10}
        
        params = {
            'channel': channel_map[self.channel_combo.currentText()],
            'coupling': coupling_map[self.coupling_combo.currentText()],
            'range': range_map[self.range_combo.currentText()],
            'enabled': self.channel_enable.isChecked()
        }
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.worker.set_operation("configure_channel", **params)
        self.worker.start()
        
    def disconnect_device(self):
        """Disconnect from device"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.worker.set_operation("disconnect")
        self.worker.start()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Check dependencies
    if not PICO_AVAILABLE:
        reply = QMessageBox.question(None, "PicoSDK Missing", 
                                   "PicoSDK is not available. Install with: pip install picosdk\n\n"
                                   "Continue anyway to test GUI?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            sys.exit(1)
    
    # Create and show main window
    window = Test6824EGUI()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
