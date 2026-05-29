from pydantic import BaseModel
from typing import List, Dict, Optional


class SoilInput(BaseModel):
    moisture: float
    salinity: float
    temperature: float
    ph: float
    lat: float = 0.0
    lon: float = 0.0


class EnhancedRequest(BaseModel):
    soil: SoilInput
    crops: List[str]


class ScanRequest(BaseModel):
    readings: List[SoilInput]
    allocations: Dict[str, float]
