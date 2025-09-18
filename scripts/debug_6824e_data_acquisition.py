#!/usr/bin/env python3
"""
Debug script to test actual data acquisition from 6824E.
This will help us understand why the main application disconnects instead of acquiring data.
"""

import sys
import os
import time
import threading

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_6824e_data_acquisition():
    """Test the actual data acquisition from 6824E using our existing code"""
    
    print("=== 6824E Data Acquisition Debug Test ===\n")
    
    try:
        from app.acquisition.pico_6000_direct import Pico6000DirectSource
        from app.core.streaming_controller import StreamingController, StreamingConfig
        
        print("✓ Imported required modules successfully")
        
        # Test 1: Direct source connection and configuration
        print("\n--- Test 1: Direct Source Connection ---")
        
        source = Pico6000DirectSource()
        
        if not source.connect():
            print("❌ Failed to connect to 6824E")
            return False
        
        print("✓ Connected to 6824E successfully")
        
        # Configure multi-channel
        print("\n--- Test 2: Multi-Channel Configuration ---")
        
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
        
        # Test 3: Data reading
        print("\n--- Test 3: Data Reading ---")
        
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
                print()
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Failed to read data: {e}")
                return False
        
        # Disconnect
        source.disconnect()
        print("✓ Disconnected successfully")
        
        # Test 4: Streaming Controller Integration
        print("\n--- Test 4: Streaming Controller Integration ---")
        
        controller = StreamingController()
        
        # Create config with all channels enabled
        config = StreamingConfig()
        config.multi_channel_mode = True
        config.channel_c_enabled = True
        config.channel_d_enabled = True
        config.channel_e_enabled = True
        config.channel_f_enabled = True
        config.channel_g_enabled = True
        config.channel_h_enabled = True
        
        controller._config = config
        
        # Set up the 6824E source
        controller._pico_6000_source = Pico6000DirectSource()
        
        if not controller._pico_6000_source.connect():
            print("❌ Failed to connect 6824E to controller")
            return False
        
        print("✓ Connected 6824E to controller")
        
        # Test the _setup_data_source method
        print("\n--- Test 5: Controller Data Source Setup ---")
        
        try:
            result = controller._setup_data_source()
            print(f"✓ _setup_data_source() returned: {result}")
        except Exception as e:
            print(f"❌ _setup_data_source() failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test data acquisition loop
        print("\n--- Test 6: Data Acquisition Loop ---")
        
        try:
            # Simulate the acquisition loop
            for i in range(3):
                block_data = controller._acquire_block()
                print(f"Block {i+1}: {len(block_data)} samples")
                
                if block_data:
                    # Check the data format
                    sample = block_data[0]
                    print(f"  Sample format: {len(sample)} elements")
                    print(f"  First sample: {sample}")
                
                time.sleep(0.1)
            
            print("✓ Data acquisition loop working")
            
        except Exception as e:
            print(f"❌ Data acquisition loop failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Cleanup
        controller._pico_6000_source.disconnect()
        print("✓ Cleanup completed")
        
        print("\n🎉 All tests PASSED!")
        print("✓ 6824E data acquisition is working correctly")
        print("✓ The issue must be in the GUI start/stop logic")
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("6824E Data Acquisition Debug Test")
    print("=" * 50)
    
    success = test_6824e_data_acquisition()
    
    if success:
        print("\n🎉 Data acquisition is working correctly!")
        print("The issue is likely in the GUI start/stop logic.")
        print("The application is disconnecting instead of starting acquisition.")
    else:
        print("\n❌ Data acquisition test failed")
    
    print("\nTest completed.")
