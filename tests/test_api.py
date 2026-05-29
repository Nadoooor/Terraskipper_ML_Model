import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "MudBot" in response.json()["message"]


def test_normal_mode(client):
    """Test normal mode endpoint."""
    payload = {
        "moisture": 0.65,
        "salinity": 1.5,
        "temperature": 28,
        "ph": 6.5
    }
    response = client.post("/api/normal", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "normal"
    assert len(data["recommendations"]) == 5
    assert data["recommendations"][0]["score"] >= data["recommendations"][-1]["score"]


def test_enhanced_mode(client):
    """Test enhanced mode endpoint."""
    payload = {
        "soil": {
            "moisture": 0.65,
            "salinity": 1.5,
            "temperature": 28,
            "ph": 6.5
        },
        "crops": ["Rice", "Wheat"]
    }
    response = client.post("/api/enhanced", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "enhanced"
    assert len(data["recommendations"]) == 2


def test_scan_mode(client):
    """Test scan mode endpoint."""
    payload = {
        "readings": [
            {"moisture": 0.65, "salinity": 1.5, "temperature": 28, "ph": 6.5, "lat": 31.0, "lon": 31.0},
            {"moisture": 0.55, "salinity": 2.0, "temperature": 26, "ph": 6.3, "lat": 31.001, "lon": 31.001},
        ],
        "allocations": {"Rice": 0.6, "Wheat": 0.4}
    }
    response = client.post("/api/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "scan"
    assert data["total_cells"] > 0
    assert "zone_summary" in data
