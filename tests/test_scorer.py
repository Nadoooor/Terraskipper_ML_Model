import pytest
from ai.scorer import CropScorer, SoilReading


@pytest.fixture
def scorer():
    return CropScorer("config/crop_database.csv")


def test_score_crop(scorer):
    """Test single crop scoring."""
    reading = SoilReading(moisture=0.65, salinity=1.5, 
                          temperature=28, ph=6.5)
    rice = scorer.crops[scorer.crops['crop'] == 'Rice'].iloc[0]
    score = scorer.score_crop(rice, reading)
    assert 0 <= score <= 100
    assert score > 50


def test_score_all(scorer):
    """Test scoring all crops."""
    reading = SoilReading(moisture=0.65, salinity=1.5,
                          temperature=28, ph=6.5)
    results = scorer.score_all(reading)
    assert len(results) == 20
    assert all(0 <= r['score'] <= 100 for r in results)
    assert results[0]['score'] >= results[-1]['score']


def test_range_score():
    """Test Gaussian range scoring."""
    scorer = CropScorer("config/crop_database.csv")
    
    score_at_opt = scorer._range_score(25, 20, 25, 30)
    assert score_at_opt == pytest.approx(1.0, abs=0.01)
    
    score_outside = scorer._range_score(40, 20, 25, 30)
    assert score_outside == 0.0


def test_salinity_score():
    """Test salinity scoring."""
    scorer = CropScorer("config/crop_database.csv")
    
    score_zero = scorer._salinity_score(0, 2.0)
    assert score_zero == pytest.approx(1.0)
    
    score_half = scorer._salinity_score(1.0, 2.0)
    assert score_half == pytest.approx(0.5)
    
    score_max = scorer._salinity_score(2.0, 2.0)
    assert score_max == pytest.approx(0.0)
