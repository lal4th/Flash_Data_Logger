#!/usr/bin/env python3
"""
Simple GUI test to demonstrate multi-channel data display.
This shows what the multi-channel data should look like when working correctly.
"""

import sys
import os
import time
import numpy as np

def test_simple_gui():
    """Create a simple GUI to display simulated multi-channel data"""
    
    print("=== Simple Multi-Channel GUI Test ===\n")
    
    try:
        from PyQt6 import QtWidgets, QtCore
        import pyqtgraph as pg
        
        print("✓ PyQt6 and pyqtgraph imported successfully")
        
        class SimpleMultiChannelWindow(QtWidgets.QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("6824E Multi-Channel Test - What You Should See")
                self.setGeometry(100, 100, 1200, 800)
                
                # Create central widget
                central_widget = QtWidgets.QWidget()
                self.setCentralWidget(central_widget)
                
                # Create layout
                layout = QtWidgets.QVBoxLayout(central_widget)
                
                # Create a single plot with all channels
                self.plot = pg.PlotWidget(title="Multi-Channel Data (A, B, C, D) - Simulated")
                self.plot.setLabel('left', 'Voltage', units='V')
                self.plot.setLabel('bottom', 'Time', units='s')
                self.plot.setYRange(-5, 5)
                self.plot.addLegend()
                layout.addWidget(self.plot)
                
                # Create curves for each channel
                self.curves = {}
                colors = ['blue', 'red', 'green', 'orange']
                channels = ['A', 'B', 'C', 'D']
                
                for channel, color in zip(channels, colors):
                    curve = self.plot.plot(pen=color, name=f"Channel {channel}")
                    self.curves[channel] = curve
                
                # Create control buttons
                button_layout = QtWidgets.QHBoxLayout()
                
                self.start_button = QtWidgets.QPushButton("Start Test")
                self.start_button.clicked.connect(self.start_test)
                button_layout.addWidget(self.start_button)
                
                self.stop_button = QtWidgets.QPushButton("Stop Test")
                self.stop_button.clicked.connect(self.stop_test)
                self.stop_button.setEnabled(False)
                button_layout.addWidget(self.stop_button)
                
                self.clear_button = QtWidgets.QPushButton("Clear")
                self.clear_button.clicked.connect(self.clear_data)
                button_layout.addWidget(self.clear_button)
                
                layout.addLayout(button_layout)
                
                # Status label
                self.status_label = QtWidgets.QLabel("Ready to test - Click 'Start Test' to see simulated multi-channel data")
                layout.addWidget(self.status_label)
                
                # Timer for data updates
                self.timer = QtCore.QTimer()
                self.timer.timeout.connect(self.update_data)
                
                # Data storage
                self.time_data = []
                self.channel_data = {channel: [] for channel in channels}
                self.start_time = None
                
            def start_test(self):
                """Start the data acquisition test"""
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.status_label.setText("Running multi-channel simulation...")
                
                # Clear previous data
                self.time_data = []
                for channel in self.channel_data:
                    self.channel_data[channel] = []
                
                self.start_time = time.time()
                self.timer.start(50)  # Update every 50ms
                
            def stop_test(self):
                """Stop the data acquisition test"""
                self.timer.stop()
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.status_label.setText("Test stopped")
                
            def clear_data(self):
                """Clear all data"""
                self.timer.stop()
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                
                self.time_data = []
                for channel in self.channel_data:
                    self.channel_data[channel] = []
                
                # Clear the plots
                for curve in self.curves.values():
                    curve.setData([], [])
                
                self.status_label.setText("Data cleared - Click 'Start Test' to begin")
                
            def update_data(self):
                """Update the plot data with simulated multi-channel signals"""
                if self.start_time is None:
                    return
                
                current_time = time.time() - self.start_time
                
                # Generate simulated data for each channel
                # This simulates what we should get from the 6824E
                channel_values = {
                    'A': 2.0 * np.sin(2 * np.pi * 1.0 * current_time),  # 1Hz sine wave
                    'B': 1.5 * np.sin(2 * np.pi * 2.0 * current_time),  # 2Hz sine wave
                    'C': 1.0 * np.sin(2 * np.pi * 3.0 * current_time),  # 3Hz sine wave
                    'D': 0.5 * np.sin(2 * np.pi * 4.0 * current_time),  # 4Hz sine wave
                }
                
                # Store data
                self.time_data.append(current_time)
                for channel, value in channel_values.items():
                    self.channel_data[channel].append(value)
                
                # Keep only last 200 points
                if len(self.time_data) > 200:
                    self.time_data = self.time_data[-200:]
                    for channel in self.channel_data:
                        self.channel_data[channel] = self.channel_data[channel][-200:]
                
                # Update plots
                for channel, curve in self.curves.items():
                    if len(self.time_data) > 0 and len(self.channel_data[channel]) > 0:
                        curve.setData(self.time_data, self.channel_data[channel])
                
                # Update status
                self.status_label.setText(f"Running... Time: {current_time:.1f}s | "
                                        f"A: {channel_values['A']:.2f}V | "
                                        f"B: {channel_values['B']:.2f}V | "
                                        f"C: {channel_values['C']:.2f}V | "
                                        f"D: {channel_values['D']:.2f}V")
        
        # Create and show the GUI
        app = QtWidgets.QApplication(sys.argv)
        window = SimpleMultiChannelWindow()
        window.show()
        
        print("✓ Simple GUI created successfully")
        print("✓ This shows what multi-channel data SHOULD look like")
        print("✓ All 4 channels (A, B, C, D) display different sine waves")
        print("✓ Click 'Start Test' to begin the simulation")
        print("✓ You should see 4 different colored sine waves on the same plot:")
        print("  - Channel A: Blue, 1Hz sine wave")
        print("  - Channel B: Red, 2Hz sine wave") 
        print("  - Channel C: Green, 3Hz sine wave")
        print("  - Channel D: Orange, 4Hz sine wave")
        print("\nThis is what your Flash Data Logger should display when working correctly!")
        
        # Run the GUI
        app.exec()
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import GUI libraries: {e}")
        print("  Make sure PyQt6 and pyqtgraph are installed")
        return False
    except Exception as e:
        print(f"❌ GUI error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Simple Multi-Channel GUI Test")
    print("=" * 50)
    print("This test shows what multi-channel data should look like")
    print("when all channels (A, B, C, D) are working correctly.")
    print("=" * 50)
    
    success = test_simple_gui()
    
    if success:
        print("\n🎉 GUI test completed successfully!")
        print("This demonstrates what your Flash Data Logger should show")
        print("when channels C and D are working correctly.")
    else:
        print("\n❌ GUI test failed")
    
    print("\nTest program completed.")
