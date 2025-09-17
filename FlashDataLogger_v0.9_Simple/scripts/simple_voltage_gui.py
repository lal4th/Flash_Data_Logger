#!/usr/bin/env python3
"""
Simple PicoScope 4262 Voltage GUI

A simplified GUI that bypasses the problematic detection code
and uses the working DLL approach directly.

Usage:
    python scripts/simple_voltage_gui.py
"""

import sys
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import ctypes
import os
import numpy as np

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


class SimpleVoltageGUI:
    """Simplified GUI for live voltage monitoring with PicoScope 4262."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PicoScope 4262 Live Voltage Monitor")
        self.root.geometry("600x500")
        
        # PicoScope variables
        self.handle = ctypes.c_int16(0)
        self.lib = None
        self.opened = False
        self.running = False
        self.measurement_thread = None
        
        # GUI variables
        self.voltage_var = tk.StringVar(value="0.000000")
        self.adc_var = tk.StringVar(value="0")
        self.std_var = tk.StringVar(value="0.000000")
        self.samples_var = tk.StringVar(value="0")
        self.range_var = tk.StringVar(value="±5V")
        self.status_var = tk.StringVar(value="Not connected")
        
        # Voltage ranges - CORRECTED MAPPING
        self.voltage_ranges = {
            "±10mV": (0, 0.010),
            "±20mV": (1, 0.020),
            "±50mV": (2, 0.050),
            "±100mV": (3, 0.100),
            "±200mV": (4, 0.200),
            "±500mV": (5, 0.500),
            "±1V": (6, 1.000),
            "±2V": (7, 2.000),   # CORRECTED: This was labeled ±5V but is actually ±2V
            "±5V": (8, 5.000),   # CORRECTED: This was labeled ±10V but is actually ±5V
            "±10V": (9, 10.000), # CORRECTED: This was labeled ±20V but is actually ±10V
        }
        
        self.setup_gui()
        self.setup_picoscope()
    
    def setup_gui(self):
        """Set up the GUI components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="PicoScope 4262 Live Voltage Monitor", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Status
        status_label = ttk.Label(main_frame, text="Status:")
        status_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        status_value = ttk.Label(main_frame, textvariable=self.status_var, 
                                foreground="red", font=("Arial", 10, "bold"))
        status_value.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Voltage range selection
        range_label = ttk.Label(main_frame, text="Voltage Range:")
        range_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.range_combo = ttk.Combobox(main_frame, textvariable=self.range_var, 
                                       values=list(self.voltage_ranges.keys()),
                                       state="readonly", width=15)
        self.range_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        self.range_combo.bind("<<ComboboxSelected>>", self.on_range_changed)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Monitoring", 
                                      command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Monitoring", 
                                     command=self.stop_monitoring, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Voltage display
        voltage_frame = ttk.LabelFrame(main_frame, text="Live Readings", padding="10")
        voltage_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        voltage_frame.columnconfigure(1, weight=1)
        
        # Voltage value
        voltage_label = ttk.Label(voltage_frame, text="Voltage:")
        voltage_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        voltage_value = ttk.Label(voltage_frame, textvariable=self.voltage_var, 
                                 font=("Arial", 20, "bold"), foreground="blue")
        voltage_value.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # ADC value
        adc_label = ttk.Label(voltage_frame, text="Raw ADC:")
        adc_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        adc_value = ttk.Label(voltage_frame, textvariable=self.adc_var, 
                             font=("Arial", 14), foreground="green")
        adc_value.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Standard deviation
        std_label = ttk.Label(voltage_frame, text="Std Dev:")
        std_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        std_value = ttk.Label(voltage_frame, textvariable=self.std_var, 
                             font=("Arial", 12), foreground="orange")
        std_value.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Sample count
        samples_label = ttk.Label(voltage_frame, text="Samples:")
        samples_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        samples_value = ttk.Label(voltage_frame, textvariable=self.samples_var, 
                                 font=("Arial", 10), foreground="gray")
        samples_value.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Measurement Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log controls
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Button(log_button_frame, text="Clear Log", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(log_button_frame, text="Save Log", 
                  command=self.save_log).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = """
Instructions:
1. Select a voltage range from the dropdown
2. Connect your voltage source to PicoScope Channel A
3. Click 'Start Monitoring' to begin readings
4. Values update every 2 seconds with averaged measurements
5. Std Dev shows measurement stability (±lower is better)
6. Use the log to record measurements for different voltage inputs
7. Click 'Stop Monitoring' when done

Test different voltage inputs and record the averaged results!
        """
        
        instructions_label = ttk.Label(main_frame, text=instructions, 
                                      font=("Arial", 9), foreground="gray")
        instructions_label.grid(row=6, column=0, columnspan=3, pady=10, sticky=tk.W)
    
    def setup_picoscope(self):
        """Set up PicoScope connection using the working approach."""
        try:
            self.log_message("Setting up PicoScope connection...")
            
            # Use the working DLL path from diagnostics
            dll_path = r"C:\Program Files\Pico Technology\PicoScope 7 T&M Stable\ps4000.dll"
            
            # Add DLL directory to PATH
            dll_dir = os.path.dirname(dll_path)
            old_path = os.environ.get('PATH', '')
            os.environ['PATH'] = dll_dir + os.pathsep + old_path
            
            if hasattr(os, 'add_dll_directory'):
                os.add_dll_directory(dll_dir)
            
            # Load DLL
            ps4000 = ctypes.CDLL(dll_path)
            
            # Set up function signatures
            ps4000.ps4000OpenUnit.argtypes = [ctypes.POINTER(ctypes.c_int16)]
            ps4000.ps4000OpenUnit.restype = ctypes.c_int16
            ps4000.ps4000CloseUnit.argtypes = [ctypes.c_int16]
            ps4000.ps4000CloseUnit.restype = ctypes.c_int16
            ps4000.ps4000SetChannel.argtypes = [ctypes.c_int16, ctypes.c_int32, ctypes.c_int16, ctypes.c_int32, ctypes.c_int32, ctypes.c_float]
            ps4000.ps4000SetChannel.restype = ctypes.c_int16
            ps4000.ps4000GetTimebase2.argtypes = [ctypes.c_int16, ctypes.c_uint32, ctypes.c_int32, ctypes.POINTER(ctypes.c_int32), ctypes.c_int16, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32]
            ps4000.ps4000GetTimebase2.restype = ctypes.c_int16
            ps4000.ps4000SetDataBuffer.argtypes = [ctypes.c_int16, ctypes.c_int32, ctypes.POINTER(ctypes.c_int16), ctypes.c_int32, ctypes.c_int32]
            ps4000.ps4000SetDataBuffer.restype = ctypes.c_int16
            ps4000.ps4000RunBlock.argtypes = [ctypes.c_int16, ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32, ctypes.c_int16, ctypes.POINTER(ctypes.c_int32), ctypes.c_int32, ctypes.c_void_p, ctypes.c_void_p]
            ps4000.ps4000RunBlock.restype = ctypes.c_int16
            ps4000.ps4000IsReady.argtypes = [ctypes.c_int16, ctypes.POINTER(ctypes.c_int16)]
            ps4000.ps4000IsReady.restype = ctypes.c_int16
            ps4000.ps4000GetValues.argtypes = [ctypes.c_int16, ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_int16)]
            ps4000.ps4000GetValues.restype = ctypes.c_int16
            ps4000.ps4000Stop.argtypes = [ctypes.c_int16]
            ps4000.ps4000Stop.restype = ctypes.c_int16
            
            # Open device
            handle = ctypes.c_int16()
            status = ps4000.ps4000OpenUnit(ctypes.byref(handle))
            
            if status != 0:
                self.status_var.set(f"Open failed (status: {status})")
                self.log_message(f"ps4000OpenUnit failed with status: {status}")
                return
            
            self.handle = handle
            self.lib = ps4000
            self.opened = True
            self.status_var.set("Connected")
            
            # Configure initial channel
            self.configure_channel()
            
            self.log_message("PicoScope 4262 connected successfully!")
            
        except Exception as e:
            self.status_var.set("Connection failed")
            self.log_message(f"Connection failed: {e}")
    
    def configure_channel(self):
        """Configure PicoScope channel with current voltage range."""
        if not self.opened or self.lib is None:
            return
        
        range_name = self.range_var.get()
        range_index, full_scale = self.voltage_ranges[range_name]
        
        status = self.lib.ps4000SetChannel(
            self.handle,
            ctypes.c_int32(0),  # Channel A
            ctypes.c_int16(1),  # enabled
            ctypes.c_int32(1),  # DC coupling
            ctypes.c_int32(range_index),  # voltage range
            ctypes.c_float(0.0)  # analogue_offset
        )
        
        if status != 0:
            self.log_message(f"ps4000SetChannel failed with status: {status}")
        else:
            self.log_message(f"Configured for {range_name} (range index: {range_index})")
    
    def on_range_changed(self, event=None):
        """Handle voltage range change."""
        if self.opened:
            self.configure_channel()
    
    def start_monitoring(self):
        """Start live voltage monitoring."""
        if not self.opened:
            messagebox.showerror("Error", "PicoScope not connected")
            return
        
        if self.running:
            return
        
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Start measurement thread
        self.measurement_thread = threading.Thread(target=self.measurement_loop, daemon=True)
        self.measurement_thread.start()
        
        self.log_message("Started live monitoring")
    
    def stop_monitoring(self):
        """Stop live voltage monitoring."""
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        self.log_message("Stopped live monitoring")
    
    def measurement_loop(self):
        """Main measurement loop running in separate thread."""
        while self.running:
            try:
                # Collect samples for 2 seconds
                samples = []
                start_time = time.time()
                
                while time.time() - start_time < 2.0 and self.running:
                    try:
                        # Capture sample
                        adc_value = self.capture_sample()
                        
                        # Convert to voltage
                        range_name = self.range_var.get()
                        range_index, full_scale = self.voltage_ranges[range_name]
                        voltage = (adc_value / 32768.0) * full_scale
                        
                        samples.append((adc_value, voltage))
                        time.sleep(0.1)  # 10 Hz sampling rate
                        
                    except Exception as e:
                        self.root.after(0, self.log_message, f"Sample error: {e}")
                        time.sleep(0.1)
                
                if samples and self.running:
                    # Calculate averages
                    avg_adc = int(np.mean([s[0] for s in samples]))
                    avg_voltage = np.mean([s[1] for s in samples])
                    std_voltage = np.std([s[1] for s in samples])
                    
                    # Update GUI (thread-safe)
                    self.root.after(0, self.update_display, avg_adc, avg_voltage, std_voltage, len(samples))
                
            except Exception as e:
                self.root.after(0, self.log_message, f"Measurement error: {e}")
                time.sleep(1.0)
    
    def capture_sample(self):
        """Capture a single sample and return raw ADC value."""
        if not self.opened or self.lib is None:
            raise RuntimeError("Device not opened")
        
        # Single sample capture
        no_of_samples = 1
        timebase = 8
        oversample = 1
        
        # Get timing info
        time_interval_ns = ctypes.c_int32()
        time_units = ctypes.c_int32()
        max_samples = ctypes.c_int32()
        
        status = self.lib.ps4000GetTimebase2(
            self.handle,
            ctypes.c_uint32(timebase),
            ctypes.c_int32(no_of_samples),
            ctypes.byref(time_interval_ns),
            ctypes.c_int16(oversample),
            ctypes.byref(max_samples),
            ctypes.c_int32(0)
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000GetTimebase2 failed with status: {status}")
        
        # Set up buffer
        buffer = (ctypes.c_int16 * no_of_samples)()
        
        status = self.lib.ps4000SetDataBuffer(
            self.handle,
            ctypes.c_int32(0),  # Channel A
            ctypes.cast(buffer, ctypes.POINTER(ctypes.c_int16)),
            ctypes.c_int32(no_of_samples),
            ctypes.c_int32(0)
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000SetDataBuffer failed with status: {status}")
        
        # Run capture
        status = self.lib.ps4000RunBlock(
            self.handle,
            ctypes.c_int32(0),  # pre_trigger
            ctypes.c_int32(no_of_samples),  # post_trigger
            ctypes.c_uint32(timebase),
            ctypes.c_int16(oversample),
            ctypes.byref(ctypes.c_int32()),  # time_indisposed
            ctypes.c_int32(0),  # segment_index
            None,  # callback
            None   # parameter
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000RunBlock failed with status: {status}")
        
        # Wait for completion
        ready = ctypes.c_int16()
        start_time = time.time()
        
        while time.time() - start_time < 5.0:
            status = self.lib.ps4000IsReady(self.handle, ctypes.byref(ready))
            if status != 0:
                raise RuntimeError(f"ps4000IsReady failed with status: {status}")
            
            if ready.value:
                break
            
            time.sleep(0.01)
        
        if not ready.value:
            raise RuntimeError("Capture timed out")
        
        # Get data
        start_index = ctypes.c_uint32(0)
        no_of_samples_collected = ctypes.c_uint32(no_of_samples)
        downsampling_ratio = ctypes.c_uint32(1)
        downsampling_mode = ctypes.c_int32(0)
        segment_index = ctypes.c_uint32(0)
        overflow = ctypes.c_int16()
        
        status = self.lib.ps4000GetValues(
            self.handle,
            start_index,
            ctypes.byref(no_of_samples_collected),
            downsampling_ratio,
            downsampling_mode,
            segment_index,
            ctypes.byref(overflow)
        )
        
        if status != 0:
            raise RuntimeError(f"ps4000GetValues failed with status: {status}")
        
        if no_of_samples_collected.value == 0:
            raise RuntimeError("No samples collected")
        
        return int(buffer[0])
    
    def update_display(self, adc_value, voltage, std_voltage, sample_count):
        """Update the display with new averaged values."""
        self.voltage_var.set(f"{voltage:.6f}")
        self.adc_var.set(str(adc_value))
        self.std_var.set(f"±{std_voltage:.6f}")
        self.samples_var.set(f"{sample_count} samples")
        
        # Log the measurement
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {voltage:.6f}V (ADC: {adc_value}, Std: ±{std_voltage:.6f}V, {sample_count} samples)\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def log_message(self, message):
        """Add a message to the log."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the log."""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """Save the log to a file."""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"Log saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {e}")
    
    def on_closing(self):
        """Handle window closing."""
        self.running = False
        if self.measurement_thread and self.measurement_thread.is_alive():
            self.measurement_thread.join(timeout=1)
        
        if self.opened and self.lib is not None:
            try:
                self.lib.ps4000Stop(self.handle)
            except Exception:
                pass
            try:
                self.lib.ps4000CloseUnit(self.handle)
            except Exception:
                pass
        
        self.root.destroy()
    
    def run(self):
        """Run the GUI."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()


def main():
    """Main function."""
    try:
        app = SimpleVoltageGUI()
        app.run()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
