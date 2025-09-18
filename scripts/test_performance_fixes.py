#!/usr/bin/env python3
"""
Test script to verify the performance fixes for the Flash Data Logger.
This script tests the buffer management and plot rendering improvements.
"""

import sys
import os
import time
import threading
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6 import QtWidgets, QtCore
from app.ui.main_window import MainWindow, PlotPanel, PlotConfig
from app.core.streaming_controller import StreamingController
import numpy as np


class PerformanceTest:
    """Test class for performance validation."""
    
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_window = MainWindow()
        self.controller = self.main_window.controller
        
        # Test configuration
        self.test_duration = 30  # 30 seconds
        self.sample_rate = 100   # 100 Hz
        self.timeline = 60       # 60 seconds
        
        # Test results
        self.test_results = {
            'buffer_growth': False,
            'data_retention': False,
            'plot_artifacts': False,
            'performance_stable': False,
            'crash_detected': False
        }
        
    def setup_test_environment(self):
        """Setup the test environment with test plots."""
        print("Setting up test environment...")
        
        # Configure controller
        self.controller.set_sample_rate(self.sample_rate)
        self.controller.set_timeline(self.timeline)
        
        # Add test plots
        config_a = PlotConfig(
            channel='A',
            coupling=1,
            voltage_range=8,
            y_min=-10.0,
            y_max=10.0,
            y_label='Volts',
            title='Channel A Test',
            color=QtWidgets.QApplication.palette().color(QtWidgets.QApplication.palette().ColorRole.Text)
        )
        
        config_b = PlotConfig(
            channel='B',
            coupling=1,
            voltage_range=8,
            y_min=-10.0,
            y_max=10.0,
            y_label='Volts',
            title='Channel B Test',
            color=QtWidgets.QApplication.palette().color(QtWidgets.QApplication.palette().ColorRole.Text)
        )
        
        # Add plots to the main window
        self.main_window._add_plot_to_grid(config_a)
        self.main_window._add_plot_to_grid(config_b)
        
        print(f"Added {len(self.main_window._plot_panels)} test plots")
        
    def generate_test_data(self, duration_seconds):
        """Generate test data for the specified duration."""
        print(f"Generating test data for {duration_seconds} seconds...")
        
        start_time = time.time()
        sample_count = 0
        
        while time.time() - start_time < duration_seconds:
            current_time = time.time() - start_time
            
            # Generate sine wave test data
            import math
            channel_a_value = 5.0 * math.sin(2 * math.pi * current_time * 0.5)  # 0.5 Hz sine wave
            channel_b_value = 3.0 * math.cos(2 * math.pi * current_time * 0.3)  # 0.3 Hz cosine wave
            
            # Update plots with test data
            for row, col, panel in self.main_window._plot_panels:
                if panel.channel == 'A':
                    panel.update_data(current_time, channel_a_value)
                elif panel.channel == 'B':
                    panel.update_data(current_time, channel_b_value)
            
            sample_count += 1
            
            # Process Qt events to keep UI responsive
            self.app.processEvents()
            
            # Small delay to simulate real data acquisition
            time.sleep(1.0 / self.sample_rate)
        
        print(f"Generated {sample_count} samples")
        return sample_count
    
    def test_buffer_management(self):
        """Test buffer management and memory usage."""
        print("\n=== Testing Buffer Management ===")
        
        # Get initial buffer sizes
        initial_sizes = []
        for row, col, panel in self.main_window._plot_panels:
            initial_sizes.append(len(panel._time_buffer))
        
        # Generate test data
        sample_count = self.generate_test_data(10)  # 10 seconds of data
        
        # Check buffer sizes after data generation
        final_sizes = []
        for row, col, panel in self.main_window._plot_panels:
            final_sizes.append(len(panel._time_buffer))
        
        # Verify buffers are not growing excessively
        max_expected_size = self.timeline * self.sample_rate * 2.0  # 2x timeline for buffer
        max_expected_size = max(10000, min(max_expected_size, 500000))  # Apply limits
        
        buffer_ok = True
        for i, (initial, final) in enumerate(zip(initial_sizes, final_sizes)):
            if final > max_expected_size * 1.5:  # Allow 50% over limit
                print(f"❌ Buffer {i} too large: {final} > {max_expected_size * 1.5}")
                buffer_ok = False
            else:
                print(f"✓ Buffer {i} size OK: {final} <= {max_expected_size * 1.5}")
        
        self.test_results['buffer_growth'] = buffer_ok
        return buffer_ok
    
    def test_data_retention(self):
        """Test data retention throughout the session."""
        print("\n=== Testing Data Retention ===")
        
        # Clear all plots first
        for row, col, panel in self.main_window._plot_panels:
            panel.clear()
        
        # Generate data for 15 seconds
        self.generate_test_data(15)
        
        # Check that data from the beginning is still there
        retention_ok = True
        for row, col, panel in self.main_window._plot_panels:
            if len(panel._time_buffer) > 0:
                first_time = panel._time_buffer[0]
                if first_time > 5.0:  # If first time is > 5 seconds, data was lost
                    print(f"❌ Data retention failed for {panel.channel}: first time = {first_time}")
                    retention_ok = False
                else:
                    print(f"✓ Data retention OK for {panel.channel}: first time = {first_time}")
            else:
                print(f"❌ No data in {panel.channel} buffer")
                retention_ok = False
        
        self.test_results['data_retention'] = retention_ok
        return retention_ok
    
    def test_plot_artifacts(self):
        """Test for plot rendering artifacts."""
        print("\n=== Testing Plot Artifacts ===")
        
        # Clear all plots
        for row, col, panel in self.main_window._plot_panels:
            panel.clear()
        
        # Generate a small amount of data
        self.generate_test_data(2)
        
        # Check for (0,0) line artifacts by examining the data
        artifacts_ok = True
        for row, col, panel in self.main_window._plot_panels:
            if len(panel._time_buffer) > 0 and len(panel._data_buffer) > 0:
                # Check if there's a (0,0) point at the beginning
                if panel._time_buffer[0] == 0.0 and panel._data_buffer[0] == 0.0:
                    # This might be OK if it's the first real data point
                    if len(panel._time_buffer) > 1:
                        # Check if there's a line from (0,0) to the first real data
                        if panel._time_buffer[1] > 0.1:  # If there's a gap, it's an artifact
                            print(f"❌ (0,0) line artifact detected in {panel.channel}")
                            artifacts_ok = False
                        else:
                            print(f"✓ No (0,0) line artifact in {panel.channel}")
                    else:
                        print(f"✓ Single data point in {panel.channel} (no artifact)")
                else:
                    print(f"✓ No (0,0) point in {panel.channel}")
            else:
                print(f"❌ No data in {panel.channel} buffer")
                artifacts_ok = False
        
        self.test_results['plot_artifacts'] = artifacts_ok
        return artifacts_ok
    
    def test_performance_stability(self):
        """Test performance stability over extended period."""
        print("\n=== Testing Performance Stability ===")
        
        # Clear all plots
        for row, col, panel in self.main_window._plot_panels:
            panel.clear()
        
        # Generate data for extended period
        start_time = time.time()
        sample_count = self.generate_test_data(self.test_duration)
        end_time = time.time()
        
        # Calculate performance metrics
        actual_duration = end_time - start_time
        expected_duration = self.test_duration
        performance_ratio = actual_duration / expected_duration
        
        print(f"Expected duration: {expected_duration:.1f}s")
        print(f"Actual duration: {actual_duration:.1f}s")
        print(f"Performance ratio: {performance_ratio:.2f}")
        print(f"Samples generated: {sample_count}")
        
        # Performance is OK if we're within 20% of expected time
        performance_ok = 0.8 <= performance_ratio <= 1.2
        
        if performance_ok:
            print("✓ Performance stability OK")
        else:
            print("❌ Performance stability issues detected")
        
        self.test_results['performance_stable'] = performance_ok
        return performance_ok
    
    def run_all_tests(self):
        """Run all performance tests."""
        print("Starting Flash Data Logger Performance Tests")
        print("=" * 50)
        
        try:
            # Setup test environment
            self.setup_test_environment()
            
            # Run tests
            self.test_buffer_management()
            self.test_data_retention()
            self.test_plot_artifacts()
            self.test_performance_stability()
            
            # Print results
            print("\n" + "=" * 50)
            print("TEST RESULTS SUMMARY")
            print("=" * 50)
            
            all_passed = True
            for test_name, result in self.test_results.items():
                if test_name == 'crash_detected':
                    # For crash detection, False (no crash) is good
                    status = "✓ PASS" if not result else "❌ FAIL"
                else:
                    status = "✓ PASS" if result else "❌ FAIL"
                print(f"{test_name.replace('_', ' ').title()}: {status}")
                if test_name == 'crash_detected':
                    if result:  # Crash detected is bad
                        all_passed = False
                else:
                    if not result:  # Other failures are bad
                        all_passed = False
            
            print("=" * 50)
            if all_passed:
                print("🎉 ALL TESTS PASSED - Performance fixes are working!")
            else:
                print("⚠️  SOME TESTS FAILED - Performance issues remain")
            
            return all_passed
            
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results['crash_detected'] = True
            return False


def main():
    """Main test function."""
    print("Flash Data Logger Performance Test")
    print("Testing buffer management and plot rendering fixes")
    print()
    
    # Create and run tests
    test = PerformanceTest()
    success = test.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
