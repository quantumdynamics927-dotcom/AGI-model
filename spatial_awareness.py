"""Spatial Awareness module

Map latent consciousness vectors to a 2D occupancy grid, plan paths using
an A* implementation, and apply a simple phi-based smoothing to produce
biomimetically-inspired trajectories.
"""
from typing import List, Tuple
import numpy as np


def latent_to_2d(latent: np.ndarray) -> np.ndarray:
    """Project latent vectors (n, d) to 2D using centered SVD (PCA).

    Returns array shape (n,2).
    """
    X = np.asarray(latent, dtype=float)
    X = X - X.mean(axis=0, keepdims=True)
    # small n,d safe SVD
    u, s, vt = np.linalg.svd(X, full_matrices=False)
    coords = X.dot(vt.T[:, :2])
    return coords


def coords_to_grid(coords: np.ndarray, grid_size: int = 128, padding: int = 2) -> np.ndarray:
    """Rasterize 2D coords to an occupancy grid (0 free, 1 occupied).

    Points project to grid cells; dense areas become obstacles.
    """
    assert coords.ndim == 2 and coords.shape[1] == 2
    coords = np.asarray(coords)
    mins = coords.min(axis=0)
    maxs = coords.max(axis=0)
    span = maxs - mins
    # avoid zero span
    span[span == 0] = 1.0
    # normalize to [0, 1]
    norm = (coords - mins) / span
    idx = np.floor(norm * (grid_size - 1)).astype(int)

    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for x, y in idx:
        x0 = max(0, x - padding)
        x1 = min(grid_size - 1, x + padding)
        y0 = max(0, y - padding)
        y1 = min(grid_size - 1, y + padding)
        grid[y0:y1 + 1, x0:x1 + 1] = 1

    return grid


def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    return float((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def a_star(grid: np.ndarray, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Simple A* pathfinder on 8-connected grid. Returns list of (x,y).
    If no path found returns empty list.
    """
    import heapq

    h, w = grid.shape
    sx, sy = start
    gx, gy = goal
    if not (0 <= sx < w and 0 <= sy < h and 0 <= gx < w and 0 <= gy < h):
        return []
    if grid[sy, sx] != 0 or grid[gy, gx] != 0:
        # start or goal blocked
        return []

    neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    open_set = []
    heapq.heappush(open_set, (0 + heuristic(start, goal), 0, start, None))
    came_from = {}
    gscore = {start: 0}

    while open_set:
        _, cost, current, parent = heapq.heappop(open_set)
        if current in came_from:
            continue
        came_from[current] = parent
        if current == goal:
            # reconstruct
            path = []
            node = current
            while node is not None:
                path.append(node)
                node = came_from[node]
            return list(reversed(path))

        cx, cy = current
        for dx, dy in neighbors:
            nx, ny = cx + dx, cy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if grid[ny, nx] != 0:
                continue
            tentative = gscore[current] + heuristic(current, (nx, ny))
            if tentative < gscore.get((nx, ny), float('inf')):
                gscore[(nx, ny)] = tentative
                priority = tentative + heuristic((nx, ny), goal)
                heapq.heappush(open_set, (priority, tentative, (nx, ny), current))

    return []


def smooth_path(path: List[Tuple[int, int]], window: int = 3) -> List[Tuple[float, float]]:
    """Simple moving-average smoothing; returns float coordinates."""
    if not path:
        return []
    pts = np.array(path, dtype=float)
    k = max(1, window)
    sm = np.copy(pts)
    for i in range(len(pts)):
        lo = max(0, i - k)
        hi = min(len(pts), i + k + 1)
        sm[i] = pts[lo:hi].mean(axis=0)
    return [tuple(p) for p in sm]


def apply_phi_harmonics(path: List[Tuple[float, float]], phi: float = 1.6180339887, strength: float = 0.2) -> List[Tuple[float, float]]:
    """Nudge points toward a loose logarithmic spiral about centroid using phi.
    This is a light aesthetic transform to bias the path with golden-ratio geometry.
    """
    if not path:
        return []
    pts = np.array(path, dtype=float)
    center = pts.mean(axis=0)
    rel = pts - center
    # convert to polar
    xs, ys = rel[:, 0], rel[:, 1]
    radii = np.sqrt(xs * xs + ys * ys)
    thetas = np.arctan2(ys, xs)

    n = len(pts)
    # target spiral: r ~ a * phi^(k/n) where k is index
    a = radii.mean() + 1e-6
    targets = a * (phi ** (np.linspace(0, 1, n)))

    new_r = radii * (1 - strength) + targets * strength
    # small rotation proportional to index
    new_theta = thetas + 0.1 * np.linspace(0, 1, n) * strength

    new_x = new_r * np.cos(new_theta) + center[0]
    new_y = new_r * np.sin(new_theta) + center[1]
    out = np.stack([new_x, new_y], axis=1)
    return [tuple(p) for p in out]


def map_latent_space_and_plan(latent: np.ndarray, start_i: int, goal_i: int, grid_size: int = 128) -> Tuple[np.ndarray, List[Tuple[int, int]], List[Tuple[float, float]]]:
    """Convenience: map latent to grid, run A*, and return (grid, raw_path, smoothed_phi_path).
    start_i and goal_i are indices into the latent array used to seed start/goal.
    """
    coords = latent_to_2d(latent)
    grid = coords_to_grid(coords, grid_size=grid_size)

    # convert start/goal coords to grid indices
    mins = coords.min(axis=0)
    maxs = coords.max(axis=0)
    span = maxs - mins
    span[span == 0] = 1.0
    norm = (coords - mins) / span
    idx = np.floor(norm * (grid_size - 1)).astype(int)

    start = tuple(idx[start_i][::-1])  # (row,col) -> (x,y)
    goal = tuple(idx[goal_i][::-1])

    raw = a_star(grid, start, goal)
    sm = smooth_path(raw, window=3)
    phi_sm = apply_phi_harmonics(sm, strength=0.25)

    return grid, raw, phi_sm
