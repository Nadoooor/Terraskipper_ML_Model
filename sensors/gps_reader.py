"""GPS NMEA parsing interface."""

import re
from typing import Tuple, Optional


def parse_nmea_gprmc(sentence: str) -> Optional[Tuple[float, float]]:
    """
    Parse NMEA GPRMC sentence and return (latitude, longitude).
    Format: $GPRMC,time,status,lat,lat_dir,lon,lon_dir,...
    """
    try:
        parts = sentence.split(',')
        if parts[0] != '$GPRMC' or parts[2] != 'A':
            return None
        
        lat_str = parts[3]
        lat_dir = parts[4]
        lon_str = parts[5]
        lon_dir = parts[6]
        
        lat = _dms_to_decimal(lat_str, lat_dir)
        lon = _dms_to_decimal(lon_str, lon_dir)
        
        return (lat, lon)
    except (IndexError, ValueError):
        return None


def _dms_to_decimal(dms: str, direction: str) -> float:
    """Convert degrees-minutes-seconds to decimal."""
    d = int(dms[:2])
    m = float(dms[2:])
    decimal = d + m / 60.0
    return decimal if direction in ['N', 'E'] else -decimal
