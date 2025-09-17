#!/usr/bin/env python3
"""
Simple test to verify 4262 connection works.

This is a minimal test to prove basic device connection.
"""

import sys
import os
import ctypes
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))


def test_simple_4262():
    """Simple test of 4262 connection."""
    print("🔍 Simple 4262 Connection Test")
    print("=" * 30)
    
    # Find ps4000.dll
    dll_path = Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Pico Technology" / "SDK" / "lib" / "ps4000.dll"
    
    if not dll_path.exists():
        print(f"❌ ps4000.dll not found at {dll_path}")
        return False
    
    print(f"✅ Found ps4000.dll at: {dll_path}")
    
    try:
        # Load the DLL
        print("Loading ps4000.dll...")
        ps4000 = ctypes.CDLL(str(dll_path))
        print("✅ DLL loaded successfully")
        
        # Try to open device
        print("Attempting to open 4262 device...")
        handle = ctypes.c_int16()
        status = ps4000.ps4000OpenUnit(ctypes.byref(handle))
        print(f"Status: {status}")
        
        if status == 0:
            print("✅ 4262 device opened successfully!")
            
            # Get device info
            try:
                buffer = ctypes.create_string_buffer(256)
                required_len = ctypes.c_int16()
                ps4000.ps4000GetUnitInfo(handle, buffer, ctypes.c_int16(len(buffer)), ctypes.byref(required_len), 3)
                model = buffer.value.decode(errors="ignore")
                print(f"✅ Device model: {model}")
            except Exception as e:
                print(f"⚠️  Could not get device info: {e}")
            
            # Close the device
            ps4000.ps4000CloseUnit(handle)
            print("✅ Device closed successfully")
            return True
        else:
            print(f"❌ 4262 device open failed with status: {status}")
            return False
            
    except Exception as e:
        print(f"❌ 4262 connection test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🔧 Simple 4262 Test")
    print("=" * 20)
    
    success = test_simple_4262()
    
    if success:
        print("\n✅ SUCCESS: 4262 connection works!")
        print("Basic device connection is functional.")
    else:
        print("\n❌ FAILURE: 4262 connection failed")
        print("There is a fundamental issue with device access.")


if __name__ == "__main__":
    main()


