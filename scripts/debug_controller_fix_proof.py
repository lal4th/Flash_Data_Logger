#!/usr/bin/env python3
"""
Proof-of-concept: wrapper-based fix for 6824E controller issues.
Tests relative timestamp conversion and larger block sizing without touching app code.
"""

from __future__ import annotations

import time
from typing import List, Tuple, Any
import numpy as np

from app.core.streaming_controller import StreamingController


def main() -> int:
    print("\n=== Controller Fix Proof (6824E) ===")
    
    # Track session start for relative timestamps
    session_start = time.perf_counter()
    plot_timestamps: List[float] = []
    csv_timestamps: List[float] = []
    block_sizes: List[int] = []
    
    c = StreamingController()
    
    # Monkeypatch _process_block to convert to relative timestamps
    orig_process_block = c._process_block  # type: ignore[attr-defined]
    
    def relative_process_block(block_data):
        """Convert absolute timestamps to relative seconds from session start."""
        processed = orig_process_block(block_data)
        if processed:
            # Convert first timestamp to relative seconds
            first_timestamp = processed[0][0]
            relative_start = first_timestamp - session_start
            
            # Convert all timestamps in the block to relative
            relative_processed = []
            for i, (timestamp, a_val, b_val) in enumerate(processed):
                relative_timestamp = relative_start + (i * 0.01)  # 100Hz = 10ms intervals
                relative_processed.append((relative_timestamp, a_val, b_val))
            
            return relative_processed
        return processed
    
    # Monkeypatch _queue_plot_data to capture timestamps
    orig_queue_plot = c._queue_plot_data  # type: ignore[attr-defined]
    
    def capture_plot_queue(block_data):
        if block_data:
            timestamps = [d[0] for d in block_data]
            plot_timestamps.extend(timestamps)
            block_sizes.append(len(block_data))
        return orig_queue_plot(block_data)
    
    # Monkeypatch _queue_csv_data to capture timestamps  
    orig_queue_csv = c._queue_csv_data  # type: ignore[attr-defined]
    
    def capture_csv_queue(block_data):
        if block_data:
            timestamps = [d[0] for d in block_data]
            csv_timestamps.extend(timestamps)
        return orig_queue_csv(block_data)
    
    # Apply patches
    c._process_block = relative_process_block  # type: ignore
    c._queue_plot_data = capture_plot_queue  # type: ignore
    c._queue_csv_data = capture_csv_queue  # type: ignore
    
    # Run acquisition
    c.probe_device()
    c.start()
    try:
        time.sleep(2.0)
    finally:
        c.stop()
    
    # Analyze results
    print(f"Session duration: {time.perf_counter() - session_start:.2f}s")
    print(f"Plot timestamps: {len(plot_timestamps)} samples")
    print(f"CSV timestamps: {len(csv_timestamps)} samples")
    print(f"Block sizes: {block_sizes[:10]}...")
    
    if plot_timestamps:
        print(f"Plot timestamp range: {plot_timestamps[0]:.3f} to {plot_timestamps[-1]:.3f}")
        print(f"Plot timestamp delta: {plot_timestamps[-1] - plot_timestamps[0]:.3f}s")
        
        # Check if timestamps are relative (should start near 0)
        if plot_timestamps[0] < 10.0:  # Less than 10 seconds = likely relative
            print("✓ Plot timestamps appear to be relative")
        else:
            print("✗ Plot timestamps still appear to be absolute")
    
    if csv_timestamps:
        print(f"CSV timestamp range: {csv_timestamps[0]:.3f} to {csv_timestamps[-1]:.3f}")
        if csv_timestamps[0] < 10.0:
            print("✓ CSV timestamps appear to be relative")
        else:
            print("✗ CSV timestamps still appear to be absolute")
    
    # Check block sizing
    avg_block_size = np.mean(block_sizes) if block_sizes else 0
    print(f"Average block size: {avg_block_size:.1f} samples")
    if avg_block_size > 1.0:
        print("✓ Block sizing improved (multi-sample blocks)")
    else:
        print("✗ Block sizing still single-sample")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

