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
    if mesh:
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
                    ply_local_idx = 0
                    for w_idx, web in enumerate(mesh.webs.values()):
                        if ply_idx < cumulative + len(web.plies):
                            web_idx = w_idx
                            ply_local_idx = ply_idx - cumulative
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
    return mesh_obj