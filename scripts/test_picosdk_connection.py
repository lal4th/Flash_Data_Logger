#!/usr/bin/env python3
"""
Simple PicoScope Connection Test Script
Based on PicoSDK Python Wrappers

This script tests connection to any supported PicoScope device,
with specific focus on the 6824E (6000 series).

Usage: python test_picosdk_connection.py
"""

import sys
import traceback
from typing import List, Dict, Any

def test_picosdk_discovery():
    """Test device discovery using picosdk.discover"""
    print("=== Testing PicoSDK Device Discovery ===")
    
    try:
        from picosdk.discover import find_all_units
        print("✓ picosdk.discover imported successfully")
        
        print("Searching for connected PicoScope devices...")
        scopes = find_all_units()
        
        if not scopes:
            print("❌ No PicoScope devices found")
            return False
            
        print(f"✓ Found {len(scopes)} PicoScope device(s):")
        
        for i, scope in enumerate(scopes):
            print(f"  Device {i+1}:")
            print(f"    Info: {scope.info}")
            print(f"    Driver: {scope.driver}")
            print(f"    Handle: {scope.handle}")
            
            # Test basic operations
            try:
                # Get unit info
                info = scope.get_unit_info()
                print(f"    Unit Info: {info}")
                
                # Close the device
                scope.close()
                print(f"    ✓ Device closed successfully")
                
            except Exception as e:
                print(f"    ❌ Error with device operations: {e}")
                
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import picosdk.discover: {e}")
        return False
    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        traceback.print_exc()
        return False


def test_ps6000a_direct():
    """Test direct ps6000a connection (for 6824E)"""
    print("\n=== Testing Direct ps6000a Connection (6824E) ===")
    
    try:
        from picosdk.ps6000a import ps6000a as ps
        from picosdk.functions import assert_pico_ok
        import ctypes
        
        print("✓ ps6000a imported successfully")
        
        # Create handle
        chandle = ctypes.c_int16()
        status = {}
        
        # Open unit
        print("Attempting to open 6000 series PicoScope...")
        status["openunit"] = ps.ps6000aOpenUnit(ctypes.byref(chandle), None, 1)
        
        if status["openunit"] == 0:
            print("✓ Successfully opened 6000 series PicoScope")
            
            # Get unit info
            try:
                buffer = ctypes.create_string_buffer(256)
                required_len = ctypes.c_int16()
                ps.ps6000aGetUnitInfo(chandle, ctypes.byref(buffer), 
                                    ctypes.c_int16(len(buffer)), 
                                    ctypes.byref(required_len), 3)
                model = buffer.value.decode(errors="ignore")
                print(f"✓ Device Model: {model}")
            except Exception as e:
                print(f"⚠ Could not get unit info: {e}")
            
            # Test channel setup
            try:
                channel = ps.PS6000A_CHANNEL['PS6000A_CHANNEL_A']
                coupling = ps.PS6000A_COUPLING['PS6000A_DC']
                range_val = ps.PS6000A_RANGE['PS6000A_5V']
                status["setChannel"] = ps.ps6000aSetChannel(chandle, channel, 1, coupling, range_val, 0, 0)
                
                if status["setChannel"] == 0:
                    print("✓ Channel A configured successfully")
                else:
                    print(f"⚠ Channel configuration returned status: {status['setChannel']}")
                    
            except Exception as e:
                print(f"⚠ Channel setup failed: {e}")
            
            # Close unit
            status["close"] = ps.ps6000aCloseUnit(chandle)
            if status["close"] == 0:
                print("✓ Device closed successfully")
            else:
                print(f"⚠ Close returned status: {status['close']}")
                
            return True
            
        else:
            print(f"❌ Failed to open 6000 series PicoScope. Status: {status['openunit']}")
            
            # Common status codes
            status_codes = {
                3: "PICO_NOT_FOUND - Device not found or PicoScope app running",
                4: "PICO_INVALID_PARAMETER", 
                5: "PICO_INVALID_HANDLE - Device already open",
                288: "PICO_DEVICE_TIME_STAMP_RESET - Device timestamp reset",
                268435457: "DLL dependency issue"
            }
            
            error_desc = status_codes.get(status["openunit"], f"Unknown status {status['openunit']}")
            print(f"   Error: {error_desc}")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import ps6000a: {e}")
        return False
    except Exception as e:
        print(f"❌ ps6000a test failed: {e}")
        traceback.print_exc()
        return False


def test_ps4000_direct():
    """Test direct ps4000 connection (for 4262)"""
    print("\n=== Testing Direct ps4000 Connection (4262) ===")
    
    try:
        from picosdk.ps4000 import ps4000 as ps
        from picosdk.functions import assert_pico_ok
        import ctypes
        
        print("✓ ps4000 imported successfully")
        
        # Create handle
        chandle = ctypes.c_int16()
        
        # Open unit
        print("Attempting to open 4000 series PicoScope...")
        status = ps.ps4000OpenUnit(ctypes.byref(chandle))
        
        if status == 0:
            print("✓ Successfully opened 4000 series PicoScope")
            
            # Get unit info
            try:
                buffer = ctypes.create_string_buffer(256)
                required_len = ctypes.c_int16()
                ps.ps4000GetUnitInfo(chandle, ctypes.byref(buffer), 
                                   ctypes.c_int16(len(buffer)), 
                                   ctypes.byref(required_len), 3)
                model = buffer.value.decode(errors="ignore")
                print(f"✓ Device Model: {model}")
            except Exception as e:
                print(f"⚠ Could not get unit info: {e}")
            
            # Close unit
            close_status = ps.ps4000CloseUnit(chandle)
            if close_status == 0:
                print("✓ Device closed successfully")
            else:
                print(f"⚠ Close returned status: {close_status}")
                
            return True
            
        else:
            print(f"❌ Failed to open 4000 series PicoScope. Status: {status}")
            
            # Common status codes
            status_codes = {
                3: "PICO_NOT_FOUND - Device not found or PicoScope app running",
                4: "PICO_INVALID_PARAMETER",
                5: "PICO_INVALID_HANDLE - Device already open",
                268435457: "DLL dependency issue"
            }
            
            error_desc = status_codes.get(status, f"Unknown status {status}")
            print(f"   Error: {error_desc}")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import ps4000: {e}")
        return False
    except Exception as e:
        print(f"❌ ps4000 test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("PicoScope Connection Test Script")
    print("=" * 50)
    print("Testing connection to any supported PicoScope device")
    print("Focus: 6824E (6000 series) and 4262 (4000 series)")
    print()
    
    # Test results
    results = {
        "discovery": False,
        "ps6000a": False, 
        "ps4000": False
    }
    
    # Run tests
    results["discovery"] = test_picosdk_discovery()
    results["ps6000a"] = test_ps6000a_direct()
    results["ps4000"] = test_ps4000_direct()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{test_name.upper()}: {status}")
    
    # Overall result
    any_success = any(results.values())
    if any_success:
        print("\n🎉 At least one connection method succeeded!")
        print("   Your PicoScope device is working with PicoSDK Python wrappers.")
    else:
        print("\n💥 All connection tests failed.")
        print("   Please check:")
        print("   - PicoScope is connected via USB")
        print("   - PicoScope software is closed")
        print("   - PicoSDK is properly installed")
        print("   - Try running as Administrator")
    
    return 0 if any_success else 1


if __name__ == "__main__":
    sys.exit(main())
