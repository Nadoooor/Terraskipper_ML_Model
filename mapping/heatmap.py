import folium
from folium.plugins import HeatMap
import numpy as np
from typing import Dict


CROP_COLORS = {
    'Rice': '#1a78c2',        'Watermelon': '#e83e3e',
    'Tomato': '#e8613e',      'Cotton': '#f0c040',
    'Maize': '#f0a030',       'Wheat': '#c8b06a',
    'Lemon': '#e0e040',       'Sorghum': '#c06020',
    'Barley': '#d0b888',      'Sugarcane': '#40b860',
    'Default': '#888888'
}


def generate_suitability_heatmap(
    surfaces: Dict[str, np.ndarray],
    lat_mesh: np.ndarray,
    lon_mesh: np.ndarray,
    crop_name: str,
    output_path: str = 'suitability_map.html'
) -> folium.Map:
    """Render a single-crop suitability heatmap as a Folium map."""
    surface = surfaces[crop_name]
    center  = [lat_mesh.mean(), lon_mesh.mean()]
    fmap    = folium.Map(location=center, zoom_start=14,
                         tiles='CartoDB positron')

    heat_data = [
        [lat_mesh.ravel()[i], lon_mesh.ravel()[i], float(surface.ravel()[i])]
        for i in range(surface.size)
        if surface.ravel()[i] > 10
    ]
    HeatMap(heat_data, radius=15, blur=10, max_zoom=18,
            gradient={0.2: 'blue', 0.5: 'lime', 0.8: 'yellow', 1.0: 'red'}
            ).add_to(fmap)

    folium.LayerControl().add_to(fmap)
    fmap.save(output_path)
    return fmap
