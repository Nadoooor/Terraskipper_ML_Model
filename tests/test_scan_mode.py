import pytest
import numpy as np
from ai.scorer import CropScorer, SoilReading
from ai.scan_mode import ScanModeEngine


@pytest.fixture
def engine():
    scorer = CropScorer("config/crop_database.csv")
    return ScanModeEngine(scorer)


@pytest.fixture
def test_readings():
    """Generate test readings."""
    return [
        SoilReading(0.65, 1.5, 28, 6.5, 31.0, 31.0),
        SoilReading(0.55, 2.0, 26, 6.3, 31.001, 31.001),
        SoilReading(0.75, 1.2, 30, 6.7, 31.002, 31.002),
    ]


def test_interpolate_surface(engine, test_readings):
    """Test IDW surface interpolation."""
    lat_grid, lon_grid, lat_mesh, lon_mesh, surfaces = engine.interpolate_surface(
        test_readings, grid_resolution=50)
    
    assert len(surfaces) == 20
    assert all(isinstance(s, np.ndarray) for s in surfaces.values())
    assert lat_mesh.shape == (50, 50)


def test_allocate_zones(engine, test_readings):
    """Test zone allocation."""
    _, _, lat_mesh, lon_mesh, surfaces = engine.interpolate_surface(
        test_readings, grid_resolution=50)
    
    allocations = {'Rice': 0.6, 'Wheat': 0.4}
    zone_df = engine.allocate_zones(lat_mesh, lon_mesh, surfaces, allocations)
    
    assert len(zone_df) == 2500
    assert set(zone_df.columns) == {'lat', 'lon', 'assigned_crop', 'score'}
    assert zone_df['assigned_crop'].nunique() <= 2
