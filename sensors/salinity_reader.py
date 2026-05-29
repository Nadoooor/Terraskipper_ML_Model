"""Salinity (EC) sensor interface."""

import time
from typing import Optional


class SalinitySensor:
    """Abstract EC sensor interface (dS/m)."""
    
    def __init__(self, pin: int = None, i2c_address: int = None):
        self.pin = pin
        self.i2c_address = i2c_address
    
    def read(self) -> Optional[float]:
        """Read salinity/EC value (dS/m) or None on error."""
        try:
            time.sleep(0.1)
            return 1.5
        except Exception as e:
            print(f"Salinity read error: {e}")
            return None
