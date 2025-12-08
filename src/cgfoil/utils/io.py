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
    try:
        import pyvista as pv
        import numpy as np
    except ImportError:
        logger.warning("pyvista not available, cannot save VTK")
        return
    mesh_obj = pv.UnstructuredGrid(
        np.array(mesh_result.faces).flatten(),
        [pv.CellType.TRIANGLE] * len(mesh_result.faces),
        mesh_result.vertices,
    )
    mesh_obj.cell_data["material_id"] = mesh_result.face_material_ids
    mesh_obj.cell_data["normals"] = np.array(
        [[n[0], n[1], 0.0] for n in mesh_result.face_normals]
    )
    mesh_obj.cell_data["inplane"] = np.array(
        [[i[0], i[1], 0.0] for i in mesh_result.face_inplanes]
    )
    plane_orientations = [
        math.degrees(math.atan2(iy, ix)) for ix, iy in mesh_result.face_inplanes
    ]
    mesh_obj.cell_data["plane_orientations"] = plane_orientations
    # Add offset normals (inward for skins)
    mesh_obj.cell_data["offset_normals"] = np.array(
        [[-n[0], -n[1], 0.0] for n in mesh_result.face_normals]
    )
    # Add ply thicknesses
    for ply_idx in range(len(mesh_result.skin_ply_thicknesses)):
        thicknesses = []
        for idx, mat_id in enumerate(mesh_result.face_material_ids):
            if (
                mat_id in mesh_result.skin_material_ids
                and mesh_result.skin_material_ids.index(mat_id) == ply_idx
            ):
                # Find closest outer point
                _, v0, v1, v2 = mesh_result.faces[idx]
                p0 = mesh_result.vertices[v0][:2]
                p1 = mesh_result.vertices[v1][:2]
                p2 = mesh_result.vertices[v2][:2]
                cx = (p0[0] + p1[0] + p2[0]) / 3.0
                cy = (p0[1] + p1[1] + p2[1]) / 3.0
                closest_i = min(
                    range(len(mesh_result.outer_points)),
                    key=lambda j: (mesh_result.outer_points[j][0] - cx) ** 2
                    + (mesh_result.outer_points[j][1] - cy) ** 2,
                )
                thicknesses.append(mesh_result.skin_ply_thicknesses[ply_idx][closest_i])
            else:
                thicknesses.append(0.0)
        mesh_obj.cell_data[f"ply_{ply_idx}_thickness"] = thicknesses
    for ply_idx in range(len(mesh_result.web_ply_thicknesses)):
        thicknesses = []
        for idx, mat_id in enumerate(mesh_result.face_material_ids):
            if mat_id == mesh_result.web_material_ids[ply_idx]:
                # Find closest on the untrimmed_line for that web
                cumulative = 0
                web_idx = 0
                for w_idx, web in enumerate(mesh.webs.values()):
                    if ply_idx < cumulative + len(web.plies):
                        web_idx = w_idx
                        ply_idx - cumulative
                        break
                    cumulative += len(web.plies)
                untrimmed = mesh_result.untrimmed_lines[web_idx]
                _, v0, v1, v2 = mesh_result.faces[idx]
                p0 = mesh_result.vertices[v0][:2]
                p1 = mesh_result.vertices[v1][:2]
                p2 = mesh_result.vertices[v2][:2]
                cx = (p0[0] + p1[0] + p2[0]) / 3.0
                cy = (p0[1] + p1[1] + p2[1]) / 3.0
                closest_i = min(
                    range(len(untrimmed)),
                    key=lambda j: (untrimmed[j][0] - cx) ** 2
                    + (untrimmed[j][1] - cy) ** 2,
                )
                thicknesses.append(mesh_result.web_ply_thicknesses[ply_idx][closest_i])
            else:
                thicknesses.append(0.0)
        mesh_obj.cell_data[f"ply_{ply_idx}_thickness"] = thicknesses
    mesh_obj.save(vtk_file)
    logger.info(f"Mesh saved to {vtk_file}")
