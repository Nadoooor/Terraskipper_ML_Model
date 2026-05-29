from .scorer import CropScorer, SoilReading
from typing import List


def run_enhanced_mode(scorer: CropScorer, reading: SoilReading,
                      user_crops: List[str]) -> dict:
    """
    Rank ONLY the user-supplied crop list.
    Raises a warning if any crop name is unrecognised.
    """
    known = set(scorer.crops['crop'].str.lower())
    unrecognised = [c for c in user_crops if c.lower() not in known]
    if unrecognised:
        print(f"[WARNING] Unrecognised crops: {unrecognised}")

    rankings = scorer.score_all(reading, crop_filter=user_crops)
    return {
        'mode': 'enhanced',
        'user_crop_list': user_crops,
        'recommendations': rankings
    }
