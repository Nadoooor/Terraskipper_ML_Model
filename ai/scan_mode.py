import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from typing import List, Dict, Tuple
from .scorer import CropScorer, SoilReading


class ScanModeEngine:
    def __init__(self, scorer: CropScorer):
        self.scorer = scorer

    def interpolate_surface(
        self,
        readings: List[SoilReading],
        grid_resolution: int = 100,
        power: float = 2.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, np.ndarray]]:
        """
        IDW interpolation over a regular grid.
        Returns (lat_grid, lon_grid, lat_mesh, lon_mesh, crop_score_surfaces dict).
        """
        lats = np.array([r.lat for r in readings])
        lons = np.array([r.lon for r in readings])

        lat_grid = np.linspace(lats.min(), lats.max(), grid_resolution)
        lon_grid = np.linspace(lons.min(), lons.max(), grid_resolution)
        lat_mesh, lon_mesh = np.meshgrid(lat_grid, lon_grid)

        points    = np.stack([lats, lons], axis=1)
        grid_pts  = np.stack([lat_mesh.ravel(), lon_mesh.ravel()], axis=1)
        tree      = cKDTree(points)

        all_scores = {}
        for reading in readings:
            for item in self.scorer.score_all(reading):
                name = item['crop']
                all_scores.setdefault(name, []).append(item['score'])

        surfaces = {}
        dists, idxs = tree.query(grid_pts, k=min(6, len(readings)))
        weights = 1.0 / np.where(dists == 0, 1e-10, dists) ** power
        weights /= weights.sum(axis=1, keepdims=True)

        for crop_name, scores in all_scores.items():
            score_arr    = np.array(scores)
            interp_flat  = (weights * score_arr[idxs]).sum(axis=1)
            surfaces[crop_name] = interp_flat.reshape(
                grid_resolution, grid_resolution)

        return lat_grid, lon_grid, lat_mesh, lon_mesh, surfaces

    def allocate_zones(
        self,
        lat_mesh: np.ndarray,
        lon_mesh: np.ndarray,
        surfaces: Dict[str, np.ndarray],
        allocations: Dict[str, float]
    ) -> pd.DataFrame:
        """
        Greedy zone allocation: assign cells to crops by best score,
        respecting land allocation percentages.
        """
        requested = list(allocations.keys())
        total_cells = lat_mesh.size

        score_stack = np.stack(
            [surfaces[c].ravel() for c in requested], axis=0)

        best_crop_idx = np.argmax(score_stack, axis=0)
        best_score    = score_stack[best_crop_idx, np.arange(total_cells)]

        order = np.argsort(-best_score)

        cell_lats = lat_mesh.ravel()
        cell_lons = lon_mesh.ravel()

        quotas = {c: int(alloc * total_cells)
                  for c, alloc in allocations.items()}
        assigned_crop  = [''] * total_cells
        assigned_score = [0.0] * total_cells

        for cell_idx in order:
            crop_name = requested[best_crop_idx[cell_idx]]
            if quotas.get(crop_name, 0) > 0:
                assigned_crop[cell_idx]  = crop_name
                assigned_score[cell_idx] = best_score[cell_idx]
                quotas[crop_name] -= 1

        return pd.DataFrame({
            'lat':          cell_lats,
            'lon':          cell_lons,
            'assigned_crop': assigned_crop,
            'score':        assigned_score
        })
