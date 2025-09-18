#!/usr/bin/env python3
"""
Debug the extended configure_multi_channel method to verify it can configure all 8 channels.
"""

from __future__ import annotations

from app.acquisition.pico_6000_direct import Pico6000DirectSource


def main() -> int:
    print("\n=== Extended Configure Multi-Channel Debug ===")
    
    source = Pico6000DirectSource()
    
    if source.connect():
        print("✓ Connected to 6824E")
        
        # Test 1: Configure only A and B (backward compatibility)
        print("\nTest 1: Configure only A and B (backward compatibility)")
        try:
            source.configure_multi_channel(
                sample_rate_hz=100,
                channel_a_enabled=True,
                channel_b_enabled=True,
                channel_c_enabled=False,
                channel_d_enabled=False,
            )
            print("  ✓ Backward compatibility test passed")
        except Exception as e:
            print(f"  ✗ Backward compatibility test failed: {e}")
        
        # Test 2: Configure A, B, C, and D
        print("\nTest 2: Configure A, B, C, and D")
        try:
            source.configure_multi_channel(
                sample_rate_hz=100,
                channel_a_enabled=True,
                channel_b_enabled=True,
                channel_c_enabled=True,
                channel_d_enabled=True,
                channel_e_enabled=False,
                channel_f_enabled=False,
                channel_g_enabled=False,
                channel_h_enabled=False,
            )
            print("  ✓ A,B,C,D configuration test passed")
        except Exception as e:
            print(f"  ✗ A,B,C,D configuration test failed: {e}")
        
        # Test 3: Configure all 8 channels
        print("\nTest 3: Configure all 8 channels")
        try:
            source.configure_multi_channel(
                sample_rate_hz=100,
                channel_a_enabled=True,
                channel_b_enabled=True,
                channel_c_enabled=True,
                channel_d_enabled=True,
                channel_e_enabled=True,
                channel_f_enabled=True,
                channel_g_enabled=True,
                channel_h_enabled=True,
            )
            print("  ✓ All 8 channels configuration test passed")
        except Exception as e:
            print(f"  ✗ All 8 channels configuration test failed: {e}")
        
        source.disconnect()
    else:
        print("✗ Failed to connect to 6824E")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

