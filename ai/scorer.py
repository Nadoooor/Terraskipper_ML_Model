import numpy as np
import pandas as pd
from typing import Dict, List, Optional


class SoilReading:
    """Encapsulates a single sensor snapshot from the robot."""
    def __init__(self, moisture: float, salinity: float,
                 temperature: float, ph: float,
                 lat: float = 0.0, lon: float = 0.0):
        self.moisture    = moisture
        self.salinity    = salinity
        self.temperature = temperature
        self.ph          = ph
        self.lat         = lat
        self.lon         = lon


class CropScorer:
    """
    Calculates a 0–100 suitability score for each crop given soil conditions.
    Uses a weighted multi-parameter Gaussian + tolerance model.
    """

    def __init__(self, crop_db_path: str):
        self.crops = pd.read_csv(crop_db_path)

    def _range_score(self, value: float, vmin: float,
                     vopt: float, vmax: float) -> float:
        """
        Trapezoid-Gaussian hybrid:
        - Returns 1.0 inside [vopt ± 10% range]
        - Decays as Gaussian outside that window toward vmin/vmax
        - Returns 0.0 outside [vmin, vmax]
        """
        if value < vmin or value > vmax:
            return 0.0
        if vmin <= value <= vmax:
            half = (vmax - vmin) / 2.0
            dist = abs(value - vopt) / half
            return float(np.exp(-2.0 * dist ** 2))
        return 0.0

    def _salinity_score(self, salinity: float, sal_max: float) -> float:
        """
        Salinity tolerance: linear decay from 0 dS/m (perfect) to sal_max (zero).
        """
        if salinity <= 0:
            return 1.0
        if salinity >= sal_max:
            return 0.0
        return 1.0 - (salinity / sal_max)

    def score_crop(self, crop: pd.Series, reading: SoilReading) -> float:
        """Return a 0–100 suitability score for one crop against one reading."""
        m_score  = self._range_score(
            reading.moisture, crop['moisture_min'],
            crop['moisture_opt'], crop['moisture_max'])

        s_score  = self._salinity_score(
            reading.salinity, crop['salinity_max_dsm'])

        t_score  = self._range_score(
            reading.temperature, crop['temp_min_c'],
            crop['temp_opt_c'], crop['temp_max_c'])

        ph_score = self._range_score(
            reading.ph, crop['ph_min'],
            crop['ph_opt'], crop['ph_max'])

        weighted = (
            crop['weight_moisture']  * m_score  +
            crop['weight_salinity']  * s_score  +
            crop['weight_temp']      * t_score  +
            crop['weight_ph']        * ph_score
        )
        return round(weighted * 100, 1)

    def score_all(self, reading: SoilReading,
                  crop_filter: Optional[List[str]] = None) -> List[Dict]:
        """
        Score all crops (or a filtered subset) against a reading.
        Returns a ranked list of {crop, score, breakdown}.
        """
        df = self.crops
        if crop_filter:
            df = df[df['crop'].str.lower().isin(
                [c.lower() for c in crop_filter])]

        results = []
        for _, crop in df.iterrows():
            score = self.score_crop(crop, reading)
            results.append({
                'crop':  crop['crop'],
                'score': score,
                'breakdown': {
                    'moisture':    round(self._range_score(
                        reading.moisture, crop['moisture_min'],
                        crop['moisture_opt'], crop['moisture_max']) * 100, 1),
                    'salinity':    round(self._salinity_score(
                        reading.salinity, crop['salinity_max_dsm']) * 100, 1),
                    'temperature': round(self._range_score(
                        reading.temperature, crop['temp_min_c'],
                        crop['temp_opt_c'], crop['temp_max_c']) * 100, 1),
                    'ph':          round(self._range_score(
                        reading.ph, crop['ph_min'],
                        crop['ph_opt'], crop['ph_max']) * 100, 1),
                },
                'notes': crop['notes']
            })

        return sorted(results, key=lambda x: x['score'], reverse=True)
