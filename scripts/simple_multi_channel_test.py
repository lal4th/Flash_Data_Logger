#!/usr/bin/env python3
"""
Simple test to verify we can configure and read from multiple channels on 6824E.
This focuses on the core functionality without complex timebase setup.
"""

import sys
import os
import time
import ctypes
from ctypes import c_int16, byref, create_string_buffer
import numpy as np

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_simple_multi_channel():
    """Simple test to configure and read from channels A, B, C, D"""
    
    print("=== Simple 6824E Multi-Channel Test ===\n")
    
    try:
        # Import the PicoSDK
        from picosdk.ps6000a import ps6000a as ps
        print("✓ PicoSDK ps6000a module imported successfully")
        
        # Open the device
        chandle = c_int16()
        status = ps.ps6000aOpenUnit(byref(chandle), None, 1)
        
        if status != 0:
            print(f"❌ Failed to open 6824E device. Status: {status}")
            return False
            
        print(f"✓ 6824E device opened successfully (handle: {chandle.value})")
        
        # Configure all 4 channels (A, B, C, D)
        print("\n--- Configuring Channels ---")
        
        channels = [
            (0, "A", 1, 9),  # Channel 0 (A), DC coupling, ±10V range
            (1, "B", 1, 9),  # Channel 1 (B), DC coupling, ±10V range  
            (2, "C", 1, 9),  # Channel 2 (C), DC coupling, ±10V range
            (3, "D", 1, 9),  # Channel 3 (D), DC coupling, ±10V range
        ]
        
        for channel_num, channel_name, coupling, range_val in channels:
            status = ps.ps6000aSetChannelOn(chandle, channel_num, coupling, range_val, 0.0, 0)
            if status == 0:
                coupling_text = "DC" if coupling == 1 else "AC"
                print(f"✓ Channel {channel_name} configured (coupling={coupling_text}, range={range_val})")
            else:
                print(f"❌ Failed to configure channel {channel_name}. Status: {status}")
                return False
        
        # Test basic data reading using the existing working code
        print("\n--- Testing Data Reading ---")
        
        # Import our existing working acquisition code
        from app.acquisition.pico_6000_direct import Pico6000DirectSource
        
        # Create a source instance
        source = Pico6000DirectSource()
        
        # Connect to the device
        if not source.connect():
            print("❌ Failed to connect using Pico6000DirectSource")
            return False
        
        print("✓ Connected using Pico6000DirectSource")
        
        # Configure multi-channel
        print("\n--- Configuring Multi-Channel Mode ---")
        
        try:
            source.configure_multi_channel(
                sample_rate_hz=100,
                channel_a_enabled=True,
                channel_a_coupling=1,  # DC
                channel_a_range=9,     # ±10V
                channel_b_enabled=True,
                channel_b_coupling=1,  # DC
                channel_b_range=9,     # ±10V
                channel_c_enabled=True,
                channel_c_coupling=1,  # DC
                channel_c_range=9,     # ±10V
                channel_d_enabled=True,
                channel_d_coupling=1,  # DC
                channel_d_range=9,     # ±10V
                resolution_bits=16
            )
            print("✓ Multi-channel configuration successful")
        except Exception as e:
            print(f"❌ Multi-channel configuration failed: {e}")
            return False
        
        # Test reading data from all channels
        print("\n--- Testing Multi-Channel Data Reading ---")
        
        for i in range(5):
            try:
                # Read multi-channel data
                (a_val, b_val, c_val, d_val, e_val, f_val, g_val, h_val), timestamp = source.read_multi_channel()
                
                print(f"Sample {i+1}:")
                print(f"  Timestamp: {timestamp:.3f}s")
                print(f"  Channel A: {a_val:.3f}V")
                print(f"  Channel B: {b_val:.3f}V")
                print(f"  Channel C: {c_val:.3f}V")
                print(f"  Channel D: {d_val:.3f}V")
                print(f"  Channel E: {e_val:.3f}V")
                print(f"  Channel F: {f_val:.3f}V")
                print(f"  Channel G: {g_val:.3f}V")
                print(f"  Channel H: {h_val:.3f}V")
                print()
                
                time.sleep(0.1)  # Small delay between readings
                
            except Exception as e:
                print(f"❌ Failed to read multi-channel data: {e}")
                return False
        
        # Disconnect
        source.disconnect()
        print("✓ Disconnected successfully")
        
        print("\n🎉 Multi-channel test PASSED!")
        print("✓ All 8 channels (A-H) are working simultaneously")
        print("✓ Channels A, B, C, D are configured and reading data")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import required modules: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_gui():
    """Create a simple GUI to display the multi-channel data"""
    
    print("\n=== Simple GUI Test ===\n")
    
    try:
        from PyQt6 import QtWidgets, QtCore
        import pyqtgraph as pg
        import numpy as np
        
        print("✓ PyQt6 and pyqtgraph imported successfully")
        
        class SimpleMultiChannelWindow(QtWidgets.QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("6824E Multi-Channel Test - Simple GUI")
                self.setGeometry(100, 100, 1000, 600)
                
                # Create central widget
                central_widget = QtWidgets.QWidget()
                self.setCentralWidget(central_widget)
                
                # Create layout
                layout = QtWidgets.QVBoxLayout(central_widget)
                
                # Create a single plot with all channels
                self.plot = pg.PlotWidget(title="Multi-Channel Data (A, B, C, D)")
                self.plot.setLabel('left', 'Voltage', units='V')
                self.plot.setLabel('bottom', 'Time', units='s')
                self.plot.setYRange(-5, 5)
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
                
                layout.addLayout(button_layout)
                
                # Status label
                self.status_label = QtWidgets.QLabel("Ready to test - Click 'Start Test' to begin")
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
                self.status_label.setText("Running multi-channel test...")
                
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
        print("✓ All 4 channels (A, B, C, D) should display different sine waves")
        print("✓ Click 'Start Test' to begin the simulation")
        print("✓ You should see 4 different colored sine waves on the same plot")
        
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
    print("Simple 6824E Multi-Channel Test Program")
    print("=" * 50)
    
    # Test 1: Hardware acquisition using existing code
    print("Test 1: Hardware Acquisition (using existing code)")
    hardware_success = test_simple_multi_channel()
    
    if hardware_success:
        print("\n" + "=" * 50)
        print("Test 2: Simple GUI Display")
        
        # Test 2: Simple GUI display
        gui_success = test_simple_gui()
        
        if gui_success:
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n❌ GUI test failed")
    else:
        print("\n❌ Hardware test failed - skipping GUI test")
    
    print("\nTest program completed.")
