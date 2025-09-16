"""
PicoScope 4262 Voltage Conversion Module

This module provides mathematically correct voltage conversion for PicoScope 4262
without using hard-coded calibration factors.

Mathematical Derivation:
- PicoScope 4262 uses a 16-bit signed ADC
- ADC range: -32768 to +32767 (total: 65536 discrete levels)
- For voltage range ±V_range, the full scale span is 2*V_range
- Conversion factor: (2*V_range) / 65536 = V_range / 32768 volts per count
- Formula: V_actual = (ADC_value / 32768) * V_range

This formula is mathematically derived and works consistently across all voltage ranges.
"""

import numpy as np
from typing import Union, Dict, Any
from dataclasses import dataclass


@dataclass
class VoltageRange:
    """Represents a voltage range configuration."""
    index: int
    name: str
    full_scale_volts: float
    description: str


class PicoScopeVoltageConverter:
    """
    Mathematically correct voltage converter for PicoScope 4262.
    
    This converter uses the derived formula V = (ADC/32768) * V_range
    which works consistently across all voltage ranges without calibration.
    """
    
    # PicoScope 4000 series voltage ranges - CORRECTED MAPPING
    VOLTAGE_RANGES = {
        0: VoltageRange(0, "±10mV", 0.010, "±10 millivolts"),
        1: VoltageRange(1, "±20mV", 0.020, "±20 millivolts"),
        2: VoltageRange(2, "±50mV", 0.050, "±50 millivolts"),
        3: VoltageRange(3, "±100mV", 0.100, "±100 millivolts"),
        4: VoltageRange(4, "±200mV", 0.200, "±200 millivolts"),
        5: VoltageRange(5, "±500mV", 0.500, "±500 millivolts"),
        6: VoltageRange(6, "±1V", 1.000, "±1 volt"),
        7: VoltageRange(7, "±2V", 2.000, "±2 volts"),   # CORRECTED: This was labeled ±5V but is actually ±2V
        8: VoltageRange(8, "±5V", 5.000, "±5 volts"),   # CORRECTED: This was labeled ±10V but is actually ±5V
        9: VoltageRange(9, "±10V", 10.000, "±10 volts"), # CORRECTED: This was labeled ±20V but is actually ±10V
    }
    
    # ADC characteristics
    ADC_MAX_VALUE = 32767
    ADC_MIN_VALUE = -32768
    ADC_TOTAL_LEVELS = 65536
    
    def __init__(self):
        """Initialize the voltage converter."""
        pass
    
    def get_voltage_range(self, range_index: int) -> VoltageRange:
        """
        Get voltage range information for a given range index.
        
        Args:
            range_index: The PicoScope voltage range index (0-9)
            
        Returns:
            VoltageRange object containing range information
            
        Raises:
            ValueError: If range_index is not valid
        """
        if range_index not in self.VOLTAGE_RANGES:
            raise ValueError(f"Invalid voltage range index: {range_index}. Valid ranges: 0-9")
        
        return self.VOLTAGE_RANGES[range_index]
    
    def calculate_conversion_factor(self, voltage_range: Union[int, VoltageRange]) -> float:
        """
        Calculate the conversion factor for a given voltage range.
        
        Mathematical derivation:
        - For voltage range ±V_range, full scale span is 2*V_range
        - ADC has 65536 discrete levels
        - Conversion factor = (2*V_range) / 65536 = V_range / 32768
        
        Args:
            voltage_range: Either a range index (int) or VoltageRange object
            
        Returns:
            Conversion factor in volts per ADC count
        """
        if isinstance(voltage_range, int):
            voltage_range = self.get_voltage_range(voltage_range)
        
        # Mathematical formula: V_range / 32768
        return voltage_range.full_scale_volts / 32768.0
    
    def convert_adc_to_voltage(
        self, 
        adc_value: Union[int, np.ndarray], 
        voltage_range: Union[int, VoltageRange]
    ) -> Union[float, np.ndarray]:
        """
        Convert ADC value(s) to voltage using the mathematically derived formula.
        
        Formula: V_actual = (ADC_value / 32768) * V_range
        
        This formula is mathematically correct and works consistently across
        all voltage ranges without requiring calibration factors.
        
        Args:
            adc_value: Raw ADC value(s) from PicoScope
            voltage_range: Either a range index (int) or VoltageRange object
            
        Returns:
            Converted voltage value(s) in volts
        """
        if isinstance(voltage_range, int):
            voltage_range = self.get_voltage_range(voltage_range)
        
        # Apply the mathematically derived formula
        # V = (ADC / 32768) * V_range
        if isinstance(adc_value, np.ndarray):
            return (adc_value.astype(np.float64) / 32768.0) * voltage_range.full_scale_volts
        else:
            return (float(adc_value) / 32768.0) * voltage_range.full_scale_volts
    
    def convert_voltage_to_adc(
        self, 
        voltage: Union[float, np.ndarray], 
        voltage_range: Union[int, VoltageRange]
    ) -> Union[int, np.ndarray]:
        """
        Convert voltage value(s) to ADC counts (inverse of convert_adc_to_voltage).
        
        Formula: ADC_value = (V_actual / V_range) * 32768
        
        Args:
            voltage: Voltage value(s) in volts
            voltage_range: Either a range index (int) or VoltageRange object
            
        Returns:
            ADC count value(s)
        """
        if isinstance(voltage_range, int):
            voltage_range = self.get_voltage_range(voltage_range)
        
        # Inverse formula: ADC = (V / V_range) * 32768
        if isinstance(voltage, np.ndarray):
            adc_values = (voltage / voltage_range.full_scale_volts) * 32768.0
            return np.round(adc_values).astype(np.int16)
        else:
            return int(round((voltage / voltage_range.full_scale_volts) * 32768.0))
    
    def validate_adc_range(self, adc_value: Union[int, np.ndarray]) -> bool:
        """
        Validate that ADC values are within the valid range.
        
        Args:
            adc_value: ADC value(s) to validate
            
        Returns:
            True if all values are within valid range, False otherwise
        """
        if isinstance(adc_value, np.ndarray):
            return np.all((adc_value >= self.ADC_MIN_VALUE) & (adc_value <= self.ADC_MAX_VALUE))
        else:
            return self.ADC_MIN_VALUE <= adc_value <= self.ADC_MAX_VALUE
    
    def get_voltage_resolution(self, voltage_range: Union[int, VoltageRange]) -> float:
        """
        Get the voltage resolution (smallest voltage change) for a given range.
        
        Args:
            voltage_range: Either a range index (int) or VoltageRange object
            
        Returns:
            Voltage resolution in volts
        """
        if isinstance(voltage_range, int):
            voltage_range = self.get_voltage_range(voltage_range)
        
        # Resolution = V_range / 32768 (same as conversion factor)
        return self.calculate_conversion_factor(voltage_range)
    
    def get_available_ranges(self) -> Dict[int, VoltageRange]:
        """
        Get all available voltage ranges.
        
        Returns:
            Dictionary mapping range indices to VoltageRange objects
        """
        return self.VOLTAGE_RANGES.copy()
    
    def find_best_range_for_voltage(self, voltage: float, margin: float = 0.1) -> VoltageRange:
        """
        Find the best voltage range for measuring a given voltage.
        
        Args:
            voltage: The voltage to be measured
            margin: Safety margin (0.1 = 10% margin)
            
        Returns:
            Best VoltageRange for the given voltage
        """
        abs_voltage = abs(voltage)
        required_range = abs_voltage * (1.0 + margin)
        
        # Find the smallest range that can accommodate the voltage
        for range_idx in sorted(self.VOLTAGE_RANGES.keys()):
            voltage_range = self.VOLTAGE_RANGES[range_idx]
            if voltage_range.full_scale_volts >= required_range:
                return voltage_range
        
        # If no range is found, return the largest range
        return self.VOLTAGE_RANGES[max(self.VOLTAGE_RANGES.keys())]
    
    def get_conversion_info(self, voltage_range: Union[int, VoltageRange]) -> Dict[str, Any]:
        """
        Get comprehensive conversion information for a voltage range.
        
        Args:
            voltage_range: Either a range index (int) or VoltageRange object
            
        Returns:
            Dictionary containing conversion information
        """
        if isinstance(voltage_range, int):
            voltage_range = self.get_voltage_range(voltage_range)
        
        conversion_factor = self.calculate_conversion_factor(voltage_range)
        resolution = self.get_voltage_resolution(voltage_range)
        
        return {
            'range_index': voltage_range.index,
            'range_name': voltage_range.name,
            'full_scale_volts': voltage_range.full_scale_volts,
            'description': voltage_range.description,
            'conversion_factor': conversion_factor,
            'voltage_resolution': resolution,
            'adc_max_value': self.ADC_MAX_VALUE,
            'adc_min_value': self.ADC_MIN_VALUE,
            'adc_total_levels': self.ADC_TOTAL_LEVELS,
            'formula': 'V = (ADC / 32768) * V_range'
        }


# Convenience functions for easy use
def convert_adc_to_voltage(adc_value: Union[int, np.ndarray], voltage_range: int) -> Union[float, np.ndarray]:
    """
    Convenience function to convert ADC values to voltage.
    
    Args:
        adc_value: Raw ADC value(s) from PicoScope
        voltage_range: PicoScope voltage range index (0-9)
        
    Returns:
        Converted voltage value(s) in volts
    """
    converter = PicoScopeVoltageConverter()
    return converter.convert_adc_to_voltage(adc_value, voltage_range)


def convert_voltage_to_adc(voltage: Union[float, np.ndarray], voltage_range: int) -> Union[int, np.ndarray]:
    """
    Convenience function to convert voltage values to ADC counts.
    
    Args:
        voltage: Voltage value(s) in volts
        voltage_range: PicoScope voltage range index (0-9)
        
    Returns:
        ADC count value(s)
    """
    converter = PicoScopeVoltageConverter()
    return converter.convert_voltage_to_adc(voltage, voltage_range)


def get_voltage_range_info(voltage_range: int) -> Dict[str, Any]:
    """
    Convenience function to get voltage range information.
    
    Args:
        voltage_range: PicoScope voltage range index (0-9)
        
    Returns:
        Dictionary containing range information
    """
    converter = PicoScopeVoltageConverter()
    return converter.get_conversion_info(voltage_range)


# Example usage and testing
if __name__ == "__main__":
    # Create converter instance
    converter = PicoScopeVoltageConverter()
    
    # Test with different voltage ranges
    test_ranges = [6, 7, 8, 9]  # ±1V, ±5V, ±10V, ±20V
    test_adc_values = [0, 16384, -16384, 32767, -32768]
    
    print("PicoScope 4262 Voltage Conversion Test")
    print("=" * 40)
    
    for range_idx in test_ranges:
        voltage_range = converter.get_voltage_range(range_idx)
        print(f"\nRange {range_idx}: {voltage_range.name}")
        print("-" * 30)
        
        for adc_value in test_adc_values:
            voltage = converter.convert_adc_to_voltage(adc_value, range_idx)
            print(f"  ADC {adc_value:6d} -> {voltage:8.6f}V")
        
        # Show conversion info
        info = converter.get_conversion_info(range_idx)
        print(f"  Conversion factor: {info['conversion_factor']:.8f} V/count")
        print(f"  Voltage resolution: {info['voltage_resolution']:.8f} V")
