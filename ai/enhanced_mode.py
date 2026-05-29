from .scorer import CropScorer, SoilReading
from typing import List


def _get_known_crops(scorer):
    """Return a set of known crop names (case-insensitive) from scorer.
    Works with both CropScorer (crops) and TFLiteScorer (crops_df).
    """
    if hasattr(scorer, 'crops'):
        df = scorer.crops
    elif hasattr(scorer, 'crops_df'):
        df = scorer.crops_df
    else:
        return set()
    return set(df['crop'].str.lower())


def run_enhanced_mode(scorer: CropScorer, reading: SoilReading,
                      user_crops: List[str]) -> dict:
    """
    Rank ONLY the user-supplied crop list.
    Raises a warning if any crop name is unrecognised.
    """
    known = _get_known_crops(scorer)
    unrecognised = [c for c in user_crops if c.lower() not in known]
    if unrecognised:
        print(f"[WARNING] Unrecognised crops: {unrecognised}")

    rankings = scorer.score_all(reading, crop_filter=user_crops)
    return {
        'mode': 'enhanced',
        'user_crop_list': user_crops,
        'recommendations': rankings
    }
