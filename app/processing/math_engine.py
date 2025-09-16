"""
Math Engine for Flash Data Logger v0.9
Provides real-time formula evaluation for math channels.
"""

import math
import re
import numpy as np
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass


@dataclass
class MathChannelConfig:
    """Configuration for a math channel."""
    name: str
    formula: str
    enabled: bool = True
    y_min: float = -10.0
    y_max: float = 10.0
    y_label: str = ""
    color: Optional[Any] = None


class FormulaError(Exception):
    """Exception raised for formula evaluation errors."""
    pass


class MathEngine:
    """
    Real-time mathematical formula evaluation engine.
    Supports basic operations, trigonometric functions, and statistical operations.
    """
    
    def __init__(self):
        self._compiled_formulas: Dict[str, Callable] = {}
        self._math_channels: Dict[str, MathChannelConfig] = {}
        self._data_buffers: Dict[str, List[float]] = {}
        
        # Available functions for formulas
        self._functions = {
            # Basic math
            'abs': abs,
            'sqrt': math.sqrt,
            'pow': pow,
            'exp': math.exp,
            'log': math.log,
            'log10': math.log10,
            'ln': math.log,
            
            # Trigonometric
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'atan2': math.atan2,
            
            # Statistical (will be implemented with numpy)
            'avg': self._avg,
            'min': self._min,
            'max': self._max,
            'std': self._std,
            'median': self._median,
            
            # Constants
            'pi': math.pi,
            'e': math.e,
        }
        
        # Safe namespace for formula evaluation
        self._safe_namespace = {
            '__builtins__': {},
            **self._functions,
            'A': 0.0,  # Channel A value
            'B': 0.0,  # Channel B value
        }
    
    def add_math_channel(self, name: str, formula: str, config: Optional[MathChannelConfig] = None) -> bool:
        """
        Add a new math channel with the given formula.
        Returns True if successful, False if formula is invalid.
        """
        try:
            # Validate and compile formula
            compiled_func = self._compile_formula(formula)
            
            # Create or update math channel
            if config is None:
                config = MathChannelConfig(name=name, formula=formula)
            else:
                config.formula = formula
            
            self._math_channels[name] = config
            self._compiled_formulas[name] = compiled_func
            self._data_buffers[name] = []
            
            return True
            
        except FormulaError:
            return False
    
    def remove_math_channel(self, name: str) -> None:
        """Remove a math channel."""
        if name in self._math_channels:
            del self._math_channels[name]
        if name in self._compiled_formulas:
            del self._compiled_formulas[name]
        if name in self._data_buffers:
            del self._data_buffers[name]
    
    def update_channel_data(self, channel_a: float, channel_b: float) -> Dict[str, float]:
        """
        Update channel data and calculate all math channel values.
        Returns dictionary of math channel name -> calculated value.
        """
        # Update safe namespace with current channel values
        self._safe_namespace['A'] = channel_a
        self._safe_namespace['B'] = channel_b
        
        results = {}
        
        for name, config in self._math_channels.items():
            if not config.enabled:
                continue
                
            try:
                # Calculate math channel value
                compiled_func = self._compiled_formulas[name]
                value = compiled_func()
                
                # Store in buffer for statistical functions
                self._data_buffers[name].append(value)
                
                # Keep buffer size reasonable (last 1000 values)
                if len(self._data_buffers[name]) > 1000:
                    self._data_buffers[name] = self._data_buffers[name][-1000:]
                
                results[name] = value
                
            except Exception as e:
                # Handle calculation errors gracefully - return NaN without printing
                results[name] = float('nan')
                # Note: Error messages suppressed to reduce terminal noise
        
        return results
    
    def validate_formula(self, formula: str) -> tuple[bool, str]:
        """
        Validate a formula without executing it.
        Returns (is_valid, error_message).
        """
        try:
            self._compile_formula(formula)
            return True, ""
        except FormulaError as e:
            return False, str(e)
    
    def _compile_formula(self, formula: str) -> Callable:
        """
        Compile a formula into a callable function.
        Raises FormulaError if formula is invalid.
        """
        if not formula.strip():
            raise FormulaError("Empty formula")
        
        # Clean up formula
        formula = formula.strip()
        
        # Replace ^ with ** for Python power operator
        formula = formula.replace('^', '**')
        
        # Validate formula syntax
        self._validate_syntax(formula)
        
        # Create a safe evaluation function
        def compiled_func():
            try:
                return float(eval(formula, self._safe_namespace))
            except Exception as e:
                raise FormulaError(f"Calculation error: {e}")
        
        return compiled_func
    
    def _validate_syntax(self, formula: str) -> None:
        """Validate formula syntax and raise FormulaError if invalid."""
        # Check for balanced parentheses
        if formula.count('(') != formula.count(')'):
            raise FormulaError("Unbalanced parentheses")
        
        # Check for valid characters
        valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+-*/.()^, ')
        if not all(c in valid_chars for c in formula):
            raise FormulaError("Invalid characters in formula")
        
        # Check for dangerous operations
        dangerous_patterns = [
            r'import\s+',
            r'__\w+__',
            r'exec\s*\(',
            r'eval\s*\(',
            r'open\s*\(',
            r'file\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, formula, re.IGNORECASE):
                raise FormulaError("Formula contains potentially dangerous operations")
    
    def _avg(self) -> float:
        """Calculate average of current math channel buffer."""
        buffer = self._data_buffers.get('_current_channel', [])
        if not buffer:
            return 0.0
        return sum(buffer) / len(buffer)
    
    def _min(self) -> float:
        """Calculate minimum of current math channel buffer."""
        buffer = self._data_buffers.get('_current_channel', [])
        if not buffer:
            return 0.0
        return min(buffer)
    
    def _max(self) -> float:
        """Calculate maximum of current math channel buffer."""
        buffer = self._data_buffers.get('_current_channel', [])
        if not buffer:
            return 0.0
        return max(buffer)
    
    def _std(self) -> float:
        """Calculate standard deviation of current math channel buffer."""
        buffer = self._data_buffers.get('_current_channel', [])
        if not buffer or len(buffer) < 2:
            return 0.0
        return np.std(buffer)
    
    def _median(self) -> float:
        """Calculate median of current math channel buffer."""
        buffer = self._data_buffers.get('_current_channel', [])
        if not buffer:
            return 0.0
        return np.median(buffer)
    
    def get_math_channel_config(self, name: str) -> Optional[MathChannelConfig]:
        """Get configuration for a math channel."""
        return self._math_channels.get(name)
    
    def get_all_math_channels(self) -> Dict[str, MathChannelConfig]:
        """Get all math channel configurations."""
        return self._math_channels.copy()
    
    def clear_data_buffers(self) -> None:
        """Clear all data buffers."""
        for buffer in self._data_buffers.values():
            buffer.clear()
    
    def get_supported_functions(self) -> List[str]:
        """Get list of supported function names."""
        return list(self._functions.keys())
    
    def get_formula_examples(self) -> Dict[str, str]:
        """Get example formulas for common calculations."""
        return {
            "Power": "A * B",
            "Sum": "A + B", 
            "Difference": "A - B",
            "Ratio": "A / B",
            "Square Root": "sqrt(A)",
            "Absolute Value": "abs(A)",
            "Sine": "sin(A)",
            "Cosine": "cos(A)",
            "Exponential": "exp(A)",
            "Natural Log": "ln(A)",
            "Power": "A ** 2",
            "Average": "avg(A)",
            "Standard Deviation": "std(A)",
        }

