from ai.scorer import CropScorer, SoilReading
from ai.normal_mode import run_normal_mode
from api.schemas import SoilInput


async def handle_normal(soil: SoilInput, scorer: CropScorer):
    """Handle normal mode request."""
    reading = SoilReading(**soil.dict())
    return run_normal_mode(scorer, reading, top_n=5)
