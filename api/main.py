from fastapi import FastAPI
from ai.scorer import CropScorer, SoilReading
from ai.normal_mode import run_normal_mode
from ai.enhanced_mode import run_enhanced_mode
from ai.scan_mode import ScanModeEngine
from api.schemas import SoilInput, EnhancedRequest, ScanRequest


app = FastAPI(title="MudBot Agri-AI API", version="1.0")
scorer = CropScorer("config/crop_database.csv")
engine = ScanModeEngine(scorer)


@app.get("/")
def root():
    return {"message": "MudBot Agri-AI API v1.0"}


@app.post("/api/normal")
def normal(soil: SoilInput):
    reading = SoilReading(**soil.dict())
    return run_normal_mode(scorer, reading, top_n=5)


@app.post("/api/enhanced")
def enhanced(req: EnhancedRequest):
    reading = SoilReading(**req.soil.dict())
    return run_enhanced_mode(scorer, reading, req.crops)


@app.post("/api/scan")
def scan(req: ScanRequest):
    readings = [SoilReading(**r.dict()) for r in req.readings]
    _, _, lat_mesh, lon_mesh, surfaces = engine.interpolate_surface(readings)
    zone_df = engine.allocate_zones(lat_mesh, lon_mesh, surfaces,
                                    req.allocations)
    return {
        'mode': 'scan',
        'total_cells': len(zone_df),
        'zone_summary': zone_df.groupby('assigned_crop')['score']
                                .mean().round(1).to_dict(),
        'zones': zone_df[zone_df['assigned_crop'] != ''].to_dict(orient='records')
    }
