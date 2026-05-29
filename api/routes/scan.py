from ai.scorer import CropScorer, SoilReading
from ai.scan_mode import ScanModeEngine
from api.schemas import ScanRequest


async def handle_scan(req: ScanRequest, engine: ScanModeEngine):
    """Handle scan mode request."""
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
