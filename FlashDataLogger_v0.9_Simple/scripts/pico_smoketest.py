#!/usr/bin/env python3
"""
PicoScope 4262 Smoke Test - Phase 0
Tests basic ps4000.dll connectivity and block mode acquisition.

Usage: python scripts/pico_smoketest.py
"""

import ctypes
import os
import sys
import time
from pathlib import Path


def find_ps4000_dll():
    """
    Locate ps4000.dll by scanning common PicoSDK installation paths.
    Returns the full path to the DLL or None if not found.
    """
    # Common PicoSDK installation paths
    search_paths = [
        r"C:\Program Files\Pico Technology",
        r"C:\Program Files (x86)\Pico Technology",
    ]
    
    dll_name = "ps4000.dll"
    
    for base_path in search_paths:
        if os.path.exists(base_path):
            print(f"Scanning {base_path} for {dll_name}...")
            
            # Recursively search for ps4000.dll
            for root, dirs, files in os.walk(base_path):
                if dll_name in files:
                    dll_path = os.path.join(root, dll_name)
                    print(f"Found {dll_name} at: {dll_path}")
                    return dll_path
    
    print(f"ERROR: {dll_name} not found in any of the search paths:")
    for path in search_paths:
        print(f"  - {path}")
    return None


def test_pico_connectivity():
    """
    Test basic PicoScope 4262 connectivity using ps4000 API.
    """
    print("=== PicoScope 4262 Smoke Test ===")
    
    # Step 1: Find the DLL
    dll_path = find_ps4000_dll()
    if not dll_path:
        return False
    
    try:
        # Step 2: Add DLL directory to PATH and load the DLL
        dll_dir = os.path.dirname(dll_path)
        print(f"\nAdding DLL directory to PATH: {dll_dir}")
        
        # Add DLL directory to PATH for dependency resolution
        old_path = os.environ.get('PATH', '')
        os.environ['PATH'] = dll_dir + os.pathsep + old_path
        
        # Also try adding to DLL directory for Windows DLL search
        if hasattr(os, 'add_dll_directory'):
            print(f"Adding DLL directory for Windows search: {dll_dir}")
            os.add_dll_directory(dll_dir)
        
        print(f"Loading DLL: {dll_path}")
        try:
            ps4000 = ctypes.CDLL(dll_path)
        except OSError as e:
            print(f"ERROR: Failed to load DLL: {e}")
            print("This might be due to:")
            print("1. Missing dependencies (picoipp.dll, etc.)")
            print("2. Architecture mismatch (32-bit vs 64-bit)")
            print("3. PicoScope desktop app still running")
            print("4. Device permissions or driver issues")
            return False
        
        # Step 3: Open the device
        print("Opening PicoScope unit...")
        handle = ctypes.c_int16()
        status = ps4000.ps4000OpenUnit(ctypes.byref(handle))
        
        if status != 0:  # PICO_OK = 0
            print(f"ERROR: ps4000OpenUnit failed with status code: {status}")
            print(f"Common codes: PICO_NOT_FOUND=3, PICO_USB_3_0_DEVICE_NON_USB_3_0_PORT=23")
            return False
        
        print(f"Device opened successfully! Handle: {handle.value}")
        
        # Step 4: Configure Channel A (DC coupling, ±5V range)
        print("Configuring Channel A...")
        channel = 0  # Channel A
        enabled = 1  # Enable
        coupling = 1  # DC coupling
        voltage_range = 7  # ±5V range (ps4000 range code 7)
        analogue_offset = 0.0
        
        status = ps4000.ps4000SetChannel(
            handle,
            ctypes.c_int32(channel),
            ctypes.c_int16(enabled),
            ctypes.c_int32(coupling),
            ctypes.c_int32(voltage_range),
            ctypes.c_float(analogue_offset)
        )
        
        if status != 0:
            print(f"ERROR: ps4000SetChannel failed with status: {status}")
            ps4000.ps4000CloseUnit(handle)
            return False
        
        print("Channel A configured (DC, ±5V)")
        
        # Step 5: Find a valid timebase
        print("Finding valid timebase...")
        timebase = 8  # Start with timebase 8 (reasonable for test)
        no_of_samples = 1000
        oversample = 1
        time_interval_ns = ctypes.c_int32()
        time_units = ctypes.c_int32()
        max_samples = ctypes.c_int32()
        
        status = ps4000.ps4000GetTimebase2(
            handle,
            ctypes.c_uint32(timebase),
            ctypes.c_int32(no_of_samples),
            ctypes.byref(time_interval_ns),
            ctypes.c_int16(oversample),
            ctypes.byref(max_samples),
            ctypes.c_int32(0)  # segment_index
        )
        
        if status != 0:
            print(f"ERROR: ps4000GetTimebase2 failed with status: {status}")
            ps4000.ps4000CloseUnit(handle)
            return False
        
        print(f"Valid timebase found: {timebase}, interval: {time_interval_ns.value} ns")
        
        # Step 6: Set up data buffer
        buffer_length = no_of_samples
        buffer = (ctypes.c_int16 * buffer_length)()
        
        status = ps4000.ps4000SetDataBuffer(
            handle,
            ctypes.c_int32(channel),  # Channel A
            ctypes.cast(buffer, ctypes.POINTER(ctypes.c_int16)),
            ctypes.c_int32(buffer_length),
            ctypes.c_int32(0)  # segment_index
        )
        
        if status != 0:
            print(f"ERROR: ps4000SetDataBuffer failed with status: {status}")
            ps4000.ps4000CloseUnit(handle)
            return False
        
        print("Data buffer configured")
        
        # Step 7: Run block capture
        print("Running block capture...")
        pre_trigger_samples = 0
        post_trigger_samples = no_of_samples
        timebase_used = ctypes.c_uint32(timebase)
        time_indisposed_ms = ctypes.c_int32()
        
        status = ps4000.ps4000RunBlock(
            handle,
            ctypes.c_int32(pre_trigger_samples),
            ctypes.c_int32(post_trigger_samples),
            ctypes.c_uint32(timebase),
            ctypes.c_int16(oversample),
            ctypes.byref(time_indisposed_ms),
            ctypes.c_int32(0),  # segment_index
            None,  # lpReady callback
            None   # pParameter
        )
        
        if status != 0:
            print(f"ERROR: ps4000RunBlock failed with status: {status}")
            ps4000.ps4000CloseUnit(handle)
            return False
        
        # Step 8: Wait for capture to complete
        print("Waiting for capture to complete...")
        ready = ctypes.c_int16()
        max_wait_time = 5.0  # seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            status = ps4000.ps4000IsReady(handle, ctypes.byref(ready))
            if status != 0:
                print(f"ERROR: ps4000IsReady failed with status: {status}")
                ps4000.ps4000CloseUnit(handle)
                return False
            
            if ready.value:
                break
            
            time.sleep(0.01)  # 10ms poll
        
        if not ready.value:
            print("ERROR: Capture timed out")
            ps4000.ps4000CloseUnit(handle)
            return False
        
        print("Capture completed!")
        
        # Step 9: Get the data
        print("Retrieving data...")
        start_index = ctypes.c_uint32(0)
        no_of_samples_collected = ctypes.c_uint32(no_of_samples)
        downsampling_ratio = ctypes.c_uint32(1)
        downsampling_mode = ctypes.c_int32(0)  # PS4000_RATIO_MODE_NONE
        segment_index = ctypes.c_uint32(0)
        overflow = ctypes.c_int16()
        
        # ps4000GetValues parameters: handle, startIndex, noOfSamples, downsamplingRatio, downsamplingMode, segmentIndex, overflow
        status = ps4000.ps4000GetValues(
            handle,
            start_index,
            ctypes.byref(no_of_samples_collected),
            downsampling_ratio,
            downsampling_mode,
            segment_index,
            ctypes.byref(overflow)
        )
        
        if status != 0:
            print(f"ERROR: ps4000GetValues failed with status: {status}")
            print("Common ps4000 error codes:")
            print("  PICO_INVALID_PARAMETER = 4")
            print("  PICO_NO_SAMPLES_AVAILABLE = 29")
            print("  PICO_INVALID_TIMEBASE = 70")
            ps4000.ps4000CloseUnit(handle)
            return False
        
        print(f"Retrieved {no_of_samples_collected.value} samples")
        
        # Step 10: Convert ADC counts to volts and print first 10
        print("\nFirst 10 voltage samples:")
        max_adc = 32767  # 16-bit ADC
        voltage_range_v = 5.0  # ±5V range
        
        for i in range(min(10, no_of_samples_collected.value)):
            adc_count = buffer[i]
            voltage = (adc_count * voltage_range_v) / max_adc
            print(f"  Sample {i}: {adc_count} ADC → {voltage:.4f} V")
        
        # Step 11: Clean shutdown
        print("\nStopping and closing unit...")
        ps4000.ps4000Stop(handle)
        ps4000.ps4000CloseUnit(handle)
        
        print("✓ Smoke test PASSED - PicoScope 4262 connectivity confirmed!")
        return True
        
    except Exception as e:
        print(f"ERROR: Exception during test: {e}")
        print(f"DLL path used: {dll_path}")
        return False


if __name__ == "__main__":
    success = test_pico_connectivity()
    sys.exit(0 if success else 1)
