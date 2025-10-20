"""Input/Output utilities."""

from CGAL.CGAL_Kernel import Point_2
from scipy.interpolate import PchipInterpolator
import numpy as np
import math


def load_airfoil(filename, n_elem=None):
    """Load airfoil points from file, optionally resample to n_elem using PCHIP on arc length."""
    points = []
    with open(filename, "r") as f:
        lines = f.readlines()
        for line in lines[1:]:  # Skip header
            parts = line.strip().split()
            if len(parts) == 2:
                x = float(parts[0])
                y = float(parts[1])
                points.append(Point_2(x, y))
    if n_elem and len(points) != n_elem:
        # Compute arc length parametric t
        x_orig = [p.x() for p in points]
        y_orig = [p.y() for p in points]
        dists = [0.0]
        for i in range(1, len(points)):
            dx = x_orig[i] - x_orig[i - 1]
            dy = y_orig[i] - y_orig[i - 1]
            dist = math.sqrt(dx**2 + dy**2)
            dists.append(dists[-1] + dist)
        total_length = dists[-1]
        # Interpolate x and y over arc length
        pchip_x = PchipInterpolator(dists, x_orig)
        pchip_y = PchipInterpolator(dists, y_orig)
        t_new = np.linspace(0, total_length, n_elem)
        x_new = pchip_x(t_new)
        y_new = pchip_y(t_new)
        points = [Point_2(xn, yn) for xn, yn in zip(x_new, y_new)]
    return points
