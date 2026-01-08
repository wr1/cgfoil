"""VTK mesh building utilities."""

import math


def build_vtk_mesh(mesh_result, mesh=None):
    """Build a PyVista UnstructuredGrid from mesh_result and optional mesh."""
    try:
        import pyvista as pv
        import numpy as np
    except ImportError:
        raise ImportError("pyvista not available")
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
    plane_orientations = []
    for ix, iy in mesh_result.face_inplanes:
        angle = math.degrees(math.atan2(iy, ix))
        angle = (angle + 90) % 180 - 90
        plane_orientations.append(angle)
    mesh_obj.cell_data["plane_orientations"] = plane_orientations
    # Add offset normals (inward for skins)
    mesh_obj.cell_data["offset_normals"] = np.array(
        [[-n[0], -n[1], 0.0] for n in mesh_result.face_normals]
    )
    # Compute cell sizes using pyvista
    mesh_obj.compute_cell_sizes()
    return mesh_obj
