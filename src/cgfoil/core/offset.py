"""Offset airfoil functionality."""

import math
from CGAL.CGAL_Kernel import Point_2


def offset_airfoil(points, distances, normal_ref=None):
    """Offset the airfoil by distances along normals (inward), aligned with normal_ref if provided."""
    if isinstance(distances, (int, float)):
        distances = [distances] * len(points)
    n = len(points)
    offset_points = []
    for i in range(n):
        prev = points[(i - 1) % n]
        curr = points[i]
        next_p = points[(i + 1) % n]
        # Tangent vector
        tx = (next_p.x() - prev.x()) / 2
        ty = (next_p.y() - prev.y()) / 2
        # Normalize tangent
        t_len = math.sqrt(tx**2 + ty**2)
        if t_len > 0:
            tx /= t_len
            ty /= t_len
        # Natural normal (outward)
        natural_nx = -ty
        natural_ny = tx
        # Adjust based on normal_ref
        if normal_ref:
            dot = natural_nx * normal_ref[0] + natural_ny * normal_ref[1]
            if dot < 0:
                natural_nx = -natural_nx
                natural_ny = -natural_ny
        nx, ny = natural_nx, natural_ny
        # Offset inward
        ox = curr.x() + distances[i] * nx
        oy = curr.y() + distances[i] * ny
        offset_points.append(Point_2(ox, oy))
    return offset_points
