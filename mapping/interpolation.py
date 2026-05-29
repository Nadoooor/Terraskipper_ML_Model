"""IDW spatial interpolation utilities."""

import numpy as np


def inverse_distance_weighting(
    points: np.ndarray,
    values: np.ndarray,
    grid_points: np.ndarray,
    k: int = 6,
    power: float = 2.0
) -> np.ndarray:
    """
    Perform IDW interpolation.
    
    Args:
        points: (N, 2) array of data locations [lat, lon]
        values: (N,) array of values at those points
        grid_points: (M, 2) array of grid locations
        k: number of nearest neighbors
        power: power parameter for IDW
    
    Returns:
        (M,) array of interpolated values
    """
    from scipy.spatial import cKDTree
    
    tree = cKDTree(points)
    dists, idxs = tree.query(grid_points, k=min(k, len(points)))
    
    weights = 1.0 / np.where(dists == 0, 1e-10, dists) ** power
    weights /= weights.sum(axis=1, keepdims=True)
    
    interpolated = (weights * values[idxs]).sum(axis=1)
    return interpolated
