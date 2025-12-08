"""Input/Output utilities."""

from CGAL.CGAL_Kernel import Point_2
from scipy.interpolate import PchipInterpolator
import numpy as np
import math
from cgfoil.utils.logger import logger


def load_airfoil(airfoil_input, n_elem=None):
    """Load airfoil points from various inputs, optionally resample to n_elem
    using PCHIP on arc length."""
    if isinstance(airfoil_input, str):
        if airfoil_input.endswith(".vtk"):
            import pyvista as pv

            mesh = pv.read(airfoil_input)
            points_2d = mesh.points[:, :2].tolist()
            points = [Point_2(x, y) for x, y in points_2d]
        else:
            points = []
            with open(airfoil_input, "r") as f:
                lines = f.readlines()
                for line in lines[1:]:  # Skip header
                    parts = line.strip().split()
                    if len(parts) == 2:
                        x = float(parts[0])
                        y = float(parts[1])
                        points.append(Point_2(x, y))
    else:
        # Assume list or ndarray
        if isinstance(airfoil_input, np.ndarray):
            points_2d = airfoil_input.tolist()
        else:
            points_2d = airfoil_input
        points = [Point_2(x, y) for x, y in points_2d]

    if n_elem and len(points) != n_elem:
        return _resample_points(points, n_elem)
    return points


def _resample_points(points, n_elem):
    """Resample points to n_elem using PCHIP on arc length."""
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
    return [Point_2(xn, yn) for xn, yn in zip(x_new, y_new)]


def save_mesh_to_vtk(mesh_result, mesh, vtk_file):
    """Save mesh result to VTK file."""
    from cgfoil.core.vtk import build_vtk_mesh
    mesh_obj = build_vtk_mesh(mesh_result, mesh)
    mesh_obj.save(vtk_file)
    logger.info(f"Mesh saved to {vtk_file}")