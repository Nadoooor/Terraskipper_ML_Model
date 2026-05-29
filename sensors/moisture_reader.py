"""Moisture sensor ADC/I2C interface."""

import time
from typing import Optional


class MoistureSensor:
    """Abstract moisture sensor interface (0.0-1.0 volumetric water content)."""
    
    def __init__(self, pin: int = None, i2c_address: int = None):
        self.pin = pin
        self.i2c_address = i2c_address
    
    def read(self) -> Optional[float]:
        """Read moisture value; return 0.0-1.0 or None on error."""
        try:
            time.sleep(0.1)
            return 0.5
        except Exception as e:
            print(f"Moisture read error: {e}")
            return None
