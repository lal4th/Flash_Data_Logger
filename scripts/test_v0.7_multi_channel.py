#!/usr/bin/env python3
"""
Test script for v0.7 multi-channel foundation.
This script tests the multi-channel acquisition and CSV writing functionality.
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.acquisition.pico_direct import PicoDirectSource, test_device_connection
from app.storage.csv_writer import CsvWriter
from app.core.streaming_controller import StreamingController
import time

def test_device_connection_wrapper():
    """Test if PicoScope device is available."""
    print("Testing PicoScope device connection...")
    success, message = test_device_connection()
    print(f"Device connection: {message}")
    return success

def test_multi_channel_csv_writer():
    """Test multi-channel CSV writer functionality."""
    print("\nTesting multi-channel CSV writer...")
    
    # Create test CSV file
    test_csv_path = Path("test_multi_channel.csv")
    
    # Channel configuration
    channel_config = {
        'channel_a': {
            'enabled': True,
            'coupling': 1,
            'range': 8,  # ±5V
            'offset': 0.0
        },
        'channel_b': {
            'enabled': True,
            'coupling': 1,
            'range': 8,  # ±5V
            'offset': 0.0
        }
    }
    
    # Create CSV writer
    csv_writer = CsvWriter(test_csv_path, multi_channel_mode=True, channel_config=channel_config)
    csv_writer.open()
    
    # Write test data
    test_data = [
        (0.000, 1.234, 2.345),
        (0.001, 1.235, 2.346),
        (0.002, 1.236, 2.347),
        (0.003, 1.237, 2.348),
        (0.004, 1.238, 2.349),
    ]
    
    for timestamp, ch_a, ch_b in test_data:
        csv_writer.write_multi_channel_row(timestamp, ch_a, ch_b)
    
    csv_writer.close()
    
    # Verify file was created
    if test_csv_path.exists():
        print(f"✓ Multi-channel CSV file created: {test_csv_path}")
        print("File contents:")
        with open(test_csv_path, 'r') as f:
            print(f.read())
        
        # Clean up
        test_csv_path.unlink()
        print("✓ Test file cleaned up")
        return True
    else:
        print("✗ Multi-channel CSV file was not created")
        return False

def test_pico_direct_multi_channel():
    """Test PicoDirectSource multi-channel configuration."""
    print("\nTesting PicoDirectSource multi-channel configuration...")
    
    try:
        # Create PicoDirectSource
        source = PicoDirectSource()
        
        # Test multi-channel configuration
        source.configure_multi_channel(
            sample_rate_hz=100,
            channel_a_enabled=True,
            channel_a_coupling=1,
            channel_a_range=8,  # ±5V
            channel_a_offset=0.0,
            channel_b_enabled=True,
            channel_b_coupling=1,
            channel_b_range=8,  # ±5V
            channel_b_offset=0.0
        )
        
        print("✓ Multi-channel configuration successful")
        
        # Test channel configuration methods
        config_a = source.get_channel_config(0)
        config_b = source.get_channel_config(1)
        
        print(f"✓ Channel A config: {config_a}")
        print(f"✓ Channel B config: {config_b}")
        
        # Test mode detection
        is_multi = source.is_multi_channel_mode()
        print(f"✓ Multi-channel mode: {is_multi}")
        
        return True
        
    except Exception as e:
        print(f"✗ Multi-channel configuration failed: {e}")
        return False

def test_streaming_controller_multi_channel():
    """Test StreamingController multi-channel configuration."""
    print("\nTesting StreamingController multi-channel configuration...")
    
    try:
        # Create StreamingController
        controller = StreamingController()
        
        # Test multi-channel configuration
        controller.set_multi_channel_mode(True)
        controller.set_channel_a_config(True, 1, 8, 0.0)  # enabled, DC, ±5V, no offset
        controller.set_channel_b_config(True, 1, 8, 0.0)  # enabled, DC, ±5V, no offset
        
        # Get configuration
        config = controller.get_multi_channel_config()
        print(f"✓ Multi-channel config: {config}")
        
        return True
        
    except Exception as e:
        print(f"✗ StreamingController multi-channel configuration failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Flash Data Logger v0.7 - Multi-Channel Foundation Test")
    print("=" * 60)
    
    tests = [
        ("Device Connection", test_device_connection_wrapper),
        ("Multi-Channel CSV Writer", test_multi_channel_csv_writer),
        ("PicoDirectSource Multi-Channel", test_pico_direct_multi_channel),
        ("StreamingController Multi-Channel", test_streaming_controller_multi_channel),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:30} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Multi-channel foundation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
