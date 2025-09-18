#!/usr/bin/env python3
"""
Debug script to isolate plotting performance issues.
This script feeds fake multi-channel data to the plotting system
and monitors buffer growth, memory usage, and performance.
"""

import sys
import os
import time
import threading
import psutil
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6 import QtWidgets, QtCore
from app.ui.main_window import MainWindow, PlotPanel, PlotConfig
import numpy as np
import math


class PlottingDebugger:
    """Debug class to isolate plotting performance issues."""
    
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = MainWindow()
        
        # Test configuration
        self.test_duration = 20  # 20 seconds
        self.sample_rate = 100   # 100 Hz
        self.timeline = 60       # 60 seconds
        
        # Debug monitoring
        self.debug_data = {
            'buffer_sizes': [],
            'memory_usage': [],
            'plot_update_times': [],
            'data_points': [],
            'timestamps': []
        }
        
        # Performance monitoring
        self.start_time = None
        self.sample_count = 0
        
    def setup_debug_environment(self):
        """Setup debug environment with monitoring plots."""
        print("Setting up debug environment...")
        
        # Configure main window
        self.main_window.spinbox_timeline.setValue(self.timeline)
        self.main_window.combo_samplerate.setCurrentIndex(2)  # 100 Hz
        
        # Add debug plots for channels A, B, C, D
        channels = ['A', 'B', 'C', 'D']
        colors = [
            QtWidgets.QApplication.palette().color(QtWidgets.QApplication.palette().ColorRole.Text),  # Default
            QtWidgets.QApplication.palette().color(QtWidgets.QApplication.palette().ColorRole.Text),  # Default
            QtWidgets.QApplication.palette().color(QtWidgets.QApplication.palette().ColorRole.Text),  # Default
            QtWidgets.QApplication.palette().color(QtWidgets.QApplication.palette().ColorRole.Text),  # Default
        ]
        
        for i, (channel, color) in enumerate(zip(channels, colors)):
            config = PlotConfig(
                channel=channel,
                coupling=1,
                voltage_range=8,
                y_min=-5.0,
                y_max=5.0,
                y_label='Volts',
                title=f'Channel {channel} Debug',
                color=color
            )
            
            # Add plot to the main window
            self.main_window._add_plot_to_grid(config)
            print(f"Added Channel {channel} debug plot")
        
        print(f"Total plots: {len(self.main_window._plot_panels)}")
        
    def monitor_system_resources(self):
        """Monitor system resources during the test."""
        process = psutil.Process()
        
        while self.start_time and time.time() - self.start_time < self.test_duration:
            current_time = time.time() - self.start_time
            
            # Get memory usage
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # Get buffer sizes
            buffer_sizes = []
            for row, col, panel in self.main_window._plot_panels:
                buffer_sizes.append(len(panel._time_buffer))
            
            # Store debug data
            self.debug_data['timestamps'].append(current_time)
            self.debug_data['memory_usage'].append(memory_mb)
            self.debug_data['buffer_sizes'].append(buffer_sizes.copy())
            self.debug_data['data_points'].append(self.sample_count)
            
            # Print debug info every 2 seconds
            if int(current_time) % 2 == 0 and current_time > 0:
                print(f"Time: {current_time:.1f}s | Memory: {memory_mb:.1f}MB | Buffers: {buffer_sizes} | Samples: {self.sample_count}")
            
            time.sleep(0.5)  # Monitor every 500ms
    
    def generate_debug_data(self):
        """Generate fake multi-channel data and monitor performance."""
        print(f"Generating debug data for {self.test_duration} seconds...")
        
        self.start_time = time.time()
        self.sample_count = 0
        
        # Start resource monitoring in background
        monitor_thread = threading.Thread(target=self.monitor_system_resources, daemon=True)
        monitor_thread.start()
        
        try:
            while time.time() - self.start_time < self.test_duration:
                current_time = time.time() - self.start_time
                
                # Generate different sine waves for each channel
                channel_data = {}
                channel_data['A'] = 3.0 * math.sin(2 * math.pi * current_time * 0.5)  # 0.5 Hz
                channel_data['B'] = 2.5 * math.cos(2 * math.pi * current_time * 0.3)  # 0.3 Hz
                channel_data['C'] = 2.0 * math.sin(2 * math.pi * current_time * 0.7)  # 0.7 Hz
                channel_data['D'] = 1.5 * math.cos(2 * math.pi * current_time * 0.4)  # 0.4 Hz
                
                # Update each plot
                plot_update_start = time.time()
                for row, col, panel in self.main_window._plot_panels:
                    if panel.channel in channel_data:
                        panel.update_data(current_time, channel_data[panel.channel])
                
                plot_update_time = time.time() - plot_update_start
                self.debug_data['plot_update_times'].append(plot_update_time)
                
                self.sample_count += 1
                
                # Process Qt events to keep UI responsive
                self.app.processEvents()
                
                # Small delay to simulate real data acquisition
                time.sleep(1.0 / self.sample_rate)
                
        except Exception as e:
            print(f"❌ Error during data generation: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"Generated {self.sample_count} samples")
        
    def analyze_debug_data(self):
        """Analyze the collected debug data."""
        print("\n" + "=" * 60)
        print("DEBUG DATA ANALYSIS")
        print("=" * 60)
        
        if not self.debug_data['timestamps']:
            print("❌ No debug data collected")
            return
        
        # Memory usage analysis
        memory_data = self.debug_data['memory_usage']
        if memory_data:
            initial_memory = memory_data[0]
            final_memory = memory_data[-1]
            max_memory = max(memory_data)
            memory_growth = final_memory - initial_memory
            
            print(f"Memory Usage:")
            print(f"  Initial: {initial_memory:.1f} MB")
            print(f"  Final: {final_memory:.1f} MB")
            print(f"  Max: {max_memory:.1f} MB")
            print(f"  Growth: {memory_growth:.1f} MB")
            
            if memory_growth > 50:  # More than 50MB growth
                print("  ❌ EXCESSIVE MEMORY GROWTH DETECTED")
            else:
                print("  ✓ Memory growth within acceptable limits")
        
        # Buffer size analysis
        buffer_data = self.debug_data['buffer_sizes']
        if buffer_data:
            print(f"\nBuffer Size Analysis:")
            for i, (row, col, panel) in enumerate(self.main_window._plot_panels):
                if i < len(buffer_data[0]):
                    initial_size = buffer_data[0][i]
                    final_size = buffer_data[-1][i]
                    max_size = max([buf[i] for buf in buffer_data])
                    
                    print(f"  Channel {panel.channel}:")
                    print(f"    Initial: {initial_size} points")
                    print(f"    Final: {final_size} points")
                    print(f"    Max: {max_size} points")
                    
                    if max_size > 100000:  # More than 100k points
                        print(f"    ❌ BUFFER TOO LARGE")
                    else:
                        print(f"    ✓ Buffer size acceptable")
        
        # Plot update performance analysis
        update_times = self.debug_data['plot_update_times']
        if update_times:
            avg_update_time = sum(update_times) / len(update_times)
            max_update_time = max(update_times)
            
            print(f"\nPlot Update Performance:")
            print(f"  Average update time: {avg_update_time*1000:.2f} ms")
            print(f"  Max update time: {max_update_time*1000:.2f} ms")
            
            if avg_update_time > 0.01:  # More than 10ms average
                print("  ❌ PLOT UPDATES TOO SLOW")
            else:
                print("  ✓ Plot update performance acceptable")
        
        # Data retention analysis
        print(f"\nData Retention Analysis:")
        for row, col, panel in self.main_window._plot_panels:
            if panel._time_buffer:
                first_time = panel._time_buffer[0]
                last_time = panel._time_buffer[-1]
                data_span = last_time - first_time
                
                print(f"  Channel {panel.channel}:")
                print(f"    First data point: {first_time:.3f} s")
                print(f"    Last data point: {last_time:.3f} s")
                print(f"    Data span: {data_span:.3f} s")
                
                if first_time > 1.0:  # Data starts after 1 second
                    print(f"    ❌ DATA LOSS DETECTED - missing {first_time:.3f} seconds")
                else:
                    print(f"    ✓ Data retention OK")
            else:
                print(f"  Channel {panel.channel}: ❌ NO DATA")
    
    def run_debug_test(self):
        """Run the complete debug test."""
        print("Flash Data Logger Plotting Performance Debug")
        print("=" * 60)
        
        try:
            # Setup debug environment
            self.setup_debug_environment()
            
            # Generate debug data
            self.generate_debug_data()
            
            # Analyze results
            self.analyze_debug_data()
            
            print("\n" + "=" * 60)
            print("DEBUG TEST COMPLETE")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Debug test failed: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main debug function."""
    print("Starting plotting performance debug...")
    
    # Create and run debug test
    debugger = PlottingDebugger()
    debugger.run_debug_test()
    
    # Keep the app running so we can see the final state
    print("\nPress Ctrl+C to exit...")
    try:
        debugger.app.exec()
    except KeyboardInterrupt:
        print("\nDebug test terminated by user")


if __name__ == "__main__":
    main()
