import folium
import pandas as pd
from typing import Dict


CROP_COLORS = {
    'Rice': '#1a78c2',        'Watermelon': '#e83e3e',
    'Tomato': '#e8613e',      'Cotton': '#f0c040',
    'Maize': '#f0a030',       'Wheat': '#c8b06a',
    'Lemon': '#e0e040',       'Sorghum': '#c06020',
    'Barley': '#d0b888',      'Sugarcane': '#40b860',
    'Default': '#888888'
}


def generate_zone_map(
    zone_df: pd.DataFrame,
    output_path: str = 'zone_map.html'
) -> folium.Map:
    """Render the Scan Mode zone allocation as a color-coded Folium map."""
    center = [zone_df['lat'].mean(), zone_df['lon'].mean()]
    fmap   = folium.Map(location=center, zoom_start=14,
                        tiles='CartoDB positron')

    for _, row in zone_df[zone_df['assigned_crop'] != ''].iterrows():
        color = CROP_COLORS.get(row['assigned_crop'],
                                 CROP_COLORS['Default'])
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=4,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=f"{row['assigned_crop']}: {row['score']:.1f}%"
        ).add_to(fmap)

    legend_html = '<div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:10px;border-radius:8px;font-size:12px">'
    crops = zone_df['assigned_crop'].unique()
    for c in crops:
        if c:
            legend_html += f'<span style="color:{CROP_COLORS.get(c, "#888")};font-size:18px">■</span> {c}<br>'
    legend_html += '</div>'
    fmap.get_root().html.add_child(folium.Element(legend_html))

    fmap.save(output_path)
    return fmap
