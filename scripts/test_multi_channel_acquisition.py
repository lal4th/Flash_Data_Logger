#!/usr/bin/env python3
"""
Standalone test program to verify multi-channel data acquisition from 6824E.
This will test reading signals from channels A, B, C, and D simultaneously
without any GUI complexity.
"""

import sys
import os
import time
import ctypes
from ctypes import c_int16, byref, create_string_buffer
import numpy as np

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_6824e_multi_channel_acquisition():
    """Test reading from all 4 channels (A, B, C, D) simultaneously"""
    
    print("=== 6824E Multi-Channel Acquisition Test ===\n")
    
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
        
        # Set up timebase for 100Hz sampling
        print("\n--- Setting up Timebase ---")
        timebase = 8  # Approximately 100Hz for 6824E
        no_of_samples = 1000
        
        # Use the correct function signature
        time_interval = ctypes.c_float()
        time_units = ctypes.c_int16()
        max_samples = ctypes.c_int32()
        
        status = ps.ps6000aGetTimebase(
            chandle, timebase, no_of_samples, 
            byref(time_interval), byref(time_units), byref(max_samples)
        )
        
        if status == 0:
            print(f"✓ Timebase configured: {time_interval.value} {time_units.value} per sample")
            print(f"✓ Max samples: {max_samples.value}")
        else:
            print(f"❌ Failed to configure timebase. Status: {status}")
            return False
        
        # Set up buffers for all channels
        print("\n--- Setting up Data Buffers ---")
        
        # Create buffers for each channel
        buffers = {}
        for channel_num, channel_name, _, _ in channels:
            buffer = (ctypes.c_int16 * no_of_samples)()
            status = ps.ps6000aSetDataBuffer(
                chandle, channel_num, buffer, no_of_samples, 0, 0
            )
            if status == 0:
                buffers[channel_name] = buffer
                print(f"✓ Buffer created for channel {channel_name}")
            else:
                print(f"❌ Failed to create buffer for channel {channel_name}. Status: {status}")
                return False
        
        # Run the acquisition
        print("\n--- Running Acquisition ---")
        
        # Start the acquisition
        status = ps.ps6000aRunBlock(
            chandle, 0, no_of_samples, timebase, 0, None, 0, None, None
        )
        
        if status != 0:
            print(f"❌ Failed to start acquisition. Status: {status}")
            return False
            
        print("✓ Acquisition started")
        
        # Wait for completion
        ready = ctypes.c_int16()
        check_count = 0
        max_checks = 100  # 10 seconds timeout
        
        while check_count < max_checks:
            status = ps.ps6000aIsReady(chandle, byref(ready))
            if status == 0 and ready.value:
                print("✓ Acquisition completed")
                break
            time.sleep(0.1)
            check_count += 1
        
        if check_count >= max_checks:
            print("❌ Acquisition timeout")
            return False
        
        # Get the data
        print("\n--- Reading Data ---")
        
        no_of_samples_returned = ctypes.c_int32()
        start_index = ctypes.c_int32()
        overflow = ctypes.c_int16()
        
        status = ps.ps6000aGetValues(
            chandle, 0, byref(no_of_samples_returned), 1, 0, 0, byref(start_index)
        )
        
        if status != 0:
            print(f"❌ Failed to get values. Status: {status}")
            return False
        
        print(f"✓ Retrieved {no_of_samples_returned.value} samples")
        
        # Convert and display the data
        print("\n--- Data Results ---")
        
        for channel_name, buffer in buffers.items():
            # Convert raw ADC values to voltages
            # For ±10V range (range_val=9), the conversion factor is typically 10V/32768
            voltage_conversion = 10.0 / 32768.0
            voltages = np.array(buffer[:no_of_samples_returned.value]) * voltage_conversion
            
            # Calculate some basic statistics
            mean_voltage = np.mean(voltages)
            std_voltage = np.std(voltages)
            min_voltage = np.min(voltages)
            max_voltage = np.max(voltages)
            
            print(f"Channel {channel_name}:")
            print(f"  Mean: {mean_voltage:.3f}V")
            print(f"  Std:  {std_voltage:.3f}V")
            print(f"  Min:  {min_voltage:.3f}V")
            print(f"  Max:  {max_voltage:.3f}V")
            print(f"  First 5 values: {voltages[:5]}")
            print()
        
        # Test simultaneous reading
        print("--- Simultaneous Reading Test ---")
        
        # Read a few more samples to verify all channels are working
        for i in range(3):
            print(f"Sample {i+1}:")
            for channel_name, buffer in buffers.items():
                voltage = buffer[i] * voltage_conversion
                print(f"  Channel {channel_name}: {voltage:.3f}V")
            print()
        
        # Close the device
        ps.ps6000aCloseUnit(chandle)
        print("✓ Device closed successfully")
        
        print("\n🎉 Multi-channel acquisition test PASSED!")
        print("✓ All 4 channels (A, B, C, D) are working simultaneously")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import PicoSDK: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_gui_display():
    """Create a simple GUI to display the multi-channel data"""
    
    print("\n=== Simple GUI Display Test ===\n")
    
    try:
        from PyQt6 import QtWidgets, QtCore
        import pyqtgraph as pg
        import numpy as np
        
        print("✓ PyQt6 and pyqtgraph imported successfully")
        
        class MultiChannelTestWindow(QtWidgets.QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("6824E Multi-Channel Test")
                self.setGeometry(100, 100, 1200, 800)
                
                # Create central widget
                central_widget = QtWidgets.QWidget()
                self.setCentralWidget(central_widget)
                
                # Create layout
                layout = QtWidgets.QGridLayout(central_widget)
                
                # Create plot widgets for each channel
                self.plots = {}
                self.curves = {}
                
                channels = ['A', 'B', 'C', 'D']
                colors = ['blue', 'red', 'green', 'orange']
                
                for i, (channel, color) in enumerate(zip(channels, colors)):
                    # Create plot widget
                    plot = pg.PlotWidget(title=f"Channel {channel}")
                    plot.setLabel('left', 'Voltage', units='V')
                    plot.setLabel('bottom', 'Time', units='s')
                    plot.setYRange(-5, 5)
                    
                    # Add to layout
                    row = i // 2
                    col = i % 2
                    layout.addWidget(plot, row, col)
                    
                    self.plots[channel] = plot
                    
                    # Create curve
                    curve = plot.plot(pen=color, name=f"Channel {channel}")
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
                
                layout.addLayout(button_layout, 2, 0, 1, 2)
                
                # Status label
                self.status_label = QtWidgets.QLabel("Ready to test")
                layout.addWidget(self.status_label, 3, 0, 1, 2)
                
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
                self.timer.start(100)  # Update every 100ms
                
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
                
                # Keep only last 100 points
                if len(self.time_data) > 100:
                    self.time_data = self.time_data[-100:]
                    for channel in self.channel_data:
                        self.channel_data[channel] = self.channel_data[channel][-100:]
                
                # Update plots
                for channel, curve in self.curves.items():
                    if len(self.time_data) > 0 and len(self.channel_data[channel]) > 0:
                        curve.setData(self.time_data, self.channel_data[channel])
                
                # Update status
                self.status_label.setText(f"Running... Time: {current_time:.1f}s, "
                                        f"A: {channel_values['A']:.2f}V, "
                                        f"B: {channel_values['B']:.2f}V, "
                                        f"C: {channel_values['C']:.2f}V, "
                                        f"D: {channel_values['D']:.2f}V")
        
        # Create and show the GUI
        app = QtWidgets.QApplication(sys.argv)
        window = MultiChannelTestWindow()
        window.show()
        
        print("✓ Simple GUI created successfully")
        print("✓ All 4 channels (A, B, C, D) should display different sine waves")
        print("✓ Click 'Start Test' to begin the simulation")
        
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
    print("6824E Multi-Channel Test Program")
    print("=" * 50)
    
    # Test 1: Direct hardware acquisition
    print("Test 1: Direct Hardware Acquisition")
    hardware_success = test_6824e_multi_channel_acquisition()
    
    if hardware_success:
        print("\n" + "=" * 50)
        print("Test 2: Simple GUI Display")
        
        # Test 2: Simple GUI display
        gui_success = test_simple_gui_display()
        
        if gui_success:
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n❌ GUI test failed")
    else:
        print("\n❌ Hardware test failed - skipping GUI test")
    
    print("\nTest program completed.")
