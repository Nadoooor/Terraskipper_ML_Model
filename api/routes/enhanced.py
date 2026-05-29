from ai.scorer import CropScorer, SoilReading
from ai.enhanced_mode import run_enhanced_mode
from api.schemas import EnhancedRequest


async def handle_enhanced(req: EnhancedRequest, scorer: CropScorer):
    """Handle enhanced mode request."""
    reading = SoilReading(**req.soil.dict())
    return run_enhanced_mode(scorer, reading, req.crops)
