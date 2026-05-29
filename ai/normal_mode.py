from .scorer import CropScorer, SoilReading


def run_normal_mode(scorer: CropScorer, reading: SoilReading,
                    top_n: int = 5) -> dict:
    """
    Auto-rank ALL crops in the database against current soil conditions.
    Returns the top N recommendations with full explainability breakdown.
    """
    rankings = scorer.score_all(reading)
    return {
        'mode': 'normal',
        'location': {'lat': reading.lat, 'lon': reading.lon},
        'soil_input': {
            'moisture':    reading.moisture,
            'salinity':    reading.salinity,
            'temperature': reading.temperature,
            'ph':          reading.ph
        },
        'recommendations': rankings[:top_n]
    }
