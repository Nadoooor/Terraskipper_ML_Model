"""Temperature sensor (DS18B20 / thermistor) interface."""

import time
from typing import Optional


class TemperatureSensor:
    """Abstract temperature sensor interface (°C)."""
    
    def __init__(self, pin: int = None, sensor_type: str = "DS18B20"):
        self.pin = pin
        self.sensor_type = sensor_type
    
    def read(self) -> Optional[float]:
        """Read temperature in °C or None on error."""
        try:
            time.sleep(0.1)
            return 25.0
        except Exception as e:
            print(f"Temperature read error: {e}")
            return None
