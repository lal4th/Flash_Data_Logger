#!/usr/bin/env python3
"""
Simple test to verify 6824E connection works.

This is a minimal test to prove basic 6824E device connection.
"""

import sys
import os
import ctypes
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))


def test_simple_6824e():
    """Simple test of 6824E connection."""
    print("🔍 Simple 6824E Connection Test")
    print("=" * 30)
    
    # Find ps6000a.dll
    dll_path = Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Pico Technology" / "SDK" / "lib" / "ps6000a.dll"
    
    if not dll_path.exists():
        print(f"❌ ps6000a.dll not found at {dll_path}")
        return False
    
    print(f"✅ Found ps6000a.dll at: {dll_path}")
    
    try:
        # Load the DLL
        print("Loading ps6000a.dll...")
        ps6000a = ctypes.CDLL(str(dll_path))
        print("✅ DLL loaded successfully")
        
        # Try to open device
        print("Attempting to open 6824E device...")
        handle = ctypes.c_int16()
        status = ps6000a.ps6000aOpenUnit(ctypes.byref(handle), None)
        print(f"Status: {status}")
        
        if status == 0:
            print("✅ 6824E device opened successfully!")
            
            # Get device info
            try:
                buffer = ctypes.create_string_buffer(256)
                required_len = ctypes.c_int16()
                ps6000a.ps6000aGetUnitInfo(handle, buffer, ctypes.c_int16(len(buffer)), ctypes.byref(required_len), 3)
                model = buffer.value.decode(errors="ignore")
                print(f"✅ Device model: {model}")
            except Exception as e:
                print(f"⚠️  Could not get device info: {e}")
            
            # Close the device
            ps6000a.ps6000aCloseUnit(handle)
            print("✅ Device closed successfully")
            return True
        else:
            print(f"❌ 6824E device open failed with status: {status}")
            return False
            
    except Exception as e:
        print(f"❌ 6824E connection test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🔧 Simple 6824E Test")
    print("=" * 20)
    
    success = test_simple_6824e()
    
    if success:
        print("\n✅ SUCCESS: 6824E connection works!")
        print("Basic device connection is functional.")
    else:
        print("\n❌ FAILURE: 6824E connection failed")
        print("There is a fundamental issue with device access.")


if __name__ == "__main__":
    main()


