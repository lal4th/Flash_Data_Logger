#!/usr/bin/env python3
"""
Test Phase 1 - Block-mode integration test
Tests the PicoPs4000Source class directly to verify it works.
"""

import sys
import time
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.acquisition.pico_ps4000_source import PicoPs4000Source


def test_pico_source():
    """Test the PicoPs4000Source class directly."""
    print("=== Phase 1 Test: PicoPs4000Source ===")
    
    try:
        # Create and configure the source
        source = PicoPs4000Source()
        print("✓ PicoPs4000Source created")
        
        # Configure the source
        source.configure(
            sample_rate_hz=100,
            channel=0,  # Channel A
            coupling=1,  # DC
            voltage_range=7,  # ±5V
            resolution_bits=16
        )
        print("✓ Source configured successfully")
        print(f"✓ Diagnostics: {source.get_diagnostics()}")
        
        # Read some samples
        print("\nReading 10 samples:")
        for i in range(10):
            value, timestamp = source.read()
            print(f"  Sample {i}: {value:.4f} V @ {timestamp:.3f}s")
            time.sleep(0.1)  # Small delay between samples
        
        # Clean up
        source.close()
        print("\n✓ Source closed successfully")
        print("✓ Phase 1 Test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n✗ Phase 1 Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pico_source()
    sys.exit(0 if success else 1)
